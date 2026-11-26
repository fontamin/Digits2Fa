@echo off
REM Digits2Fa 1.1 - Windows launcher
REM Put this file and Digits2Fa.py in the folder that contains your fonts
REM (the fonts may also be in sub-folders), then double-click this file.
REM Needs: Python 3  and  pip install fonttools brotli
REM (If "python" is not found, replace it with "py -3" below.)

REM Always work from the folder this file lives in
cd /d "%~dp0"

REM ---- Default: convert EVERY font in this folder and in all its sub-folders --
REM   .                       this folder (searched together with its sub-folders: -r)
REM   --mode component        or: copy   (or use --cmap instead of --mode)
REM   --suffix=-FD            suffix added to the font names (always required)
REM   --collect-folder NAME   if more than one font is found, all results are
REM                           gathered in a folder with this name (change it freely)
REM   add --arabic to also convert the Arabic-Indic digits
python Digits2Fa.py . --mode component --suffix=-FD -r --collect-folder "FD(Farsi Digits)"

REM ---- Only one font (commented example) ------------------------------------
REM python Digits2Fa.py "Font.ttf" --mode component --suffix=-FD

REM ---- Another folder or file (commented example) ---------------------------
REM python Digits2Fa.py "C:\Users\me\Fonts" --mode component --suffix=-FD --arabic -r --collect-folder "FD(Farsi Digits)"
REM python Digits2Fa.py "C:\Users\me\Fonts\Font.ttf" --mode component --suffix=-FD -o "C:\Users\me\Fonts\out\Font-FD.ttf"

pause
