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
import sys
import argparse

from doomdata import load_wads, parse_info_c
from render import generate_animations

VERSION = "1.1.0"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = "Generate Doom sprites into tic-accurate GIF animations")
    parser.add_argument("iwad", help = "Path to the main IWAD file (e.g. doom2.wad)")
    parser.add_argument("pwads", nargs = "*", help = "Optional PWAD files for overriding")
    parser.add_argument("--infoc", default = "info.c", help = "Path to info.c (default: info.c in the current folder)")
    parser.add_argument("--scale", type = float, default = 1.0, help = "Scaling factor for the output GIFs (default: 1.0)")
    parser.add_argument("--no-aspect-ratio", action = "store_true", help = "Disable classic 1.2x vertical pixel aspect ratio")
    parser.add_argument("--all-fuzz", action = "store_true", help = "Render all sprite animations with the partial invisibility effect")
    parser.add_argument("--version", action = "version", version = f"dsprite2gif { VERSION }")

    args = parser.parse_args()

    if args.scale > 10.0:
        print(f"WARNING: Scale factor { args.scale } is greater than 10.0, GIFs may become large and do weird things to your computer.")
        input("Press ENTER to continue...")

    try:
        print(f"Loading IWAD: { args.iwad }")

        if args.pwads:
            print(f"Loading PWAD(s): { ', '.join(args.pwads) }")
            
        combined_wad = load_wads(args.iwad, args.pwads)
        
        iwad_name = os.path.splitext(os.path.basename(args.iwad))[0]
        parts = [iwad_name]

        # Create unique folder names for unique IWAD/PWAD combos
        for pwad in args.pwads:
            parts.append(os.path.splitext(os.path.basename(pwad))[0])
        
        output_dir = f"animations_{ '_'.join(parts) }"
        
        sprite_names, states, state_name_to_index, state_index_to_name, mobjinfo_list = parse_info_c(args.infoc)
        
        use_aspect = not args.no_aspect_ratio

        generate_animations(
            combined_wad, 
            states, 
            state_name_to_index, 
            mobjinfo_list, 
            scale_factor = args.scale, 
            use_aspect_ratio = use_aspect, 
            all_fuzz = args.all_fuzz, 
            output_base = output_dir
        )
        print("Done!")
        
    except Exception as exception:
        print(f"Error: { exception }")
        sys.exit(1)