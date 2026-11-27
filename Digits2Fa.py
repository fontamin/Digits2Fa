#!/usr/bin/env python3
r"""
Digits2Fa 1.1 - give a font Farsi digits where the Latin digits (0-9) are.

The Latin digits (U+0030..0039) are made to look like the Farsi digits
(U+06F0..06F9).  With --arabic the Arabic-Indic digits (U+0660..0669) get the
Farsi shapes as well (all ten, since their shapes may differ).  A Farsi
digit that is already just a component of the target digit has the same shape
and is skipped.  Goal: variants with Farsi digits for places where the
Latin digits cannot be changed.

Three methods
-------------
--mode component   (default choice for TrueType)
    The Latin glyph becomes a component of the Farsi glyph: no duplicated
    outlines, smaller file.
      * If the Farsi glyph is itself a composite, its components are reused;
        nested composites are flattened down to outline glyphs, so there are
        no composites inside composites.
      * USE_MY_METRICS is set on the component and hmtx (width / lsb) is
        copied too, so the advance is right in every case.
      * Variable fonts: the gvar entry of the Latin glyph is converted.
      * sbix bitmaps: the Latin glyph becomes a "dupe" of the Farsi bitmap.
      * Fonts with colour tables (COLR / SVG / CBDT / EBDT) and CFF/CFF2 fonts
        (no components there) automatically use a full copy.
--mode copy
    Everything is duplicated onto the Latin glyph: outlines (glyf / CFF /
    CFF2), hmtx / vmtx, HVAR / VVAR, gvar, COLR v0/v1 (+ ClipList), sbix.
--cmap
    The cmap entries of the digits are pointed straight at the Farsi
    glyphs.  Nothing else is changed (the old digit glyphs just stay unused,
    so the file does not get smaller).  --mode is not used.  Not elegant,
    but sometimes the best choice.

In 'component' and 'copy' modes kerning is handled as well: if the Farsi
digits have kerning (GPOS PairPos format 1 & 2, legacy 'kern') it is copied to
the target digits, otherwise the target digits' kerning is removed.

Workflow: font -> TTX (XML) -> edit -> compile back.

Names: the suffix is inserted after the FAMILY name and before the style
(weight) name, which is never changed.  The family is taken from the name table
(ID 16, else ID 1), not from the position of a hyphen.  With --suffix=-FD:
    family       AzarMehr-DS2             ->  AzarMehr-DS2-FD
    full name    AzarMehr-DS2 ExtraBlack  ->  AzarMehr-DS2-FD ExtraBlack
    PostScript   AzarMehr-DS2ExtraBlack   ->  AzarMehr-DS2-FD-ExtraBlack
    unique ID    ...;AzarMehr-DS2ExtraBlack  ->  ...;AzarMehr-DS2-FD-ExtraBlack
    file name    the new PostScript name:  AzarMehr-DS2-FD-ExtraBlack.ttf
In display names (family, full name) the suffix is used as typed: -FD gives
"-FD", --suffix=" FD" (or FD) gives " FD".  PostScript names always get "-FD".

Examples (imaginary Font.ttf)
-----------------------------
Write the suffix as --suffix=-FD (with '='), otherwise a leading dash may be
read as an option.  A suffix without a dash (--suffix FD) works too.

  Single file, Latin digits only
    python Digits2Fa.py Font.ttf \
        --mode component \
        --suffix=-FD

    python Digits2Fa.py Font.ttf \
        --mode copy \
        --suffix=-FD

    python Digits2Fa.py Font.ttf \
        --cmap \
        --suffix=-FD

  Single file, Latin + Arabic-Indic digits
    python Digits2Fa.py Font.ttf \
        --mode component \
        --suffix=-FD \
        --arabic

    python Digits2Fa.py Font.ttf \
        --mode copy \
        --suffix=-FD \
        --arabic

    python Digits2Fa.py Font.ttf \
        --cmap \
        --suffix=-FD \
        --arabic

  Output path / keep the intermediate TTX
    python Digits2Fa.py Font.ttf \
        -m component \
        -s=-FD \
        -o out/Font-FD.ttf

    python Digits2Fa.py Font.ttf \
        -m copy \
        -s=-FD \
        --keep-ttx

  A folder (every .ttf .otf .woff .woff2 in it; -r also searches sub-folders;
  --collect is required, see below; with -o the output folder keeps the
  sub-folder structure)
    python Digits2Fa.py ./fonts \
        --mode component \
        --suffix=-FD \
        --collect none

    python Digits2Fa.py ./fonts \
        --mode copy \
        --suffix=-FD \
        -r \
        --collect none

    python Digits2Fa.py ./fonts \
        --mode component \
        --suffix=-FD \
        --arabic \
        -r \
        --collect none \
        -o ./out

    python Digits2Fa.py ./fonts \
        --cmap \
        --suffix=-FD \
        --collect none \
        -o ./out

    python Digits2Fa.py ./fonts \
        --cmap \
        --suffix=-FD \
        --arabic \
        -r \
        --collect none

Where the results go (folder input; --collect is required, there is no default)
    --collect none         results are written next to the originals
    --collect per-folder   next to the originals too, but in every folder where
                           more than one font is converted the results are put
                           in a sub-folder (named by --collect-folder) of that
                           same folder; a single font gets its result right
                           beside it.  The folder structure of a font package
                           is not disturbed.
    --collect single       all results of the run are put together in ONE folder
                           (named by --collect-folder) in the input folder, if
                           more than one font is converted.  If two fonts would
                           get the same file name, the sub-folder structure is
                           kept inside that folder.
    --collect-folder NAME  required for per-folder and single, not allowed with
                           none.  No default name.  These folders are not
                           searched again on the next run.  With --output the
                           same structure is created inside the output folder.
    python Digits2Fa.py ./fonts \
        -m component \
        -s=-FD \
        -r \
        --collect per-folder \
        --collect-folder "FD(Farsi Digits)"

    python Digits2Fa.py ./fonts \
        -m component \
        -s=-FD \
        -r \
        --collect single \
        --collect-folder "FD(Farsi Digits)"

    python Digits2Fa.py ./fonts \
        -m component \
        -s=-FD \
        -r \
        --collect none

Rules: --suffix is always required (the new font must not share the name of
the old one); --mode is required unless --cmap is given; --mode and --cmap
cannot be combined; --collect is required for a folder input; the input is
never overwritten.

Requires: fontTools  (pip install fonttools; add brotli for woff2)
"""

