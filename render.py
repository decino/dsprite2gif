# dsprite2gif - Extracts Doom sprites from WADs into tic-accurate GIF animations
# Copyright (C) 2026 decino
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
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

from omg.lump import Graphic
from PIL import Image

from lut import get_mobj_info
from palette import load_playpal, load_colormap, translate_player_color, apply_fuzz
from doomdata import trace_state_sequence, build_sprite_frame_table

def generate_animations(wad, states, state_name_to_index, mobjinfo_list, scale_factor = 1.0, use_aspect_ratio = True, all_fuzz = False, output_base = "animations"):
    transparent_colour = (0, 0, 0, 0)
    aspect_ratio = 1.2 if use_aspect_ratio else 1.0
    playpal = load_playpal(wad)
    colormap = load_colormap(wad)

    # This is an unfortunate limitation with GIF frames
    # 1/35th of a second is ~28.5 ms, which GIFs round down to 20 ms, resulting in much faster animations
    # We'll manually set it to 30 ms, sprite animations will be sliiightly slower than in-game, but nearly identical either way
    tic_duration_in_ms = 30

    # Fill opacity LUT for masking, 128x255 opaque, 128x0 transparent
    transparency_lut = [255 if alpha < 128 else 0 for alpha in range(256)]
    
    # Decoding a lump is slow, so only do it once per lump
    image_cache = {}

    for mobj in mobjinfo_list:
        mobj_internal_name = mobj['name']

        # Multiplayer Doomguys
        if mobj_internal_name == 'MT_PLAYER':
            variants = [
                ('players', 'PlayerGreen'),
                ('players', 'PlayerIndigo'),
                ('players', 'PlayerRed'),
                ('players', 'PlayerBrown')
            ]

        # Also add turbo variants for Pinkies and Spectres 
        elif mobj_internal_name in ('MT_SERGEANT', 'MT_SHADOWS'):
            category, base_name = get_mobj_info(mobj_internal_name)

            variants = [
                (category, base_name),
                (category, base_name + 'Turbo')
            ]
        else:
            category, readable_folder_name = get_mobj_info(mobj_internal_name)
            variants = [(category, readable_folder_name)]

        is_player = mobj_internal_name == 'MT_PLAYER'
        is_fuzzed_entity = (mobj_internal_name == 'MT_SHADOWS' or all_fuzz)

        for category, readable_folder_name in variants:
            mobj_dir = os.path.join(output_base, category, readable_folder_name)
            
            entity_sequences = {}
            all_entity_frames = []
            
            for state_key, start_label in mobj['states'].items():
                sequence = trace_state_sequence(start_label, states, state_name_to_index)

                # Not animated, go to the next one
                if not sequence:
                    continue

                # Adjust state tics for turbo demons    
                if readable_folder_name.endswith('Turbo') and state_key in ('seestate', 'meleestate', 'painstate'):
                    for state in sequence:
                        if state['tics'] > 0:
                            state['tics'] = max(1, state['tics'] >> 1)
                
                sprite_prefix = sequence[0]['sprite']
                sprite_temp = build_sprite_frame_table(wad, sprite_prefix)
                needs_rotation = False
                
                for state in sequence:
                    frame_index = state['frame_index']

                    if frame_index in sprite_temp and sprite_temp[frame_index]['rotate'] == True:
                        needs_rotation = True
                        break

                # Sprite has 8 rotations, or is a billboard
                available_rots = range(1, 9) if needs_rotation else [1]

                for rotation in available_rots:
                    raw_frames = []
                    rotation_lookup = 0 if not needs_rotation else rotation - 1
                    
                    for state in sequence:
                        frame_index = state['frame_index']
                        lump_object = None
                        is_flipped = False
                        
                        if frame_index in sprite_temp:
                            if needs_rotation:
                                if sprite_temp[frame_index]['lump'][rotation_lookup] != -1:
                                    lump_object = sprite_temp[frame_index]['lump'][rotation_lookup]
                                    is_flipped = sprite_temp[frame_index]['flip'][rotation_lookup]
                            else:
                                for rotation_alt in range(8):
                                    if sprite_temp[frame_index]['lump'][rotation_alt] != -1:
                                        lump_object = sprite_temp[frame_index]['lump'][rotation_alt]
                                        is_flipped = sprite_temp[frame_index]['flip'][rotation_alt]
                                        break
                                        
                        if isinstance(lump_object, Graphic):
                            img = image_cache.get(id(lump_object))

                            if img is None:
                                img = image_cache[id(lump_object)] = lump_object.to_Image(mode = 'RGBA')
                            
                            if is_player:
                                img = translate_player_color(img, readable_folder_name, playpal)

                            if is_flipped:
                                img = img.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
                                
                            tics = state['tics']

                            # Infinite states last 2 seconds
                            if tics == -1:
                                tics = 70

                            # This kind of sucks, but 0-ms GIF frames vary by platform
                            # Some browsers turn 0 ms frames into 100 ms frames, some retain the 0 ms duration
                            # Same applies to image viewers, better safe than sorry
                            elif tics == 0:
                                tics = 1

                            if is_fuzzed_entity:
                                # Force single-frame sprites to have 10 frames to ensure the fuzz
                                effective_tics = max(tics, 10) if tics == 1 else tics
                                
                                for _ in range(effective_tics):
                                    fuzzed_img = apply_fuzz(img, playpal, colormap)
                                    frame_data = {
                                        'img': fuzzed_img,
                                        'width': lump_object.width,
                                        'height': lump_object.height,
                                        'x_offset': lump_object.x_offset,
                                        'y_offset': lump_object.y_offset,
                                        'duration_ms': tic_duration_in_ms
                                    }
                                    raw_frames.append(frame_data)
                                    all_entity_frames.append(frame_data)
                            else:
                                frame_data = {
                                    'img': img,
                                    'width': lump_object.width,
                                    'height': lump_object.height,
                                    'x_offset': lump_object.x_offset,
                                    'y_offset': lump_object.y_offset,
                                    'duration_ms': tics * tic_duration_in_ms
                                }
                                raw_frames.append(frame_data)
                                all_entity_frames.append(frame_data)
                                
                    if raw_frames:
                        if state_key not in entity_sequences:
                            entity_sequences[state_key] = {}

                        entity_sequences[state_key][rotation] = raw_frames

            if not all_entity_frames:
                continue

            # Apply offsets found in the lump
            min_x = min(-f['x_offset'] for f in all_entity_frames)
            max_x = max(-f['x_offset'] + f['width'] for f in all_entity_frames)
            min_y = min(-f['y_offset'] for f in all_entity_frames)
            max_y = max(-f['y_offset'] + f['height'] for f in all_entity_frames)

            canvas_width = max_x - min_x
            canvas_height = max_y - min_y
            origin_x = -min_x
            origin_y = -min_y

            if canvas_width <= 0 or canvas_height <= 0:
                continue

            scaled_w = int(canvas_width * scale_factor)
            scaled_h = int(canvas_height * scale_factor * aspect_ratio)

            for state_key, rotation_dict in entity_sequences.items():
                state_rotation_dir = os.path.join(mobj_dir, state_key)
                os.makedirs(state_rotation_dir, exist_ok = True)
                
                for rotation, raw_frames in rotation_dict.items():
                    canvas_frames = []
                    durations = []
                    
                    for rf in raw_frames:
                        canvas = Image.new('RGBA', (canvas_width, canvas_height), transparent_colour)
                        paste_x = origin_x - rf['x_offset']
                        paste_y = origin_y - rf['y_offset']
                        
                        canvas.paste(rf['img'], (paste_x, paste_y), rf['img'])

                        scaled_canvas = canvas.resize((scaled_w, scaled_h), Image.Resampling.NEAREST) # Lookin' good!
                        canvas_frames.append(scaled_canvas)
                        durations.append(rf['duration_ms'])
                        
                    output_file = os.path.join(state_rotation_dir, f"rotation_{ rotation }.gif")
                    paletted_frames = []

                    for frame in canvas_frames:
                        gif_frame = frame.convert('RGB').convert('P', palette = Image.Palette.ADAPTIVE, colors = 255)
                        trans_mask = frame.getchannel('A').point(transparency_lut) # Apply mask for palette index 255
                        gif_frame.paste(255, mask = trans_mask)
                        paletted_frames.append(gif_frame)

                    paletted_frames[0].save(
                        output_file,
                        save_all = True,
                        append_images = paletted_frames[1:],
                        duration = durations,
                        loop = 0,
                        disposal = 2,
                        transparency = 255
                    )
                    print(f"Generated: { output_file }")
