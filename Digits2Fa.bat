@echo off
REM Digits2Fa - Windows launcher
REM Put this file, Digits2Fa.py and Font.ttf in the same folder and double-click it.
REM Needs: Python 3  and  pip install fonttools brotli
REM (If "python" is not found, replace it with "py -3" below.)

REM Always work from the folder this file lives in
cd /d "%~dp0"

REM ---- Active command: Font.ttf in this folder ------------------------------
REM   --mode component ^| copy      (or use --cmap instead of --mode)
REM   --suffix=-FD                  (always required)
REM   add --arabic to also convert the Arabic-Indic digits
python Digits2Fa.py "Font.ttf" --mode component --suffix=-FD

REM ---- Same thing with another path (commented example) ---------------------
REM python Digits2Fa.py "C:\Users\me\Fonts\Font.ttf" --mode component --suffix=-FD -o "C:\Users\me\Fonts\out\Font-FD.ttf"

REM ---- A whole folder (commented example) -----------------------------------
REM Every .ttf/.otf/.woff/.woff2 inside; -r also searches sub-folders;
REM -o is the output folder (sub-folder structure is kept).
REM python Digits2Fa.py "C:\Users\me\Fonts" --mode component --suffix=-FD --arabic -r -o "C:\Users\me\Fonts\out"

pause
