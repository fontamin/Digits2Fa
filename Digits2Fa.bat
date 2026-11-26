@echo off
REM Digits2Fa 1.1 - Windows launcher
REM Put this file and Digits2Fa.py in the folder that contains your fonts
REM (the fonts may also be in sub-folders), then double-click this file.
REM Needs Python 3. The dependencies (fonttools, brotli) are checked on every run
REM and installed if they are missing (see requirements.txt).
REM (If "python" is not found, replace it with "py -3" everywhere below.)

REM Always work from the folder this file lives in
cd /d "%~dp0"

REM ---- Check dependencies: installs only what is missing, never upgrades ----
where python >nul 2>&1
if errorlevel 1 (
    echo Python 3 was not found. Please install it from https://www.python.org/downloads/
    echo and tick "Add python.exe to PATH" in the installer.
    pause
    exit /b 1
)

python -c "import fontTools" >nul 2>&1
if errorlevel 1 (
    echo fonttools is missing - installing it ...
    python -m pip install fonttools
    python -c "import fontTools" >nul 2>&1
    if errorlevel 1 (
        echo fonttools could not be installed automatically.
        echo Please install it yourself:  pip install fonttools
        pause
        exit /b 1
    )
)

python -c "import brotli" >nul 2>&1
if errorlevel 1 (
    echo brotli is missing - installing it ...
    python -m pip install brotli
    python -c "import brotli" >nul 2>&1
    if errorlevel 1 (
        echo brotli could not be installed automatically.
        echo Please install it yourself:  pip install brotli
        pause
        exit /b 1
    )
)

REM ---- Default: convert EVERY font in this folder and in all its sub-folders --
REM   .                       this folder (searched together with its sub-folders: -r)
REM   --mode component        or: copy   (or use --cmap instead of --mode)
REM   --suffix=-FD            suffix added to the font names (always required)
REM   --collect per-folder  where the results go (required for a folder):
REM                           per-folder = in every folder with more than one font,
REM                                        into a sub-folder next to the originals
REM                           single     = all results together in ONE folder
REM                           none       = just next to the originals
REM   --collect-folder NAME   name of that folder (change it freely; not used with none)
REM   add --arabic to also convert the Arabic-Indic digits
python Digits2Fa.py . --mode component --suffix=-FD -r --collect per-folder --collect-folder "FD(Farsi Digits)"

REM ---- Only one font (commented example) ------------------------------------
REM python Digits2Fa.py "Font.ttf" --mode component --suffix=-FD

REM ---- Another folder or file (commented example) ---------------------------
REM python Digits2Fa.py "C:\Users\me\Fonts" --mode component --suffix=-FD --arabic -r --collect per-folder --collect-folder "FD(Farsi Digits)"
REM python Digits2Fa.py "C:\Users\me\Fonts\Font.ttf" --mode component --suffix=-FD -o "C:\Users\me\Fonts\out\Font-FD.ttf"

pause
