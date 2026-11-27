#!/usr/bin/env bash
# Digits2Fa 1.1 - macOS launcher (double-click in Finder)
# Put this file and Digits2Fa.py in the folder that contains your fonts
# (the fonts may also be in sub-folders), then double-click this file.
# First time only:  chmod +x Digits2Fa.command
# If macOS blocks it ("Apple could not verify ..."): open System Settings >
# Privacy & Security, scroll down and click "Open Anyway" (it appears after the
# first blocked attempt). Or right-click > Open, or run
#  xattr -d com.apple.quarantine Digits2Fa.command
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
    echo "On Windows use Digits2Fa.bat instead."
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
if [ "$DEPS_OK" = 1 ]; then
    $PY Digits2Fa.py . --mode component --suffix=-FD -r --collect per-folder --collect-folder "FD(Farsi Digits)"
fi

# ---- Only one font (commented example) --------------------------------------
# $PY Digits2Fa.py "Font.ttf" --mode component --suffix=-FD

# ---- Another folder or file (commented example) ------------------------------
# $PY Digits2Fa.py "/Users/me/Fonts" --mode component --suffix=-FD --arabic -r --collect per-folder --collect-folder "FD(Farsi Digits)"
# $PY Digits2Fa.py "/Users/me/Fonts/Font.ttf" --mode component --suffix=-FD -o "/Users/me/Fonts/out/Font-FD.ttf"

# Keep the Terminal window open until a key is pressed
echo
read -n 1 -s -r -p "Press any key to close..."
echo