import argparse
import copy
import os
import re
import sys
import tempfile
import xml.etree.ElementTree as ET
from collections import namedtuple

from fontTools.ttLib import TTFont

__version__ = "1.1"

LATIN_BASE = 0x0030      # U+0030..U+0039
FARSI_BASE = 0x06F0    # U+06F0..U+06F9
ARABIC_BASE = 0x0660     # U+0660..U+0669 (Arabic-Indic), only with --arabic
USE_MY_METRICS = 0x0200
ROUND_XY_TO_GRID = 0x0004
COLOR_TABLES = ("COLR", "SVG", "CBDT", "CBLC", "EBDT", "EBLC")
BIG = 10 ** 9

# ----------------------------------------------------------------------------
# Per-glyph data in TTX that has to be copied from the Farsi glyph to the
# Latin glyph.   (entry tag, attribute holding glyph name, child holding name)
# ----------------------------------------------------------------------------
Spec = namedtuple("Spec", "tag attr child sort")

GLYPH_TABLES = {
    "glyf": [Spec("TTGlyph", "name", None, False)],
    "hmtx": [Spec("mtx", "name", None, False)],
    "vmtx": [Spec("mtx", "name", None, False)],
    "gvar": [Spec("glyphVariations", "glyph", None, False)],
    "CFF": [Spec("CharString", "name", None, False)],
    "CFF2": [Spec("CharString", "name", None, False)],
    "COLR": [
        Spec("ColorGlyph", "name", None, True),                  # v0
        Spec("BaseGlyphPaintRecord", None, "BaseGlyph", True),   # v1
        Spec("BaseGlyphV1Record", None, "BaseGlyph", True),      # old v1 name
    ],
    "sbix": [Spec("glyph", "name", None, True)],
    "HVAR": [Spec("Map", "glyph", None, False)],
    "VVAR": [Spec("Map", "glyph", None, False)],
}
UNSUPPORTED = ("SVG", "CBDT", "CBLC", "EBDT", "EBLC", "VORG")


def get_name(el, spec):
    if spec.child:
        c = el.find(spec.child)
        return c.get("value") if c is not None else None
    return el.get(spec.attr)


def set_name(el, spec, name):
    if spec.child:
        el.find(spec.child).set("value", name)
    else:
        el.set(spec.attr, name)


# ----------------------------------------------------------------------------
# Reading helpers
# ----------------------------------------------------------------------------
def read_glyph_order(root):
    go = root.find("GlyphOrder")
    if go is None:
        sys.exit("No GlyphOrder in TTX.")
    return {g.get("name"): int(g.get("id")) for g in go.findall("GlyphID")}


def read_cmap(root):
    cmap = root.find("cmap")
    if cmap is None:
        sys.exit("Font has no cmap table.")
    subs = [s for s in cmap if s.tag.startswith("cmap_format_")]

    def prio(s):
        key = (s.get("platformID"), s.get("platEncID"))
        if key in {("3", "10"), ("0", "4"), ("0", "6")}:
            return 0
        return 1 if s.get("platformID") in ("0", "3") else 2

    result = {}
    for sub in sorted(subs, key=prio):
        for m in sub.iter("map"):
            code = m.get("code")
            if code is not None:
                result.setdefault(int(code, 16), m.get("name"))
    return result


# ----------------------------------------------------------------------------
# Copying glyph data
# ----------------------------------------------------------------------------
def resort(parent, spec, order):
    idxs = [i for i, c in enumerate(parent) if c.tag == spec.tag]
    items = sorted((parent[i] for i in idxs),
                   key=lambda c: order.get(get_name(c, spec), BIG))
    for i, c in zip(idxs, items):
        parent[i] = c
    for n, c in enumerate(items):
        if "index" in c.attrib:
            c.set("index", str(n))


def sync_entries(table, spec, dst_to_src, order):
    """Make the entry of every Latin glyph (dst) a copy of the Farsi one."""
    count = 0
    parents = [p for p in table.iter() if any(c.tag == spec.tag for c in p)]
    for parent in parents:
        entries = {}
        for c in parent:
            if c.tag == spec.tag:
                n = get_name(c, spec)
                if n is not None:
                    entries[n] = c
        touched = False
        for dst, src in dst_to_src.items():
            s, d = entries.get(src), entries.get(dst)
            if s is None and d is None:
                continue
            new = None
            if s is not None:
                new = copy.deepcopy(s)
                set_name(new, spec, dst)
            if d is not None:
                pos = list(parent).index(d)
                if new is not None:
                    if "index" in d.attrib:
                        new.set("index", d.get("index"))
                    parent[pos] = new
                else:
                    parent.remove(d)       # Farsi glyph has none -> drop it
            else:
                parent.append(new)
            touched = True
            count += 1
        if touched and spec.sort:
            resort(parent, spec, order)
    return count


# ----------------------------------------------------------------------------
# Component mode (TrueType outlines) and sbix "dupe"
# ----------------------------------------------------------------------------
def glyph_kind(g):
    if g.find("component") is not None:
        return "composite"
    if g.find("contour") is not None:
        return "simple"
    return "empty"


def count_points(g):
    return sum(len(c.findall("pt")) for c in g.findall("contour"))


def has_instructions(g):
    ins = g.find("instructions")
    return ins is not None and any((e.text or "").strip() for e in ins.iter())


def is_plain_translation(c):
    return c.get("firstPt") is None and not any(
        k in c.attrib for k in ("scale", "scalex", "scale01", "scale10", "scaley"))


