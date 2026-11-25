#!/usr/bin/env bash
# Digits2Fa - macOS launcher (double-click in Finder)
# Put this file, Digits2Fa.py and Font.ttf in the same folder.
# First time only:  chmod +x Digits2Fa.command
# (If macOS blocks it: right-click > Open, or run
#  xattr -d com.apple.quarantine Digits2Fa.command)
# Needs:  python3  and  pip3 install fonttools brotli

# Always work from the folder this script lives in
cd "$(dirname "$0")" || exit 1

# ---- Active command: Font.ttf in this folder -------------------------------
#   --mode component | copy      (or use --cmap instead of --mode)
#   --suffix=-FD                 (always required)
#   add --arabic to also convert the Arabic-Indic digits
python3 Digits2Fa.py "Font.ttf" --mode component --suffix=-FD

# ---- Same thing with another path (commented example) ----------------------
# python3 Digits2Fa.py "/Users/me/Fonts/Font.ttf" --mode component --suffix=-FD -o "/Users/me/Fonts/out/Font-FD.ttf"

# ---- A whole folder (commented example) ------------------------------------
# Every .ttf/.otf/.woff/.woff2 inside; -r also searches sub-folders;
# -o is the output folder (sub-folder structure is kept).
# python3 Digits2Fa.py "/Users/me/Fonts" --mode component --suffix=-FD --arabic -r -o "/Users/me/Fonts/out"

# Keep the Terminal window open until a key is pressed
echo
read -n 1 -s -r -p "Press any key to close..."
echo
