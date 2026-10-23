# dsprite2gif - Extracts Doom sprites from WADs into tic-accurate GIF animations
# Copyright (C) 2026 decino
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os
import re

from omg.wad import WAD

def load_wads(iwad_path, pwad_paths):
    wads = WAD(iwad_path)

    # Epic overrides, thank you omg
    for pwad_path in pwad_paths:
        pwad = WAD(pwad_path)
        wads = wads + pwad
    return wads

def parse_info_c(info_c_path):
    if not os.path.exists(info_c_path):
        raise FileNotFoundError(f"Could not find info.c at: { info_c_path }")

    with open(info_c_path, 'r', encoding = 'latin-1') as f:
        content = f.read()

    sprite_names = []
    sprite_names_match = re.search(r'const char \*sprite_names\[\]\s*=\s*\{(.*?)\};', content, re.DOTALL)

    if sprite_names_match:
        sprite_names = re.findall(r'"([A-Z0-9]{4})"', sprite_names_match.group(1))

    # 1. {
    # 2. Find SPR_ suffix
    # 3. Frame num
    # 4. Frame duration in tics
    # 5. Action pointer (skipped)
    # 6. Next state
    state_pattern = re.compile(
        r'\{\s*SPR_([A-Z0-9]+)\s*,\s*([^,]+)\s*,\s*(-?\d+)\s*,\s*\{[^}]*\}\s*,\s*([A-Z0-9_]+)',
        re.IGNORECASE
    )
    states = []

    for match in state_pattern.finditer(content):
        spr_suffix = match.group(1).upper()
        frame_raw = match.group(2).strip()
        tics = int(match.group(3))
        next_state_label = match.group(4).strip()
        
        try:
            frame_val = int(frame_raw, 0)
        except ValueError:
            frame_val = 0
            
        states.append({
            'sprite': spr_suffix,
            'frame_raw': frame_val,
            'tics': tics,
            'next_state': next_state_label
        })

    state_name_to_index = {}
    state_index_to_name = {}
    lines = content.splitlines()
    current_index = 0
    
    for line in lines:
        if '{SPR_' in line:
            # Fortunately multigen comments the current state name for each entry
            state_comment = re.search(r'//\s*([A-Z0-9_]+)\s*$', line)

            if state_comment:
                label = state_comment.group(1)
                state_name_to_index[label] = current_index
                state_index_to_name[current_index] = label
            current_index += 1

    mobjinfo_list = []

    # Look up MT_ comments above mobjinfo entries
    mobj_blocks = re.findall(r'\{\s*(?://\s*([A-Z0-9_]+))\s*([^}]*?)\}', content, re.DOTALL)
    
    for name_comment, block in mobj_blocks:
        mobj_name = name_comment if name_comment else "MT_IDUNNO"
        
        def extract_state(field_name):
            for line in block.splitlines():
                if field_name.lower() in line.lower():
                    # 1. S_
                    # 2. State name
                    m = re.search(r'(S_[A-Z0-9_]+|0)', line)

                    if m:
                        val = m.group(1)
                        return val if val != '0' else 'S_NULL'
            return 'S_NULL'

        spawn_label = extract_state('spawnstate')
        see_label = extract_state('seestate')
        melee_label = extract_state('meleestate')
        missile_label = extract_state('missilestate')
        pain_label = extract_state('painstate')
        death_label = extract_state('deathstate')
        xdeath_label = extract_state('xdeathstate')
        raise_label = extract_state('raisestate')
        
		# These states are never called from info.c, so let's just hack them in
        if mobj_name == 'MT_VILE':
            raise_label = 'S_VILE_HEAL1'
        if mobj_name == 'MT_BOSSBRAIN':
            death_label = 'S_BRAINEXPLODE1'
        if mobj_name == 'MT_PLAYER':
            missile_label = 'S_PLAY_ATK2'
            melee_label = 'S_PLAY_ATK1'

        mobjinfo_list.append({
            'name': mobj_name,
            'states': {
                'spawnstate': spawn_label,
                'seestate': see_label,
                'meleestate': melee_label,
                'missilestate': missile_label,
                'painstate': pain_label,
                'deathstate': death_label,
                'xdeathstate': xdeath_label,
                'raisestate': raise_label,
            }
        })

    return sprite_names, states, state_name_to_index, state_index_to_name, mobjinfo_list

def trace_state_sequence(start_label, states, state_name_to_index):

    # Don't bother animating still objects
    if start_label not in state_name_to_index or start_label == 'S_NULL':
        return []
        
    sequence = []
    current_index = state_name_to_index[start_label]
    visited = set()

    while current_index < len(states) and current_index not in visited:
        visited.add(current_index)
        st = states[current_index]
        
        frame_index = st['frame_raw'] & 0x7FFF # Remove fullbright flag

        sequence.append({
            'sprite': st['sprite'],
            'frame_index': frame_index,
            'tics': st['tics']
        })        
        next_label = st['next_state']

        # End of state sequence reached
        if next_label == 'S_NULL' or next_label not in state_name_to_index:
            break
            
        next_index = state_name_to_index[next_label]

        # Loop found, sequence complete
        if next_index in visited:
            break
                    
        current_index = next_index
            
    return sequence

def build_sprite_frame_table(wad, sprite_prefix):
    sprites_section = getattr(wad, 'sprites', {})
    sprite_temp = {}
    
    for lump_name, lump_object in sprites_section.items():
        if not str(lump_name).upper().startswith(sprite_prefix):
            continue
            
        lump_name_string = str(lump_name).upper()

        if len(lump_name_string) < 6:
            continue
            
        try:
            frame_index = ord(lump_name_string[4]) - ord('A')
            rotation_num = int(lump_name_string[5])
        except ValueError:
            continue
            
        if frame_index not in sprite_temp:
            sprite_temp[frame_index] = { 'rotate': None, 'lump': [-1] * 8, 'flip': [False] * 8 }

        # Billboard sprite
        if rotation_num == 0:
            sprite_temp[frame_index]['rotate'] = False

            for r in range(8):
                sprite_temp[frame_index]['lump'][r] = lump_object
                sprite_temp[frame_index]['flip'][r] = False
        else:
            sprite_temp[frame_index]['rotate'] = True
            rotation_index = rotation_num - 1
            sprite_temp[frame_index]['lump'][rotation_index] = lump_object
            sprite_temp[frame_index]['flip'][rotation_index] = False

        # Sprites with mirrored rotations are 8 chars long    
        if len(lump_name_string) >= 8:
            try:
                sec_frame_index = ord(lump_name_string[6]) - ord('A')
                sec_rotation_num = int(lump_name_string[7])

                if sec_frame_index not in sprite_temp:
                    sprite_temp[sec_frame_index] = { 'rotate': None, 'lump': [-1] * 8, 'flip': [False] * 8 }

                if sec_rotation_num > 0:
                    sprite_temp[sec_frame_index]['rotate'] = True
                    sec_rotation_index = sec_rotation_num - 1
                    sprite_temp[sec_frame_index]['lump'][sec_rotation_index] = lump_object
                    sprite_temp[sec_frame_index]['flip'][sec_rotation_index] = True

            except ValueError:
                pass

    return sprite_temp