def flatten_components(glyphs, name, seen=()):
    """Components of composite `name` with nested composites expanded, so that
    every returned component points at an outline glyph.  None if impossible
    (transformed / point-matched nested components, hinting instructions...)."""
    if name in seen:
        return None
    g = glyphs[name]
    comps = g.findall("component")
    out = []
    for c in comps:
        child = glyphs.get(c.get("glyphName"))
        if child is None:
            return None
        if glyph_kind(child) != "composite":
            out.append(copy.deepcopy(c))            # leaf: keep verbatim
            continue
        # nested composite -> expand it
        if has_instructions(g) or has_instructions(child) or not is_plain_translation(c):
            return None
        sub = flatten_components(glyphs, c.get("glyphName"), seen + (name,))
        if sub is None:
            return None
        for sc in sub:
            if not is_plain_translation(sc):
                return None
            n = copy.deepcopy(sc)
            n.set("x", str(int(sc.get("x")) + int(c.get("x"))))
            n.set("y", str(int(sc.get("y")) + int(c.get("y"))))
            fl = int(sc.get("flags", "0"), 16)
            if not (fl & USE_MY_METRICS and int(c.get("flags", "0"), 16) & USE_MY_METRICS):
                fl &= ~USE_MY_METRICS
            n.set("flags", hex(fl))
            out.append(n)
    return out


def build_component_glyphs(glyf, dst_to_src, has_gvar):
    """Replace each Latin digit glyph with a component reference to the Farsi
    glyph (or a copy of its components).  Returns (stats, {dst: n_points})
    where the dict lists the glyphs that became a composite of a simple glyph
    (needed to convert their gvar data)."""
    glyphs = {g.get("name"): g for g in glyf.findall("TTGlyph")}
    stats = {"component": 0, "verbatim": 0, "flattened": 0, "nested_kept": 0}
    simple_points, new_elems = {}, {}
    for dst, src in dst_to_src.items():
        s = glyphs.get(src)
        if s is None:
            continue
        kind = glyph_kind(s)
        attrs = {k: v for k, v in s.attrib.items() if k != "name"}
        if kind == "simple":
            new = ET.Element("TTGlyph", attrs)
            new.set("name", dst)
            ET.SubElement(new, "component", glyphName=src, x="0", y="0",
                          flags=hex(ROUND_XY_TO_GRID | USE_MY_METRICS))
            simple_points[dst] = count_points(s)
            stats["component"] += 1
        else:
            new = None
            if kind == "composite":
                nested = any(glyph_kind(glyphs[c.get("glyphName")]) == "composite"
                             for c in s.findall("component")
                             if c.get("glyphName") in glyphs)
                if nested:
                    flat = None if has_gvar else flatten_components(glyphs, src)
                    if flat is not None:
                        new = ET.Element("TTGlyph", attrs)
                        new.set("name", dst)
                        for c in flat:
                            new.append(c)
                        stats["flattened"] += 1
                    else:
                        stats["nested_kept"] += 1
                else:
                    stats["verbatim"] += 1
            if new is None:
                new = copy.deepcopy(s)
                new.set("name", dst)
        new_elems[dst] = new
    for dst, new in new_elems.items():
        old = glyphs.get(dst)
        if old is not None:
            glyf[list(glyf).index(old)] = new
        else:
            glyf.append(new)
    return stats, simple_points


def gvar_for_components(gvar, simple_points):
    """Latin glyph is now a 1-component composite: point indexes of the 4
    phantom points move from N..N+3 to 1..4; outline-point deltas are dropped
    (they live in the Farsi glyph)."""
    for el in list(gvar.findall("glyphVariations")):
        n = simple_points.get(el.get("glyph"))
        if n is None:
            continue
        for tup in list(el.findall("tuple")):
            for d in list(tup.findall("delta")):
                pt = int(d.get("pt"))
                if pt >= n:
                    d.set("pt", str(pt - n + 1))
                else:
                    tup.remove(d)
            if not tup.findall("delta"):
                el.remove(tup)
        if not el.findall("tuple"):
            gvar.remove(el)


def process_sbix(sbix, dst_to_src):
    """Latin glyph = 'dupe' (reference) of the Farsi glyph's bitmap."""
    n = 0
    for strike in sbix.iter("strike"):
        ents = {g.get("name"): g for g in strike.findall("glyph")}
        for dst, src in dst_to_src.items():
            s, d = ents.get(src), ents.get(dst)
            if s is None and d is None:
                continue
            if s is None:
                strike.remove(d)
                continue
            gt = s.get("graphicType")
            if gt is None or gt in ("dupe", "flip"):    # empty or already a reference
                new = copy.deepcopy(s)
                new.set("name", dst)
            else:
                new = ET.Element("glyph", graphicType="dupe", name=dst,
                                 originOffsetX=s.get("originOffsetX", "0"),
                                 originOffsetY=s.get("originOffsetY", "0"))
                ET.SubElement(new, "ref", glyphname=src)
            if d is not None:
                strike[list(strike).index(d)] = new
            else:
                strike.append(new)
            n += 1
    return n


def shape_is_target(glyphs, name, target, seen=()):
    """True if glyph `name` is nothing but `target` (a single component at 0,0,
    possibly through a chain of such glyphs) - i.e. the shape is identical."""
    g = glyphs.get(name)
    if g is None or name in seen or g.find("contour") is not None:
        return False
    comps = g.findall("component")
    if len(comps) != 1:
        return False
    c = comps[0]
    if not is_plain_translation(c) or int(c.get("x", "0")) or int(c.get("y", "0")):
        return False
    n = c.get("glyphName")
    return n == target or shape_is_target(glyphs, n, target, seen + (name,))


def uses_glyph(glyphs, name, target, seen=()):
    """True if glyph `name` references `target` anywhere in its component tree."""
    g = glyphs.get(name)
    if g is None or name in seen:
        return False
    for c in g.findall("component"):
        n = c.get("glyphName")
        if n == target or uses_glyph(glyphs, n, target, seen + (name,)):
            return True
    return False


