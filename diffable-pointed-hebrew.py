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
        cpns, olines = _make_lines_of_words(ifp)
    scpns = _sorted_cpns(cpns)
    outstruc = dict(code_point_names=scpns, lines=olines)
    file_io.json_dump_to_file_path(outstruc, args.output_filename)


def _sorted_cpns(cpns):
    return [(k,) + cpns[k] for k in sorted(cpns.keys())]


def _make_lines_of_words(ifp):
    cpns = {}  # code point names
    olines = []
    for iline in ifp:
        iwords = iline.replace("\n", "").split(" ")
        owords = [_comma_join_shortened_unicode_names(cpns, w) for w in iwords]
        olines.append(owords)
    return cpns, olines


def _name_record(char):
    fullname = unicodedata.name(char, None)
    sname = uni_heb.shunna(char)
    return ord(char), sname, fullname


def _comma_join_shortened_unicode_names(io_cpns, chars):
    name_recs = list(map(_name_record, chars))
    for nr in name_recs:
        io_cpns[nr[0]] = nr[1:]
    return ",".join(nr[1] for nr in name_recs)


if __name__ == "__main__":
    main()
