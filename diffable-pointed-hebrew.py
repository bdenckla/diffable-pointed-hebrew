import argparse
import unicodedata
import pycmn.uni_heb as uni_heb
import pycmn.file_io as file_io


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
    file_io.json_dump_to_file_path(outstruc, args.output_filename)


def _sorted_cpns(cpns):
    return [(k,) + cpns[k] for k in sorted(cpns.keys())]


def _make_lines_of_words(cpns, ifp):
    olines = []
    for iline in ifp:
        iwords = iline.replace("\n", "").split(" ")
        owords = [_comma_join_shortened_unicode_names(cpns, w) for w in iwords]
        olines.append(owords)
    return olines


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


def _shortened_unicode_name(char, fullname):
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
    sname = _shortened_unicode_name(char, fullname)
    return ord(char), sname, fullname


def _comma_join_shortened_unicode_names(cpns, chars):
    name_recs = list(map(_name_record, chars))
    for nr in name_recs:
        cpns[nr[0]] = nr[1:]
    return ",".join(nr[1] or nr[2] for nr in name_recs)


if __name__ == "__main__":
    main()