def process_clips(colr, dst_to_src, src_to_dsts):
    """COLRv1 ClipList: make Latin glyphs share the Farsi glyph's clip box."""
    for clip in list(colr.iter("Clip")):
        for g in clip.findall("Glyph"):
            if g.get("value") in dst_to_src:
                clip.remove(g)
        for g in clip.findall("Glyph"):
            for d in src_to_dsts.get(g.get("value"), []):
                pos = list(clip).index(g)
                clip.insert(pos + 1, ET.Element("Glyph", value=d))
        if not clip.findall("Glyph"):
            for parent in colr.iter():
                if clip in list(parent):
                    parent.remove(clip)
                    break


# ----------------------------------------------------------------------------
# Kerning
# ----------------------------------------------------------------------------
def _pairpos_format1(pp, cov, dst_to_src, src_to_dsts, order):
    had = False
    glyphs = [g.get("value") for g in cov.findall("Glyph")]
    psets = pp.findall("PairSet")
    entries = dict(zip(glyphs, psets))
    had |= any(s in entries for s in src_to_dsts)

    # (1) as SECOND glyph: drop Latin digits, duplicate Farsi digits' records
    for ps in psets:
        recs = ps.findall("PairValueRecord")
        for r in recs:
            ps.remove(r)
        new = []
        for r in recs:
            sec = r.find("SecondGlyph").get("value")
            if sec in dst_to_src:
                continue
            new.append(r)
            for d in src_to_dsts.get(sec, []):
                had = True
                c = copy.deepcopy(r)
                c.find("SecondGlyph").set("value", d)
                new.append(c)
        new.sort(key=lambda r: order.get(r.find("SecondGlyph").get("value"), BIG))
        for n, r in enumerate(new):
            r.set("index", str(n))
            ps.append(r)

    # (2) as FIRST glyph: Latin digit gets a copy of the Farsi digit's PairSet
    final = {g: ps for g, ps in entries.items() if g not in dst_to_src}
    for d, s in dst_to_src.items():
        if s in entries:
            final[d] = copy.deepcopy(entries[s])
    final = {g: ps for g, ps in final.items() if ps.findall("PairValueRecord")}

    for g in cov.findall("Glyph"):
        cov.remove(g)
    for ps in psets:
        pp.remove(ps)
    for n, g in enumerate(sorted(final, key=lambda x: order.get(x, BIG))):
        final[g].set("index", str(n))
        ET.SubElement(cov, "Glyph", value=g)
        pp.append(final[g])
    return had


def _pairpos_format2(pp, cov, dst_to_src, src_to_dsts, order):
    glyphs = [g.get("value") for g in cov.findall("Glyph")]
    had = any(s in glyphs for s in src_to_dsts)
    new_cov = [g for g in glyphs if g not in dst_to_src]
    new_cov += [d for d, s in dst_to_src.items() if s in glyphs]
    for g in cov.findall("Glyph"):
        cov.remove(g)
    for g in sorted(set(new_cov), key=lambda x: order.get(x, BIG)):
        ET.SubElement(cov, "Glyph", value=g)

    for tag in ("ClassDef1", "ClassDef2"):
        cd = pp.find(tag)
        if cd is None:
            continue
        ents = {e.get("glyph"): e for e in cd.findall("ClassDef")}
        had |= any(s in ents for s in src_to_dsts)
        for e in ents.values():
            cd.remove(e)
        final = {g: e for g, e in ents.items() if g not in dst_to_src}
        for d, s in dst_to_src.items():
            if s in ents:
                c = copy.deepcopy(ents[s])
                c.set("glyph", d)
                final[d] = c
        for g in sorted(final, key=lambda x: order.get(x, BIG)):
            cd.append(final[g])
    return had


def process_gpos(gpos, dst_to_src, src_to_dsts, order):
    had = False
    for pp in list(gpos.iter("PairPos")):
        cov = pp.find("Coverage")
        if cov is None:
            continue
        if pp.get("Format") == "1":
            had |= _pairpos_format1(pp, cov, dst_to_src, src_to_dsts, order)
        elif pp.get("Format") == "2":
            had |= _pairpos_format2(pp, cov, dst_to_src, src_to_dsts, order)
    return had


def process_kern_table(kern, dst_to_src, src_to_dsts, order):
    had = False
    for sub in kern.iter("kernsubtable"):
        pairs = sub.findall("pair")
        for p in pairs:
            sub.remove(p)
        out = []
        for p in pairs:
            l, r = p.get("l"), p.get("r")
            if l in dst_to_src or r in dst_to_src:
                continue
            out.append(p)
            for ll in [l] + src_to_dsts.get(l, []):
                for rr in [r] + src_to_dsts.get(r, []):
                    if (ll, rr) == (l, r):
                        continue
                    had = True
                    c = copy.deepcopy(p)
                    c.set("l", ll)
                    c.set("r", rr)
                    out.append(c)
        out.sort(key=lambda p: (order.get(p.get("l"), BIG), order.get(p.get("r"), BIG)))
        for p in out:
            sub.append(p)
    return had


# ----------------------------------------------------------------------------
# Names (find & replace)
# ----------------------------------------------------------------------------
def set_text(el, new):
    m = re.match(r"(\s*)(.*?)(\s*)$", el.text or "", re.S)
    el.text = m.group(1) + new + m.group(3)


def insert_suffix(value, suffix):
    """Fallback for file names: put the suffix before the last hyphen part
    (the style):  Font-DS2-Regular -> Font-DS2-FD-Regular"""
    core = re.sub(r"\s+", "", suffix.strip().lstrip("-_ "))
    fam, sep, style = value.rpartition("-")
    if not sep:
        return value + "-" + core
    return fam + "-" + core + "-" + style


def _key(s):
    """Compare names ignoring case, spaces, hyphens and underscores."""
    return re.sub(r"[\s\-_]+", "", s).lower()


