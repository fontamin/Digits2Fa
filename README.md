# Digits2Fa

**Version 1.1**

Make a variant of a font in which the **Latin digits (0–9) look like the Farsi digits (۰–۹)**.

The Farsi digits (U+06F0–U+06F9) already exist in most Farsi fonts. Digits2Fa makes the Latin digits (U+0030–U+0039) use them, and optionally the Arabic‑Indic digits (U+0660–U+0669) too. The result is a font with Farsi digits wherever the Latin digits are typed, for places where the Latin digits can't be replaced by Farsi ones in the text itself (for example `Vazirmatn` → `Vazirmatn FD`).

The new font is always renamed with a suffix you choose, so it never has the same name as the original.

## Why do users need this kind of font?

Many programs don't let you change the Latin digits to Farsi ones, have no Farsi localization, or can't be localized at all. A font like this solves the problem on the font level: users only change the font and every digit is shown as a Farsi digit, without having to deal with software settings or environments.

## Are these fonts standard?

**No.** Fonts like this are not standard and may cause problems for machine readability: the text still contains Latin digits, only their shapes are Farsi. So what a person sees and what software reads can differ (for example in search, copy and paste, text-to-speech, OCR or text extraction, and accessibility tools).

Use them only as a workaround. If the underlying problem is solved some day (for example if the software shows Farsi digits natively or gets proper localization), it is better not to use this kind of font at all.

## Features

