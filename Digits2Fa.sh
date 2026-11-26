#!/usr/bin/env bash
# Digits2Fa 1.1 - macOS / Linux launcher
# Put this file and Digits2Fa.py in the folder that contains your fonts
# (the fonts may also be in sub-folders), then run:
#     chmod +x Digits2Fa.sh      (once)
#     ./Digits2Fa.sh
# Needs Python 3. The dependencies (fonttools, brotli) are checked on every run
# and installed if they are missing (see requirements.txt).

# Always work from the folder this script lives in
cd "$(dirname "$0")" || exit 1

# ---- Check dependencies: installs only what is missing, never upgrades ------
if ! command -v python3 >/dev/null 2>&1; then
    echo "Python 3 was not found. Please install it from https://www.python.org/downloads/"
    DEPS_OK=0
else
    DEPS_OK=1
    if ! python3 -c "import fontTools" >/dev/null 2>&1; then
        echo "fonttools is missing - installing it ..."
        python3 -m pip install fonttools || python3 -m pip install --user fonttools
        if ! python3 -c "import fontTools" >/dev/null 2>&1; then
            echo "fonttools could not be installed automatically."
            echo "Please install it yourself:  pip3 install fonttools"
            DEPS_OK=0
        fi
    fi
    if ! python3 -c "import brotli" >/dev/null 2>&1; then
        echo "brotli is missing - installing it ..."
        python3 -m pip install brotli || python3 -m pip install --user brotli
        if ! python3 -c "import brotli" >/dev/null 2>&1; then
            echo "brotli could not be installed automatically."
            echo "Please install it yourself:  pip3 install brotli"
            DEPS_OK=0
        fi
    fi
fi

# ---- Default: convert EVERY font in this folder and in all its sub-folders --
#   .                       this folder (searched together with its sub-folders: -r)
#   --mode component        or: copy   (or use --cmap instead of --mode)
#   --suffix=-FD            suffix added to the font names (always required)
#   --collect-folder NAME   if more than one font is found, all results are
#                           gathered in a folder with this name (change it freely)
#   add --arabic to also convert the Arabic-Indic digits
if [ "$DEPS_OK" = 1 ]; then
    python3 Digits2Fa.py . --mode component --suffix=-FD -r --collect-folder "FD(Farsi Digits)"
fi

# ---- Only one font (commented example) --------------------------------------
# python3 Digits2Fa.py "Font.ttf" --mode component --suffix=-FD

# ---- Another folder or file (commented example) ------------------------------
# python3 Digits2Fa.py "/Users/me/Fonts" --mode component --suffix=-FD --arabic -r --collect-folder "FD(Farsi Digits)"
# python3 Digits2Fa.py "/Users/me/Fonts/Font.ttf" --mode component --suffix=-FD -o "/Users/me/Fonts/out/Font-FD.ttf"

[ "$DEPS_OK" = 1 ] || exit 1