def split_family(value, family, glued_ok=False):
    """If `value` starts with `family` (ignoring case, spaces, hyphens and
    underscores) return (prefix, rest), else None.  The rest has to start with a
    separator (or be empty) unless glued_ok - PostScript names such as
    AzarMehr-DS2ExtraBlack have the style glued to the family."""
    target = _key(family)
    if not target:
        return None
    got, i = "", 0
    while i < len(value) and len(got) < len(target):
        if not re.match(r"[\s\-_]", value[i]):
            got += value[i].lower()
        i += 1
    if got != target:
        return None
    rest = value[i:]
    if rest and not glued_ok and not re.match(r"[\s\-_]", rest[0]):
        return None
    return value[:i], rest


def _strip_tail(value, tail):
    """Remove the style `tail` from the end of `value` (ignoring separators)."""
    n, i = len(_key(tail)), len(value)
    while i > 0 and n > 0:
        i -= 1
        if not re.match(r"[\s\-_]", value[i]):
            n -= 1
    return value[:i].rstrip(" -_")


class NamePlan:
    """How the names of a font change.  The suffix goes after the FAMILY name,
    before the style (weight) name, which is never touched:

        family     AzarMehr-DS2            ->  AzarMehr-DS2-FD
        full name  AzarMehr-DS2 ExtraBlack ->  AzarMehr-DS2-FD ExtraBlack
        PostScript AzarMehr-DS2ExtraBlack  ->  AzarMehr-DS2-FD-ExtraBlack

    The family comes from the name table (ID 16, else ID 1), not from the
    position of a hyphen.  In display names the suffix is used as typed
    (--suffix=-FD -> "-FD"; a suffix that does not start with - _ or a space
    gets a space in front); PostScript names always get "-FD"."""

    def __init__(self, names, suffix):
        s = suffix.rstrip()
        self.core = s.lstrip("-_ \t").strip()
        if not self.core:
            sys.exit("Suffix must not be empty.")
        self.ps_core = re.sub(r"\s+", "", self.core)
        self.display = s if s[:1] in ("-", "_", " ") else " " + s
        self.warnings = []

        def g(i):
            return (names.get(i) or "").strip() or None

        self.fam_old = g(16) or g(1)
        self.ps_old = g(6)
        self.styles = [x for x in (g(17),) if x]
        # no ID 16: ID 1 may contain the style ("Font Light") - take it off
        if not g(16) and self.fam_old and self.ps_old and "-" in self.ps_old:
            hint = self.ps_old.rpartition("-")[2]
            if (_key(hint) not in ("regular", "bold", "italic", "bolditalic")
                    and _key(self.fam_old).endswith(_key(hint))):
                self.fam_old = _strip_tail(self.fam_old, hint)
        self.fam_new = self.fam_old + self.display if self.fam_old else None

        self.fam_ps, self.style_ps, self.ps_new = None, "", None
        if self.ps_old:
            m = split_family(self.ps_old, self.fam_old, glued_ok=True) if self.fam_old else None
            if m:
                self.fam_ps, rest = m[0].rstrip("-_ "), m[1].lstrip("-_ ")
            elif "-" in self.ps_old:
                self.fam_ps, _, rest = self.ps_old.rpartition("-")
            else:
                self.fam_ps, rest = self.ps_old, ""
            self.style_ps = rest
            self.ps_new = self.fam_ps + "-" + self.ps_core + ("-" + rest if rest else "")

    def style_name(self):
        return self.style_ps or (self.styles[0] if self.styles else "")

    def swap_family(self, value, nid=None):
        """Insert the suffix after the family part of a display name."""
        if self.fam_old:
            m = split_family(value, self.fam_old)
            if m:
                return self.fam_new + m[1]
        for st in self.styles + ([self.style_ps] if self.style_ps else []):
            if st and value.endswith(st) and len(value) > len(st):
                return value[:-len(st)].rstrip(" -_") + self.display + " " + st
        self.warnings.append("name ID %s: family not found in '%s'; the suffix was "
                             "appended at the end" % (nid if nid is not None else "?", value))
        return value + self.display

    def ps_swap(self, value):
        """PostScript-like names (fvar instances): suffix after the family."""
        if self.fam_ps and value.startswith(self.fam_ps):
            rest = value[len(self.fam_ps):].lstrip("-_ ")
            return self.fam_ps + "-" + self.ps_core + ("-" + rest if rest else "")
        return None

    def name_record(self, nid, value):
        if nid in (1, 4, 16, 21):
            return self.swap_family(value, nid)
        if nid == 6 and self.ps_new:
            return self.ps_new
        if nid == 3:                      # unique ID, usually "version;vendor;PostScript name"
            if self.ps_old and self.ps_old in value:
                return value.replace(self.ps_old, self.ps_new)
            head, sep, tail = value.rpartition(";")
            swapped = self.ps_swap(tail)
            if swapped:
                return head + sep + swapped
            return value + ";" + self.ps_core
        if nid == 25:
            return value + self.ps_core
        if nid >= 256 and " " not in value:
            return self.ps_swap(value) or value
        return value                      # 2, 17 (style / weight) etc.: untouched


class Renamer:
    def __init__(self, root, suffix):
        recs = list(root.iter("namerecord"))
        names = {}
        for windows_only in (True, False):          # Windows English first
            for r in recs:
                nid, txt = int(r.get("nameID")), (r.text or "").strip()
                if not txt or nid in names:
                    continue
                if windows_only and (r.get("platformID"), r.get("platEncID"),
                                     r.get("langID")) != ("3", "1", "0x409"):
                    continue
                names[nid] = txt
        self.plan = NamePlan(names, suffix)

    @property
    def ps_new(self):
        return self.plan.ps_new

    @property
    def warnings(self):
        return self.plan.warnings

    def apply(self, root):
        n = 0
        for r in root.iter("namerecord"):
            if not (r.text and r.text.strip()):
                continue
            nid = int(r.get("nameID"))
            old = r.text.strip()
            new = self.plan.name_record(nid, old)
            if new != old:
                set_text(r, new)
                n += 1
        # CFF top dict names
        for cff in root.iter("CFFFont"):
            if cff.get("name") and self.plan.ps_new:
                cff.set("name", self.plan.ps_new)
            for tag in ("FullName", "FamilyName"):
                el = cff.find(tag)
                if el is not None and el.get("value"):
                    el.set("value", self.plan.swap_family(el.get("value")))
        return n


