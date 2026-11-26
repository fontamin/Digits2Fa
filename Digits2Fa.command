#!/usr/bin/env bash
# Digits2Fa 1.1 - macOS launcher (double-click in Finder)
# Put this file and Digits2Fa.py in the folder that contains your fonts
# (the fonts may also be in sub-folders), then double-click this file.
# First time only:  chmod +x Digits2Fa.command
# (If macOS blocks it: right-click > Open, or run
#  xattr -d com.apple.quarantine Digits2Fa.command)
# Needs:  python3  and  pip3 install fonttools brotli

# Always work from the folder this script lives in
cd "$(dirname "$0")" || exit 1

# ---- Default: convert EVERY font in this folder and in all its sub-folders --
#   .                       this folder (searched together with its sub-folders: -r)
#   --mode component        or: copy   (or use --cmap instead of --mode)
#   --suffix=-FD            suffix added to the font names (always required)
#   --collect-folder NAME   if more than one font is found, all results are
#                           gathered in a folder with this name (change it freely)
#   add --arabic to also convert the Arabic-Indic digits
python3 Digits2Fa.py . --mode component --suffix=-FD -r --collect-folder "FD(Farsi Digits)"

# ---- Only one font (commented example) --------------------------------------
# python3 Digits2Fa.py "Font.ttf" --mode component --suffix=-FD

# ---- Another folder or file (commented example) ------------------------------
# python3 Digits2Fa.py "/Users/me/Fonts" --mode component --suffix=-FD --arabic -r --collect-folder "FD(Farsi Digits)"
# python3 Digits2Fa.py "/Users/me/Fonts/Font.ttf" --mode component --suffix=-FD -o "/Users/me/Fonts/out/Font-FD.ttf"

# Keep the Terminal window open until a key is pressed
echo
read -n 1 -s -r -p "Press any key to close..."
echo
