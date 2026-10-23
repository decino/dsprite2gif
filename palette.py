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

import random

from PIL import Image

def load_playpal(wad):
    if 'PLAYPAL' not in wad.data:
        raise ValueError("Could not find PLAYPAL lump in WAD.")

    raw_bytes = wad.data['PLAYPAL'].data

    if len(raw_bytes) < 768:
        raise ValueError(f"PLAYPAL lump is too small ({len(raw_bytes)} bytes, expected at least 768).")

    base_palette_bytes = raw_bytes[:768]
    palette = []

    for i in range(0, 768, 3):
        palette.append((
            base_palette_bytes[i],
            base_palette_bytes[i + 1],
            base_palette_bytes[i + 2]
        ))
    return palette

def load_colormap(wad):
    if 'COLORMAP' not in wad.data:
        raise ValueError("Could not find COLORMAP lump in WAD.")

    raw_bytes = wad.data['COLORMAP'].data

    # Only the light levels up to the fuzz one are needed
    if len(raw_bytes) < (FUZZ_COLORMAP + 1) * 256:
        raise ValueError(f"COLORMAP lump is too small ({len(raw_bytes)} bytes, expected at least {(FUZZ_COLORMAP + 1) * 256}).")

    return raw_bytes

def translate_player_color(img, variant_name, playpal):
    if variant_name in ('Player', 'PlayerGreen') or not playpal:
        return img
        
    img = img.convert('RGBA')
    pixels = img.load()
    width, height = img.size

	# PLAYPAL index offsets
    offset = 0
	
    if variant_name == 'PlayerIndigo':
        offset = 16 
    elif variant_name == 'PlayerRed':
        offset = 80   
    elif variant_name == 'PlayerBrown':
        offset = 48
        
    if offset == 0:
        return img

    # Now check the actual PLAYPAL
    translation_map = {}
	
    for index in range(16):
        source_index = 112 + index
        target_index = source_index - offset

        if source_index < len(playpal) and target_index < len(playpal):
            translation_map[playpal[source_index]] = playpal[target_index]

    for y in range(height):
        for x in range(width):
            source_r, source_g, source_b, alpha = pixels[x, y]

            if alpha == 0:
                continue
                
            rgb = (source_r, source_g, source_b)

            if rgb in translation_map:
                target_r, target_g, target_b = translation_map[rgb]
                pixels[x, y] = (target_r, target_g, target_b, alpha)
                
    return img
	
# Fuzz table from DOOM's r_draw.c, Copyright (C) 1993-1996 Id Software, Inc.
FUZZTABLE = 50
FUZZOFF = 320
FUZZOFFSET = [
     FUZZOFF, -FUZZOFF,  FUZZOFF, -FUZZOFF,  FUZZOFF,  FUZZOFF, -FUZZOFF,
     FUZZOFF,  FUZZOFF, -FUZZOFF,  FUZZOFF,  FUZZOFF,  FUZZOFF, -FUZZOFF,
     FUZZOFF,  FUZZOFF,  FUZZOFF, -FUZZOFF, -FUZZOFF, -FUZZOFF, -FUZZOFF,
     FUZZOFF, -FUZZOFF, -FUZZOFF,  FUZZOFF,  FUZZOFF,  FUZZOFF,  FUZZOFF, 
    -FUZZOFF,  FUZZOFF, -FUZZOFF,  FUZZOFF,  FUZZOFF, -FUZZOFF, -FUZZOFF,  
     FUZZOFF,  FUZZOFF, -FUZZOFF, -FUZZOFF, -FUZZOFF, -FUZZOFF,  FUZZOFF,  
     FUZZOFF,  FUZZOFF,  FUZZOFF, -FUZZOFF,  FUZZOFF,  FUZZOFF, -FUZZOFF,  
     FUZZOFF
]

global_fuzz_pos = 0

# COLORMAP vertical offset darkening
FUZZ_COLORMAP = 6

# PLAYPAL index (darkish grey)
FUZZ_BACKGROUND = 108

def apply_fuzz(img, playpal, colormap):
    global global_fuzz_pos

    img = img.convert('RGBA')
    width, height = img.size
    pixels = img.load()

    # Make a PLAYPAL index sprite silhouette first
    grid = [[FUZZ_BACKGROUND if pixels[x, y][3] > 0 else None for y in range(height)] for x in range(width)]
    fuzz_pos = global_fuzz_pos % FUZZTABLE
    global_fuzz_pos = (global_fuzz_pos + 1) % FUZZTABLE

    # Samples outside the sprite hit the background, which gets darkened once
    edge_index = colormap[FUZZ_COLORMAP * 256 + FUZZ_BACKGROUND]

	# Now do the fuzz effect à la Doom
    for x in range(width):
        for y in range(height):
            if grid[x][y] is None:
                continue

            fuzz_offset = FUZZOFFSET[fuzz_pos]
            fuzz_pos = (fuzz_pos + 1) % FUZZTABLE

            row_shift = 1 if fuzz_offset > 0 else -1
            sample_y = y + row_shift

            if 0 <= sample_y < height and grid[x][sample_y] is not None:
                # Pixels above are already fuzzed and get darkened again, pixels below are still background
                target_index = colormap[FUZZ_COLORMAP * 256 + grid[x][sample_y]]
            else:
                target_index = edge_index

            grid[x][y] = target_index
            target_r, target_g, target_b = playpal[target_index]
            pixels[x, y] = (target_r, target_g, target_b, pixels[x, y][3])

    return img