def planned_stem(path, suffix):
    """File name (without extension) the converted font will get: its new
    PostScript name.  Used to detect clashes before converting."""
    stem = os.path.splitext(os.path.basename(path))[0]
    try:
        f = TTFont(path, lazy=True)
        names = {i: f["name"].getDebugName(i) for i in (1, 3, 4, 6, 16, 17)}
        f.close()
        ps = NamePlan(names, suffix).ps_new
        if ps:
            return ps
    except Exception:
        pass
    return insert_suffix(stem, suffix)


# ----------------------------------------------------------------------------
def apply_cmap_mode(root, tables, cmap, sources, targets):
    """cmap method: point the cmap entries of the target digits (Latin and,
    with --arabic, Arabic-Indic) straight at the matching Farsi glyphs.
    Nothing else in the font is touched; the old digit glyphs stay unused."""
    glyf = tables.get("glyf")
    glyphs = {g.get("name"): g for g in glyf.findall("TTGlyph")} if glyf is not None else {}
    code_src = {}
    for label, base in targets:
        for i in range(10):
            code, per = base + i, sources[i]
            dst = cmap.get(code)
            if dst is None:
                print("  note: U+%04X (%s digit) is not in the cmap; skipped" % (code, label))
            elif dst == per:
                print("  note: U+%04X already uses glyph '%s'" % (code, per))
            elif shape_is_target(glyphs, per, dst):
                print("  note: '%s' is already a component of '%s' (same shape); "
                      "U+%04X skipped" % (per, dst, code))
            else:
                code_src[code] = per
    changed = 0
    for sub in root.find("cmap"):
        if not sub.tag.startswith("cmap_format_"):
            continue
        for m in sub.iter("map"):
            code = m.get("code")
            if code is not None and int(code, 16) in code_src:
                new = code_src[int(code, 16)]
                if m.get("name") != new:
                    m.set("name", new)
                    changed += 1
    print("cmap: %d mappings now point at the Farsi glyphs." % changed)
    if not changed:
        sys.exit("Nothing to do.")


FONT_EXTS = (".ttf", ".otf", ".woff", ".woff2")


