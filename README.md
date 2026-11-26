# Digits2Fa

**Version 1.1**

Make a variant of a font in which the **Latin digits (0–9) look like the Persian digits (۰–۹)**.

The Persian digits (U+06F0–U+06F9) already exist in most Persian fonts. Digits2Fa makes the Latin digits (U+0030–U+0039) use them, and optionally the Arabic‑Indic digits (U+0660–U+0669) too. The result is a font with Persian digits wherever the Latin digits are typed, for places where the Latin digits can't be replaced by Persian ones in the text itself (for example `Vazirmatn` → `Vazirmatn FD`).

The new font is always renamed with a suffix you choose, so it never has the same name as the original.

## Features

- Three methods: **component**, **copy** and **cmap** (see [Methods](#methods)).
- Works on TrueType (`glyf`), CFF/CFF2, variable fonts (`gvar`, `HVAR`/`VVAR`), colour fonts (`COLR` v0/v1) and `sbix` bitmap fonts.
- No nested components: if a Persian glyph is itself a composite, its components are flattened down to outline glyphs.
- Advance widths are carried over (`USE_MY_METRICS` flag **and** copied `hmtx`/`vmtx`).
- Kerning (`GPOS` pair positioning, class and pair based, and the legacy `kern` table) of the Persian digits is copied to the target digits. If the Persian digits have no kerning, the target digits' kerning is removed.
- A Persian digit that is already just a component of the target digit has the same shape and is skipped.
- Renames the font (family, full name, PostScript name, unique ID, CFF names) with your suffix.
- Converts a single file or a whole folder (optionally with all its sub-folders).
- Can gather the results of a folder run in one folder of your choice (`--collect-folder`).
- Input and output formats: `.ttf`, `.otf`, `.woff`, `.woff2` (and `.ttx` for a single file).

## Requirements

- Python 3.8+
- [fontTools](https://github.com/fonttools/fonttools)

```bash
pip install fonttools
pip install brotli      # only needed for .woff2
```

## Quick start

```bash
python Digits2Fa.py Font.ttf --mode component --suffix=-FD
```

This writes `Font-FD.ttf` next to `Font.ttf`. `Font-Regular.ttf` becomes `Font-FD-Regular.ttf`, and the family name `Font` becomes `Font FD`.

> Write the suffix as `--suffix=-FD` (with `=`). A suffix that starts with a dash can otherwise be read as an option. A suffix without a dash (`--suffix FD`) also works.

## Methods

| Method | What happens | Notes |
|---|---|---|
| `--mode component` | The Latin glyph becomes a **component** of the Persian glyph. | Smallest files, no duplicated outlines. Used automatically only for TrueType fonts without colour tables; CFF/CFF2 and colour fonts fall back to a full copy. On `sbix` fonts the Latin glyph becomes a `dupe` of the Persian bitmap. |
| `--mode copy` | Everything is **duplicated** onto the Latin glyph: outlines, metrics, variations, colour layers, bitmaps. | Works on every supported font type. |
| `--cmap` | The `cmap` entries of the digits are pointed **straight at the Persian glyphs**. | Nothing else is changed, so the old digit glyphs stay unused and the file doesn't get smaller. Not elegant, but sometimes the best choice. `--mode` is not used. |

In `component` and `copy` modes kerning is handled as described above. In `cmap` mode kerning follows the Persian glyphs automatically.

## Options

| Option | Description |
|---|---|
| `path` | A font file or a folder. For a folder, every font in it is converted. |
| `-s`, `--suffix` | **Required.** Suffix added to the font names, e.g. `--suffix=-FD`. |
| `-m`, `--mode` | `component` or `copy`. **Required**, unless `--cmap` is used. |
| `--cmap` | Use the cmap method. Cannot be combined with `--mode`. |
| `--arabic` | Also apply the Persian digits to the Arabic‑Indic digits (U+0660–0669), all ten, since their shapes may differ. Off by default. |
| `-o`, `--output` | Output file (single input) or output folder (folder input). Default: next to the input. |
| `-r`, `--recursive` | Folder input: also search sub‑folders. |
| `--collect-folder NAME` | Folder input: if more than one font is converted, gather all results in a folder called `NAME` (inside the input folder, or inside `--output` if given). There is no default name. |
| `--keep-ttx` | Keep the modified `.ttx` next to the output font. |
| `--version` | Print the version and exit. |

The input is never overwritten.

## Examples

Single file:

```bash
python Digits2Fa.py Font.ttf --mode component --suffix=-FD
python Digits2Fa.py Font.ttf --mode copy      --suffix=-FD
python Digits2Fa.py Font.ttf --cmap           --suffix=-FD
```

Latin **and** Arabic‑Indic digits:

```bash
python Digits2Fa.py Font.ttf --mode component --suffix=-FD --arabic
python Digits2Fa.py Font.ttf --mode copy      --suffix=-FD --arabic
python Digits2Fa.py Font.ttf --cmap           --suffix=-FD --arabic
```

Output path, intermediate TTX:

```bash
python Digits2Fa.py Font.ttf -m component -s=-FD -o out/Font-FD.ttf
python Digits2Fa.py Font.ttf -m copy -s=-FD --keep-ttx
```

A folder (every `.ttf`, `.otf`, `.woff`, `.woff2` in it):

```bash
python Digits2Fa.py ./fonts --mode component --suffix=-FD
python Digits2Fa.py ./fonts --mode copy --suffix=-FD -r
python Digits2Fa.py ./fonts --mode component --suffix=-FD --arabic -r -o ./out
python Digits2Fa.py ./fonts --cmap --suffix=-FD -o ./out
```

A folder with all its sub-folders, results gathered in one folder:

```bash
python Digits2Fa.py ./fonts --mode component --suffix=-FD -r --collect-folder "FD(Farsi Digits)"
```

If only one font is found, nothing is collected and the result is written next to it. The collect folder is not searched again on the next run. If two fonts would get the same output file name (e.g. `A-Regular.ttf` in two sub-folders), the sub-folder structure is kept inside the collect folder.

In folder mode a failing font is reported and skipped; the others are still converted. Fonts whose name already contains the suffix (e.g. `Font-FD-Regular.ttf`) are skipped so that a second run doesn't convert the results again. Font collections (`.ttc`, `.otc`) are not supported.

## Launcher scripts (just double-click)

Put the launcher and `Digits2Fa.py` in the folder that contains your fonts and run the launcher. **By default it converts every font in that folder and in all its sub-folders** (`.ttf`, `.otf`, `.woff`, `.woff2`):

```
python Digits2Fa.py . --mode component --suffix=-FD -r --collect-folder "FD(Farsi Digits)"
```

- The suffix is `-FD`.
- If more than one font is found, all results are gathered in a folder called `FD(Farsi Digits)`. The folder name is only an argument in the launcher; change it there if you like. The Python script itself has no default for it.
- With a single font the result is written next to it.

| File | System |
|---|---|
| `Digits2Fa.bat` | Windows (double‑click) |
| `Digits2Fa.command` | macOS (double‑click, includes a final pause) |
| `Digits2Fa.sh` | macOS / Linux (terminal) |

Each launcher also contains commented examples for a single font, another folder and another file. Edit them to change the mode, suffix, folder name or to add `--arabic`.

On macOS run `chmod +x Digits2Fa.command` (or `Digits2Fa.sh`) once. Files downloaded from the internet get a quarantine flag, so macOS may refuse to open them; either right‑click → Open, or run:

```bash
xattr -d com.apple.quarantine Digits2Fa.command
```

## How it works

1. The font is opened and dumped to TTX (XML).
2. In the XML, the data of each target digit is replaced (component / copy) or its cmap entry is changed (cmap).
3. Kerning is adjusted, and the names are find‑and‑replaced with the suffix.
4. The modified TTX is compiled back to a font file.

## Limitations

- The tool has mostly been tested on small synthetic TrueType test fonts (including class kerning, nested components and a variable font). **CFF/OTF, colour fonts (`COLR`) and `sbix` fonts are implemented but not tested on real‑world fonts.** Please check the output (especially widths, kerning and variable instances) before releasing a font.
- Not copied (a warning is printed if present): `SVG`, `CBDT`/`CBLC`, `EBDT`/`EBLC`, `VORG`.
- `HVAR` without an `AdvWidthMap`: advance variations of the target digits can't be copied (warning).
- In `component` mode a glyph keeps nested components when flattening is impossible (variable fonts, hinting instructions in the composite, or transformed/point‑matched components). A warning is printed.
- Alternate digit glyphs (tabular, superscript, `zero.xxx`, …) are not touched, except composites that use the base digit glyph as a component.
- If a Persian glyph uses the target digit glyph as a transformed or offset component, the target is left unchanged to avoid a loop (warning).

## Changelog

**1.1**
- The launchers (`.bat`, `.command`, `.sh`) now convert every font in their folder and all sub-folders by default, with suffix `-FD`.
- New `--collect-folder NAME` argument: with more than one font, all results are gathered in one folder (the launchers use `FD(Farsi Digits)`).
- New `--version` argument.

**1.0**
- First release: component, copy and cmap methods, folder conversion, launchers.

## Made with Claude

This tool was created with the help of [Claude](https://claude.ai) by Anthropic.

## License

[MIT](LICENSE)