- Three methods: **component**, **copy** and **cmap** (see [Methods](#methods)).
- Works on TrueType (`glyf`), CFF/CFF2, variable fonts (`gvar`, `HVAR`/`VVAR`), colour fonts (`COLR` v0/v1) and `sbix` bitmap fonts.
- No nested components: if a Farsi glyph is itself a composite, its components are flattened down to outline glyphs.
- Advance widths are carried over (`USE_MY_METRICS` flag **and** copied `hmtx`/`vmtx`).
- Kerning (`GPOS` pair positioning, class and pair based, and the legacy `kern` table) of the Farsi digits is copied to the target digits. If the Farsi digits have no kerning, the target digits' kerning is removed.
- A Farsi digit that is already just a component of the target digit has the same shape and is skipped.
- Renames the font (family, full name, PostScript name, unique ID, CFF names) with your suffix, placed after the family name; the style/weight name is never changed.
- Converts a single file or a whole folder (optionally with all its sub-folders).
- Folder input with three ways to place the results (`--collect`): next to the originals, in a sub-folder of every folder (the folder structure of a font package stays intact), or all together in one folder.
- Input and output formats: `.ttf`, `.otf`, `.woff`, `.woff2` (and `.ttx` for a single file).

## Requirements

- Python 3 (3.9 or newer recommended; developed and tested with fontTools 4.67.0 on Python 3.12)
- [fontTools](https://github.com/fonttools/fonttools)
- [brotli](https://pypi.org/project/Brotli/), needed for `.woff2` fonts (the launchers always install it)

```bash
pip install -r requirements.txt
```

The launcher scripts (see below) check these dependencies on every run and install only what is missing; installed packages are never upgraded.

## Quick start

```bash
python Digits2Fa.py Font.ttf --mode component --suffix=-FD
```

This writes `Font-FD.ttf` next to `Font.ttf`. For `Font-Regular.ttf` the result is `Font-FD-Regular.ttf` and the family name `Font` becomes `Font-FD` (see [How the font is renamed](#how-the-font-is-renamed)).

> Long commands are written with one argument per line. On Linux/macOS a trailing `\` continues the command on the next line; in Windows `cmd` use `^` instead (PowerShell: a backtick), or simply put everything on one line.

> Write the suffix as `--suffix=-FD` (with `=`). A suffix that starts with a dash can otherwise be read as an option. A suffix without a dash (`--suffix FD`) also works.

## Methods

| Method | What happens | Notes |
|---|---|---|
| `--mode component` | The Latin glyph becomes a **component** of the Farsi glyph. | Smallest files, no duplicated outlines. Used automatically only for TrueType fonts without colour tables; CFF/CFF2 and colour fonts fall back to a full copy. On `sbix` fonts the Latin glyph becomes a `dupe` of the Farsi bitmap. |
| `--mode copy` | Everything is **duplicated** onto the Latin glyph: outlines, metrics, variations, colour layers, bitmaps. | Works on every supported font type. |
| `--cmap` | The `cmap` entries of the digits are pointed **straight at the Farsi glyphs**. | Nothing else is changed, so the old digit glyphs stay unused and the file doesn't get smaller. Not elegant, but sometimes the best choice. `--mode` is not used. |

In `component` and `copy` modes kerning is handled as described above. In `cmap` mode kerning follows the Farsi glyphs automatically.

## Options

| Option | Description |
|---|---|
| `path` | A font file or a folder. For a folder, every font in it is converted. |
| `-s`, `--suffix` | **Required.** Suffix added to the font names, e.g. `--suffix=-FD`. |
| `-m`, `--mode` | `component` or `copy`. **Required**, unless `--cmap` is used. |
| `--cmap` | Use the cmap method. Cannot be combined with `--mode`. |
| `--arabic` | Also apply the Farsi digits to the Arabic‑Indic digits (U+0660–0669), all ten, since their shapes may differ. Off by default. |
| `-o`, `--output` | Output file (single input) or output folder (folder input). Default: next to the input. |
| `-r`, `--recursive` | Folder input: also search sub‑folders. |
| `--collect` | **Required for a folder input, no default.** Where the results go: `per-folder`, `single` or `none` (see [Where the results go](#where-the-results-go-folder-input)). |
| `--collect-folder NAME` | Name of the folder used by `--collect per-folder` and `--collect single` (required for those two, not allowed with `none`; no default name). |
| `--keep-ttx` | Keep the modified `.ttx` next to the output font. |
| `--version` | Print the version and exit. |

The input is never overwritten.

## Examples

Single file:

```bash
python Digits2Fa.py Font.ttf --mode component --suffix=-FD

python Digits2Fa.py Font.ttf --mode copy --suffix=-FD

python Digits2Fa.py Font.ttf --cmap --suffix=-FD
```

Latin **and** Arabic‑Indic digits:

```bash
python Digits2Fa.py Font.ttf --mode component --suffix=-FD --arabic

python Digits2Fa.py Font.ttf --mode copy --suffix=-FD --arabic

python Digits2Fa.py Font.ttf --cmap --suffix=-FD --arabic
```

Output path, intermediate TTX:

```bash
python Digits2Fa.py Font.ttf -m component -s=-FD -o out/Font-FD.ttf

python Digits2Fa.py Font.ttf -m copy -s=-FD --keep-ttx
```

A folder (every `.ttf`, `.otf`, `.woff`, `.woff2` in it; `--collect` is always required for a folder):

```bash
python Digits2Fa.py ./fonts --mode component --suffix=-FD --collect none

python Digits2Fa.py ./fonts --mode copy --suffix=-FD -r --collect none

python Digits2Fa.py ./fonts --mode component --suffix=-FD --arabic -r --collect none -o ./out

python Digits2Fa.py ./fonts --cmap --suffix=-FD --collect none -o ./out
```

### Where the results go (folder input)

`--collect` decides, and there is no default:

| `--collect` | Result |
|---|---|
| `none` | Every result is written next to its original. No extra folder. |
| `per-folder` | Results are written next to the originals, but in every folder where **more than one** font is converted they go into a sub-folder (named by `--collect-folder`) of that same folder. A folder with a single font gets the result right beside it. The folder structure of a font package stays intact. |
| `single` | If more than one font is converted, **all** results of the run are put together in one folder (named by `--collect-folder`) in the input folder. If two fonts would get the same file name, the sub-folder structure is kept inside that folder. |

```bash
python Digits2Fa.py ./fonts -m component -s=-FD -r --collect per-folder --collect-folder "FD(Farsi Digits)"

python Digits2Fa.py ./fonts -m component -s=-FD -r --collect single --collect-folder "FD(Farsi Digits)"

python Digits2Fa.py ./fonts -m component -s=-FD -r --collect none
```

Result of `--collect per-folder`:

```
fonts/
├── A-Regular.ttf
├── A-Bold.ttf
├── FD(Farsi Digits)/        <- A-FD-Regular.ttf, A-FD-Bold.ttf
├── TTF/
│   ├── B-Regular.ttf
│   ├── B-Bold.ttf
│   └── FD(Farsi Digits)/    <- B-FD-Regular.ttf, B-FD-Bold.ttf
└── Single/
    ├── D-Regular.ttf
    └── D-FD-Regular.ttf     <- only one font: next to it
```

Result of `--collect single`:

```
fonts/
├── A-Regular.ttf, A-Bold.ttf
├── TTF/B-Regular.ttf, B-Bold.ttf
├── Single/D-Regular.ttf
└── FD(Farsi Digits)/        <- A-FD-Regular.ttf, A-FD-Bold.ttf, B-FD-Regular.ttf, ...
```

The collect folders are not searched again on the next run. With `--output ./out` the same structure is created inside `./out`.

In folder mode a failing font is reported and skipped; the others are still converted. Fonts whose name already contains the suffix (e.g. `Font-FD-Regular.ttf` or `Font-VF-FD[DSTY,KSHD,wght].ttf`; the `[axes]` part is ignored) are skipped so that a second run doesn't convert the results again. Font collections (`.ttc`, `.otc`) are not supported.

## Launcher scripts (just double-click)

Put the launcher and `Digits2Fa.py` in the folder that contains your fonts and run the launcher. **By default it converts every font in that folder and in all its sub-folders** (`.ttf`, `.otf`, `.woff`, `.woff2`):

```
python Digits2Fa.py . --mode component --suffix=-FD -r --collect per-folder --collect-folder "FD(Farsi Digits)"
```

- The suffix is `-FD`.
- `--collect per-folder`: in every folder where more than one font is found, the results are put in a sub-folder called `FD(Farsi Digits)` inside that same folder, so the folder structure of your font package stays intact and the converted fonts sit next to the originals. The folder name and the `--collect` choice are only arguments in the launcher; change them there if you like (for example `--collect single` to get everything in one folder). The Python script itself has no defaults for them.
- A folder with a single font gets the result right beside it.
- Before converting, the launcher checks whether `fonttools` and `brotli` are installed and installs only the missing ones with `pip install` (no upgrade). Both are required: if either can't be installed, nothing is converted and a message tells you how to install it yourself.

| File | System |
|---|---|
| `Digits2Fa.bat` | Windows (double‑click) |
| `Digits2Fa.command` | macOS (double‑click, includes a final pause; on the first run you may have to allow it in System Settings → Privacy & Security, see below) |
| `Digits2Fa.sh` | macOS / Linux (terminal). On Windows use `Digits2Fa.bat` instead. |

If Python is installed but the launcher says it was not found on Windows, the Microsoft Store shortcut is probably in the way: turn off *Settings → Apps → Advanced app settings → App execution aliases* for `python.exe` / `python3.exe`, or make sure the real Python is in `PATH`.

Each launcher also contains commented examples for a single font, another folder and another file. Edit them to change the mode, suffix, folder name or to add `--arabic`.

### macOS troubleshooting

- **"could not be executed because you do not have appropriate access privileges":** the file has no execute permission (this happens when a file is downloaded on its own, e.g. via "Raw" or "Save as"). Open Terminal in the folder and run, once:

  ```bash
  chmod +x Digits2Fa.command Digits2Fa.sh
  ```

  Or run it without changing anything: `bash Digits2Fa.command`.
- **"Apple could not verify ... is free of malware":** files from the internet carry a quarantine flag. You can allow the file yourself: after the first blocked attempt open **System Settings → Privacy & Security**, scroll down to the security section and click **Open Anyway** next to `Digits2Fa.command`, then confirm. (On older macOS versions the entry is under System Preferences → Security & Privacy → General.) Alternatively right‑click the file → Open, or run:

  ```bash
  xattr -d com.apple.quarantine Digits2Fa.command Digits2Fa.sh
  ```

## How it works

1. The font is opened and dumped to TTX (XML).
2. In the XML, the data of each target digit is replaced (component / copy) or its cmap entry is changed (cmap).
3. Kerning is adjusted, and the names are find‑and‑replaced with the suffix.
4. The modified TTX is compiled back to a font file.

## How the font is renamed

The suffix goes **after the family name and before the style (weight) name**. The style/weight name (`Regular`, `ExtraBlack`, …) is never changed; the script prints it after renaming. The family comes from the name table (ID 16, else ID 1), not from the position of a hyphen, so families that contain hyphens (like `AzarMehr-DS2`) work. With `--suffix=-FD`:

| Name | Before | After |
|---|---|---|
| Family (ID 1, 16) | `AzarMehr-DS2` | `AzarMehr-DS2-FD` |
| Full name (ID 4) | `AzarMehr-DS2 ExtraBlack` | `AzarMehr-DS2-FD ExtraBlack` |
| PostScript name (ID 6) | `AzarMehr-DS2ExtraBlack` | `AzarMehr-DS2-FD-ExtraBlack` |
| Unique ID (ID 3) | `3.000;amin;AzarMehr-DS2ExtraBlack` | `3.000;amin;AzarMehr-DS2-FD-ExtraBlack` |
| File name | | `AzarMehr-DS2-FD-ExtraBlack.ttf` (the new PostScript name) |

- In family and full names the suffix is used **as typed**: `--suffix=-FD` gives `Vazir-FD`, `--suffix=" FD"` (or `--suffix=FD`) gives `Vazir FD`. PostScript names and file names always get `-FD`, without spaces.
- Names are matched ignoring case, spaces, hyphens and underscores (so `AzarMehr DS2` and `AzarMehr-DS2` are the same family).
- The style names (ID 2 and ID 17) are not touched. If a font already has an odd typographic subfamily (ID 17), it stays as it is; fix it in the original.
- Mac and Windows name records are treated the same way.
- **Variable fonts** (fonts with an `fvar` table) get a file name of the form `Base-FD[axes]`. The axis tags are read from the font and sorted (custom axes in capitals first): `AzarMehr-VF[wght,DSTY].ttf` → `AzarMehr-VF-FD[DSTY,KSHD,wght].ttf`. Static fonts keep the naming described above.
- If the family can't be found in a name, the suffix is put before the style name when possible, otherwise appended at the end, and a warning is printed.

## Limitations

- The tool has mostly been tested on small synthetic TrueType test fonts (including class kerning, nested components and a variable font). **CFF/OTF, colour fonts (`COLR`) and `sbix` fonts are implemented but not tested on real‑world fonts.** Please check the output (especially widths, kerning and variable instances) before releasing a font.
- Not copied (a warning is printed if present): `SVG`, `CBDT`/`CBLC`, `EBDT`/`EBLC`, `VORG`.
- `HVAR` without an `AdvWidthMap`: advance variations of the target digits can't be copied (warning).
- In `component` mode a glyph keeps nested components when flattening is impossible (variable fonts, hinting instructions in the composite, or transformed/point‑matched components). A warning is printed.
- Alternate digit glyphs (tabular, superscript, `zero.xxx`, …) are not touched, except composites that use the base digit glyph as a component.
- If a Farsi glyph uses the target digit glyph as a transformed or offset component, the target is left unchanged to avoid a loop (warning).

## Changelog

**1.1**
- The launchers (`.bat`, `.command`, `.sh`) now convert every font in their folder and all sub-folders by default, with suffix `-FD`.
- New `--collect per-folder|single|none` argument (required for a folder input, no default) and `--collect-folder NAME`: results next to the originals, in a sub-folder of every folder with more than one font (the launchers use `per-folder` and `FD(Farsi Digits)`, so the folder structure is kept), or all together in one folder.
- New `--version` argument.
- The launchers check the dependencies (`fonttools`, `brotli`) first and install only the missing ones; nothing is upgraded. Both are required.
- Added `requirements.txt`.
- Naming: the suffix is now inserted after the family name (taken from the name table) and before the style name, which is never changed; used as typed in family/full names (`--suffix=-FD` gives `Family-FD`); the file name is the new PostScript name. Families with hyphens (e.g. `AzarMehr-DS2`) are handled correctly.
- Variable fonts: the file name becomes `Base-FD[axes]` with the axes taken from the font's `fvar` table (sorted); converted variable fonts (`…-FD[…]`) are skipped in folder runs.
- The launchers look for a working Python 3 (`python3`, `python`, `py -3`) and ignore the Microsoft Store shortcut that Windows installs as `python3`/`python` when Python isn't really installed. On failure `.sh` and `.bat` keep the window open.

**1.0**
- First release: component, copy and cmap methods, folder conversion, launchers.

## Made with Claude

This tool was created with the help of [Claude](https://claude.ai) by Anthropic.

## License

[MIT](LICENSE)