def convert_font(src_path, args, output=None, out_dir=None):
    """Convert one font. `output` = explicit output file, `out_dir` = output
    folder; with neither, the result is written next to the input."""
    src_path = os.path.abspath(src_path)
    in_dir = os.path.dirname(src_path)
    stem, ext = os.path.splitext(os.path.basename(src_path))
    ext = ext.lower()

    tmp = tempfile.TemporaryDirectory()

    # 1) font -> TTX ----------------------------------------------------------
    if ext == ".ttx":
        ttx_in = src_path
    else:
        ttx_in = os.path.join(tmp.name, "in.ttx")
        font = TTFont(src_path)
        font.saveXML(ttx_in)
        font.close()
        print("Converted to TTX.")

    tree = ET.parse(ttx_in)
    root = tree.getroot()
    tables = {t.tag.strip(): t for t in root}
    order = read_glyph_order(root)
    cmap = read_cmap(root)

    # 2) Farsi digit glyph -> Latin digit glyph ----------------------------
    targets = [("Latin", LATIN_BASE)]
    if args.arabic:
        targets.append(("Arabic-Indic", ARABIC_BASE))
    print("Source digits: U+%04X..U+%04X (Farsi) -> %s" % (
        FARSI_BASE, FARSI_BASE + 9, " + ".join(
            "%s U+%04X..U+%04X" % (n, b, b + 9) for n, b in targets)))
    sources = {}
    for i in range(10):
        per = cmap.get(FARSI_BASE + i)
        if per is None:
            sys.exit("Missing cmap entry for U+%04X" % (FARSI_BASE + i))
        sources[i] = per
    if args.cmap:
        print("Method: cmap (digits point directly at the Farsi glyphs)")
        apply_cmap_mode(root, tables, cmap, sources, targets)
    else:
        farsi_glyphs = set(sources.values())
        dst_to_src = {}
        for label, base in targets:
            for i in range(10):
                dst, per = cmap.get(base + i), sources[i]
                if dst is None:
                    sys.exit("Missing cmap entry for U+%04X (%s digit)" % (base + i, label))
                if dst == per:
                    print("  note: U+%04X and U+%04X already share glyph '%s'" %
                          (base + i, FARSI_BASE + i, dst))
                    continue
                if dst in farsi_glyphs:
                    print("  note: glyph '%s' (U+%04X) is a Farsi digit glyph of another "
                          "digit; skipped" % (dst, base + i))
                    continue
                if dst_to_src.setdefault(dst, per) != per:
                    print("  WARNING: glyph '%s' is shared by digits needing different "
                          "shapes; keeping the first" % dst)
        # A Farsi glyph that is itself just a component of the target glyph has
        # the same shape already: nothing to do (and copying would make a loop).
        glyf = tables.get("glyf")
        if glyf is not None:
            glyphs = {g.get("name"): g for g in glyf.findall("TTGlyph")}
            for dst, src in list(dst_to_src.items()):
                if shape_is_target(glyphs, src, dst):
                    print("  note: '%s' is already a component of '%s' (same shape); "
                          "skipped" % (src, dst))
                    del dst_to_src[dst]
                elif uses_glyph(glyphs, src, dst):
                    print("  WARNING: '%s' uses '%s' as a (transformed/partial) component; "
                          "'%s' left unchanged to avoid a loop." % (src, dst, dst))
                    del dst_to_src[dst]
        if not dst_to_src:
            sys.exit("Nothing to do.")
        src_to_dsts = {}
        for d, s_ in dst_to_src.items():
            src_to_dsts.setdefault(s_, []).append(d)

        # which strategy for outlines / bitmaps?
        color = [t for t in COLOR_TABLES if t in tables]
        copy_mode = args.mode == "copy"
        print("Method: %s" % args.mode)
        comp_glyf = (glyf is not None and not copy_mode and not color)
        dupe_sbix = ("sbix" in tables and not copy_mode)
        if glyf is not None and not comp_glyf:
            print("Outlines: full copy (%s)." % (
                "--mode copy" if copy_mode else
                "colour tables present, components not used: " + ", ".join(color)))
        simple_points = {}

        print("Copying glyph data:")
        for tag, specs in GLYPH_TABLES.items():
            table = tables.get(tag)
            if table is None:
                continue
            if tag == "glyf" and comp_glyf:
                st, simple_points = build_component_glyphs(glyf, dst_to_src, "gvar" in tables)
                print("  glyf  components of the source glyph: %d, copied components: %d, "
                      "flattened: %d" % (st["component"], st["verbatim"], st["flattened"]))
                if st["nested_kept"]:
                    print("  WARNING: %d glyph(s) keep nested components (variable font, "
                          "hinting instructions or transformed components)." % st["nested_kept"])
                continue
            if tag == "sbix" and dupe_sbix:
                print("  sbix  %d entries (dupe references)" % process_sbix(table, dst_to_src))
                continue
            total = sum(sync_entries(table, sp, dst_to_src, order) for sp in specs)
            if tag == "gvar" and simple_points:
                gvar_for_components(table, simple_points)
            if tag == "COLR":
                process_clips(table, dst_to_src, src_to_dsts)
            print("  %-5s %d entries" % (tag, total))
        if "HVAR" in tables and tables["HVAR"].find("AdvWidthMap") is None:
            print("  WARNING: HVAR has no AdvWidthMap; advance variations of the "
                  "Latin digits could not be copied.")
        for tag in UNSUPPORTED:
            if tag in tables:
                print("  WARNING: table %s present - digit data in it is NOT copied." % tag)

        # 3) kerning ---------------------------------------------------------------
        had = False
        if "GPOS" in tables:
            had |= process_gpos(tables["GPOS"], dst_to_src, src_to_dsts, order)
        if "kern" in tables:
            had |= process_kern_table(tables["kern"], dst_to_src, src_to_dsts, order)
        if "GPOS" in tables or "kern" in tables:
            print("Kerning: Farsi digits had kerning -> copied to the target digits."
                  if had else
                  "Kerning: Farsi digits had no kerning -> target digit kerning removed.")

    # 4) names -----------------------------------------------------------------
    if args.suffix:
        renamer = Renamer(root, args.suffix)
        n = renamer.apply(root)
        style = renamer.plan.style_name()
        print("Renamed %d name records%s." % (n, (" (style / weight name '%s' unchanged)" % style) if style else ""))
        for w in renamer.warnings:
            print("  WARNING:", w)
        new_stem = renamer.ps_new or insert_suffix(stem, args.suffix)
    else:
        new_stem = stem

    # 5) write TTX, compile --------------------------------------------------------
    if output:
        out_path = os.path.abspath(output)
    else:
        out_ext = ext
        if ext == ".ttx":
            out_ext = ".otf" if root.get("sfntVersion") == "OTTO" else ".ttf"
        out_path = os.path.join(out_dir or in_dir, new_stem + out_ext)
    if out_path == src_path:
        sys.exit("The output would overwrite the input; use --suffix or --output.")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    if args.keep_ttx:
        ttx_out = os.path.splitext(out_path)[0] + ".ttx"
    else:
        ttx_out = os.path.join(tmp.name, "out.ttx")
    tree.write(ttx_out, encoding="utf-8", xml_declaration=True)

    out_font = TTFont()
    out_font.importXML(ttx_out)
    flavor = {".woff": "woff", ".woff2": "woff2"}.get(os.path.splitext(out_path)[1].lower())
    out_font.flavor = flavor
    out_font.save(out_path)
    out_font.close()
    tmp.cleanup()
    print("Saved:", out_path)
    if ext != ".ttx":
        print("Size: %d -> %d bytes" % (os.path.getsize(src_path), os.path.getsize(out_path)))
    if args.keep_ttx:
        print("Saved:", ttx_out)
    return out_path


def _norm(path):
    return os.path.normcase(os.path.abspath(path))


def collect_fonts(folder, recursive, exclude=(), exclude_names=()):
    """Fonts in `folder` (and its sub-folders with recursive=True), without
    descending into the folders listed in `exclude` or into any folder whose
    name is in `exclude_names` (the result folders of an earlier run)."""
    found, skipped = [], []
    exclude = {_norm(e) for e in exclude}
    exclude_names = {os.path.normcase(n) for n in exclude_names}
    if recursive:
        walker = os.walk(folder)
    else:
        walker = [(folder, [], sorted(os.listdir(folder)))]
    for dirpath, dirnames, filenames in walker:
        dirnames[:] = sorted(d for d in dirnames
                             if _norm(os.path.join(dirpath, d)) not in exclude
                             and os.path.normcase(d) not in exclude_names)
        for fn in sorted(filenames):
            full = os.path.join(dirpath, fn)
            ext = os.path.splitext(fn)[1].lower()
            if ext in FONT_EXTS:
                found.append(full)
            elif ext in (".ttc", ".otc"):
                skipped.append(full)
    return found, skipped


