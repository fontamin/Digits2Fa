#!/usr/bin/env bash
# Digits2Fa 1.1 - macOS / Linux launcher
# (On Windows use Digits2Fa.bat.)
# Put this file and Digits2Fa.py in the folder that contains your fonts
# (the fonts may also be in sub-folders), then run it in a terminal:
#     bash Digits2Fa.sh
# (macOS: type "bash ", drag this file into the Terminal window, press Enter.)
# For ./Digits2Fa.sh make it executable once:  chmod +x Digits2Fa.sh
# Needs Python 3. The dependencies (fonttools, brotli) are checked on every run
# and installed if they are missing (see requirements.txt).

# Always work from the folder this script lives in
cd "$(dirname "$0")" || exit 1

# ---- Find a working Python 3 ------------------------------------------------
# (On Windows "python3" is often only a Microsoft Store shortcut that does not
#  work, so "python" and "py -3" are tried as well.)
PY=""
for cand in python3 python "py -3"; do
    if $cand -c "import sys; sys.exit(0 if sys.version_info[0] == 3 else 1)" >/dev/null 2>&1; then
        PY="$cand"
        break
    fi
done

# ---- Check dependencies: installs only what is missing, never upgrades ------
DEPS_OK=1
if [ -z "$PY" ]; then
    echo "Python 3 was not found (a Microsoft Store shortcut does not count)."
    echo "Please install it from https://www.python.org/downloads/"
    echo "On Windows you can also use Digits2Fa.bat."
    DEPS_OK=0
else
    if ! $PY -c "import fontTools" >/dev/null 2>&1; then
        echo "fonttools is missing - installing it ..."
        $PY -m pip install fonttools || $PY -m pip install --user fonttools
        if ! $PY -c "import fontTools" >/dev/null 2>&1; then
            echo "fonttools could not be installed automatically."
            echo "Please install it yourself:  $PY -m pip install fonttools"
            DEPS_OK=0
        fi
    fi
    if ! $PY -c "import brotli" >/dev/null 2>&1; then
        echo "brotli is missing - installing it ..."
        $PY -m pip install brotli || $PY -m pip install --user brotli
        if ! $PY -c "import brotli" >/dev/null 2>&1; then
            echo "brotli could not be installed automatically."
            echo "Please install it yourself:  $PY -m pip install brotli"
            DEPS_OK=0
        fi
    fi
fi

# ---- Default: convert EVERY font in this folder and in all its sub-folders --
#   .                       this folder (searched together with its sub-folders: -r)
#   --mode component        or: copy   (or use --cmap instead of --mode)
#   --suffix=-FD            suffix added to the font names (always required)
#   --collect per-folder    where the results go (required for a folder):
#                             per-folder = in every folder with more than one font,
#                                          into a sub-folder next to the originals
#                             single     = all results together in ONE folder
#                             none       = just next to the originals
#   --collect-folder NAME   name of that folder (change it freely; not used with none)
#   add --arabic to also convert the Arabic-Indic digits
STATUS=1
if [ "$DEPS_OK" = 1 ]; then
    $PY Digits2Fa.py . --mode component --suffix=-FD -r --collect per-folder --collect-folder "FD(Farsi Digits)"
    STATUS=$?
fi

# ---- Only one font (commented example) --------------------------------------
# $PY Digits2Fa.py "Font.ttf" --mode component --suffix=-FD

# ---- Another folder or file (commented example) ------------------------------
# $PY Digits2Fa.py "/Users/me/Fonts" --mode component --suffix=-FD --arabic -r --collect per-folder --collect-folder "FD(Farsi Digits)"
# $PY Digits2Fa.py "/Users/me/Fonts/Font.ttf" --mode component --suffix=-FD -o "/Users/me/Fonts/out/Font-FD.ttf"

# ---- Keep the window open (double-click) so the output can be read ----------
# Only in an interactive terminal; delete this block if you don't want the pause.
if [ -t 0 ]; then
    echo
    read -n 1 -s -r -p "Press any key to close..."
    echo
fi
exit $STATUS
