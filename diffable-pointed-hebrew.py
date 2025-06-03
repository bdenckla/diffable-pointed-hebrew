import argparse
import unicodedata
import os
import json
import pathlib
import pycmn.uni_heb as uni_heb


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_filename")
    parser.add_argument("output_filename")
    args = parser.parse_args()
    with open(args.input_filename, encoding="utf-8") as ifp:
        cpns = {}  # code point names
        olines = _make_lines_of_words(cpns, ifp)
    scpns = _sorted_cpns(cpns)
    outstruc = dict(code_point_names=scpns, lines=olines)
    with_tmp_openw(args.output_filename, lambda ofp: _dump(ofp, outstruc))


def _sorted_cpns(cpns):
    return [(k,) + cpns[k] for k in sorted(cpns.keys())]


def _make_lines_of_words(cpns, ifp):
    olines = []
    for iline in ifp:
        iwords = iline.replace("\n", "").split(" ")
        owords = [comma_join_shortened_unicode_names(cpns, w) for w in iwords]
        olines.append(owords)
    return olines


def _dump(ofp, json_dumpable_structure):
    json.dump(json_dumpable_structure, ofp, indent=0, ensure_ascii=False)
    ofp.write("\n")


def openw(pathobj, **kwargs):
    os.makedirs(pathobj.parent, exist_ok=True)
    return open(pathobj, "w", encoding="utf-8", **kwargs)


def tmp_path(path):
    pathobj = pathlib.Path(path)
    # e.g. from /dfoo/dbar/stem.ext return /dfoo/dbar/stem.tmp.ext
    # where suffix = .ext
    return pathobj.parent / (str(pathobj.stem) + ".tmp" + pathobj.suffix)


def with_tmp_openw(path, callback, **kwargs):
    tpath = tmp_path(path)
    with openw(tpath, **kwargs) as outfp:
        retval = callback(outfp)
    os.replace(tpath, path)
    return retval


_SHORTEN_DIC = {
    ("HEBREW", "LETTER"): "HLE",
    ("HEBREW", "POINT"): "HPO",
    ("HEBREW", "ACCENT"): "HAC",
    ("HEBREW", "PUNCTUATION"): "HPU",
    ("HEBREW", "MARK"): "HMA",
}
_MISC_UNI_NAME_SHORTENINGS = {
    "\N{COMBINING GRAPHEME JOINER}": "CGJ",
}


def shortened_unicode_name(char, fullname):
    if nonhe := uni_heb.he_char_name_q(char):
        return nonhe
    if muns := _MISC_UNI_NAME_SHORTENINGS.get(char):
        return muns
    if not fullname:
        return str(ord(char))
    whstrs = fullname.split()
    if len(whstrs) < 3:
        return None
    if sd := _SHORTEN_DIC.get((whstrs[0], whstrs[1])):
        return sd + " " + " ".join(whstrs[2:])
    return None


def _name_record(char):
    fullname = unicodedata.name(char, None)
    sname = shortened_unicode_name(char, fullname)
    return ord(char), sname, fullname


def comma_join_shortened_unicode_names(cpns, chars):
    name_recs = list(map(_name_record, chars))
    for nr in name_recs:
        cpns[nr[0]] = nr[1:]
    return ",".join(nr[1] or nr[2] for nr in name_recs)


if __name__ == "__main__":
    main()