def main():
    ap = argparse.ArgumentParser(
        description="Make the Latin digits (0-9) of a font look like the Farsi "
                    "digits (U+06F0-06F9), and rename the font with a suffix.")
    ap.add_argument("path", help="a font file (.ttf .otf .woff .woff2 .ttx) or a folder; "
                                 "for a folder every font in it is converted")
    ap.add_argument("-s", "--suffix", required=True,
                    help="suffix added after the family name, e.g. --suffix=-FD (always "
                         "required: the new font must not share the name of the old one). "
                         "Used as typed in the family/full names; the style name is "
                         "never changed")
    ap.add_argument("-m", "--mode", choices=("component", "copy"),
                    help="how the digits are made: 'component' = Latin glyph references "
                         "the Farsi glyph (sbix: dupe), 'copy' = outlines/bitmaps are "
                         "duplicated (required, except with --cmap)")
    ap.add_argument("--cmap", action="store_true",
                    help="point the cmap entries of the digits directly at the Farsi "
                         "glyphs; then --mode is not needed (--suffix still is)")
    ap.add_argument("-o", "--output",
                    help="output font file (single input) or output folder (folder input); "
                         "default: next to the input")
    ap.add_argument("-r", "--recursive", action="store_true",
                    help="folder input: also search sub-folders")
    ap.add_argument("--collect", choices=("per-folder", "single", "none"),
                    help="folder input (required, no default): where the results go. "
                         "per-folder = in every folder with more than one font, into a "
                         "sub-folder next to the originals (the folder structure stays); "
                         "single = all results of the run together in one folder; "
                         "none = next to the originals, no extra folder")
    ap.add_argument("--collect-folder", metavar="NAME",
                    help="name of the folder used by --collect per-folder / single "
                         "(required for those two, no default)")
    ap.add_argument("--keep-ttx", action="store_true",
                    help="keep the modified .ttx next to the output font")
    ap.add_argument("--arabic", action="store_true",
                    help="also apply the Farsi digits to the Arabic-Indic digits "
                         "(U+0660-0669), in addition to the Latin digits (off by default)")
    ap.add_argument("--version", action="version", version="Digits2Fa " + __version__)
    args = ap.parse_args()

    if args.collect_folder is not None:
        name = args.collect_folder
        if not name.strip() or name in (".", "..") or any(c in name for c in '/\\:*?"<>|'):
            ap.error("--collect-folder must be a plain folder name (no path separators "
                     "or special characters)")

    if args.cmap:
        if args.mode:
            ap.error("--mode cannot be combined with --cmap")
    elif not args.mode:
        ap.error("--mode component|copy is required (or use --cmap)")

    path = os.path.abspath(args.path)
    if not os.path.exists(path):
        sys.exit("Path not found: %s" % args.path)

    if os.path.isfile(path):
        convert_font(path, args, output=args.output)
        return

    # ---- folder mode ---------------------------------------------------------
    if args.output and os.path.splitext(args.output)[1].lower() in FONT_EXTS + (".ttx",):
        sys.exit("For a folder input, --output must be a folder, not a file.")
    # ---- folder mode: --collect decides where the results go ---------------------
    mode = args.collect
    if not mode:
        ap.error("--collect per-folder|single|none is required for a folder input")
    if mode == "none" and args.collect_folder:
        ap.error("--collect-folder cannot be used with --collect none")
    if mode != "none" and not args.collect_folder:
        ap.error("--collect %s needs --collect-folder NAME" % mode)
    name = args.collect_folder

    core = args.suffix.lstrip("-_ ")
    out_root = os.path.abspath(args.output) if args.output else path
    exclude = [os.path.abspath(args.output)] if args.output else []
    exclude_names = []
    if mode == "per-folder":
        exclude_names.append(name)
    elif mode == "single":
        exclude.append(os.path.join(out_root, name))
    fonts, unsupported = collect_fonts(path, args.recursive, exclude, exclude_names)
    for u in unsupported:
        print("Skipped (font collections are not supported): %s" % u)

    todo, skipped = [], []
    for f in fonts:
        stem = os.path.splitext(os.path.basename(f))[0]
        if core in re.split(r"[-_ ]", stem):
            print("Skipped (already has the suffix): %s" % f)
            skipped.append(f)
        else:
            todo.append(f)

    per_dir = {}
    for f in todo:
        per_dir.setdefault(os.path.dirname(f), []).append(f)
    collected = []

    # single: one folder for the whole run (only if more than one font)
    single_dir, flat = None, True
    if mode == "single" and len(todo) > 1:
        single_dir = os.path.join(out_root, name)
        names = [(planned_stem(f, args.suffix) + os.path.splitext(f)[1]).lower() for f in todo]
        flat = len(set(names)) == len(names)
        collected.append(single_dir)
        print("Collecting %d fonts into: %s" % (len(todo), single_dir))
        if not flat:
            print("  note: some fonts would get the same file name; the sub-folder "
                  "structure is kept inside the collect folder.")

    done, failed = [], []
    for f in todo:
        d = os.path.dirname(f)
        rel_dir = os.path.relpath(d, path)
        base = os.path.normpath(os.path.join(out_root, rel_dir)) if args.output else None
        if mode == "per-folder" and len(per_dir[d]) > 1:
            out_dir = os.path.join(base or d, name)
            if out_dir not in collected:
                collected.append(out_dir)
                print("Collecting %d fonts of %s into: %s" % (len(per_dir[d]), d, out_dir))
        elif single_dir:
            out_dir = single_dir if flat else os.path.normpath(os.path.join(single_dir, rel_dir))
        else:
            out_dir = base
        print("\n=== %s ===" % os.path.relpath(f, path))
        try:
            convert_font(f, args, out_dir=out_dir)
            done.append(f)
        except (Exception, SystemExit) as e:        # keep going with the other fonts
            print("FAILED: %s" % (e if str(e) else type(e).__name__))
            failed.append(f)
    print("\nDone: %d converted, %d failed, %d skipped." %
          (len(done), len(failed), len(skipped)))
    for f in failed:
        print("  failed:", f)
    for c in collected:
        print("Results folder: %s" % c)
    if not fonts:
        print("No font files found in %s%s." % (path, "" if args.recursive
              else " (use --recursive to search sub-folders)"))
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
