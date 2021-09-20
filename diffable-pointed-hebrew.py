import argparse
import unicodedata
import os
import json
import pathlib

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_filename')
    parser.add_argument('output_filename')
    args = parser.parse_args()
    with open(args.input_filename, encoding='utf-8') as ifp:
        olines = _make_lines_of_words(ifp)
    with_tmp_openw(args.output_filename, lambda ofp: _dump(ofp, olines))


def _make_lines_of_words(ifp):
    olines = []
    for iline in ifp:
        iwords = iline.split(' ')
        owords = list(map(comma_join_shortened_unicode_names, iwords))
        olines.append(owords)
    return olines


def _dump(ofp, json_dumpable_structure):
    json.dump(json_dumpable_structure, ofp, indent=0, ensure_ascii=False)
    ofp.write('\n')
    

def openw(pathobj, **kwargs):
    os.makedirs(pathobj.parent, exist_ok=True)
    return open(pathobj, 'w', encoding='utf-8', **kwargs)


def tmp_path(path):
    pathobj = pathlib.Path(path)
    # e.g. from /dfoo/dbar/stem.ext return /dfoo/dbar/stem.tmp.ext
    # where suffix = .ext
    return pathobj.parent / (str(pathobj.stem) + '.tmp' + pathobj.suffix)


def with_tmp_openw(path, callback, **kwargs):
    tpath = tmp_path(path)
    with openw(tpath, **kwargs) as outfp:
        retval = callback(outfp)
    os.replace(tpath, path)
    return retval

_SHORTEN_DIC = {
    ('HEBREW', 'LETTER'): 'HLE',
    ('HEBREW', 'POINT'): 'HPO',
    ('HEBREW', 'ACCENT'): 'HAC',
    ('HEBREW', 'PUNCTUATION'): 'HPU',
    ('HEBREW', 'MARK'): 'HMA',
}
_HE_AND_NONHE_LET_PAIRS = (
    ('\N{HEBREW LETTER ALEF}', 'α'),  # Greek alpha
    ('\N{HEBREW LETTER BET}', 'v'),  # v not b
    ('\N{HEBREW LETTER GIMEL}', 'g'),
    ('\N{HEBREW LETTER DALET}', 'd'),
    ('\N{HEBREW LETTER HE}', 'h'),
    ('\N{HEBREW LETTER VAV}', 'w'),
    ('\N{HEBREW LETTER ZAYIN}', 'z'),
    ('\N{HEBREW LETTER HET}', 'x'),
    ('\N{HEBREW LETTER TET}', 'θ'),  # See note on θ
    ('\N{HEBREW LETTER YOD}', 'y'),
    ('\N{HEBREW LETTER FINAL KAF}', 'k.'),
    ('\N{HEBREW LETTER KAF}', 'k'),
    ('\N{HEBREW LETTER LAMED}', 'l'),
    ('\N{HEBREW LETTER FINAL MEM}', 'm.'),
    ('\N{HEBREW LETTER MEM}', 'm'),
    ('\N{HEBREW LETTER FINAL NUN}', 'n.'),
    ('\N{HEBREW LETTER NUN}', 'n'),
    ('\N{HEBREW LETTER SAMEKH}', 'σ'),  # Greek sigma
    ('\N{HEBREW LETTER AYIN}', 'ʕ'),  # PHARYNGEAL VOICED FRICATIVE
    ('\N{HEBREW LETTER FINAL PE}', 'f.'),  # f. not p.
    ('\N{HEBREW LETTER PE}', 'f'),  # f not p
    ('\N{HEBREW LETTER FINAL TSADI}', '⍭.'),
    ('\N{HEBREW LETTER TSADI}', '⍭'),
    ('\N{HEBREW LETTER QOF}', 'q'),
    ('\N{HEBREW LETTER RESH}', 'r'),
    ('\N{HEBREW LETTER SHIN}', '$'),
    ('\N{HEBREW LETTER TAV}', 'τ'),  # Greek tau
)
_HE_AND_NONHE_POINT_PAIRS = (
    ('\N{HEBREW POINT DAGESH OR MAPIQ}', '·'),
    ('\N{HEBREW POINT RAFE}', '‾'),  # r̄ was another candidate
    ('\N{HEBREW POINT SHIN DOT}', '·sh'),
    ('\N{HEBREW POINT SIN DOT}', '·si'),
    ('\N{HEBREW POINT SHEVA}', ':'),  # ambiguous, could be na or nach
    ('\N{HEBREW POINT HATAF SEGOL}', ':∵'),  # ∵ aka BECAUSE
    ('\N{HEBREW POINT HATAF PATAH}', ':_'),
    ('\N{HEBREW POINT HATAF QAMATS}', ':a'),
    ('\N{HEBREW POINT HIRIQ}', 'i'),
    ('\N{HEBREW POINT TSERE}', '‥'),
    ('\N{HEBREW POINT SEGOL}', '∵'),  # ∵ aka BECAUSE
    ('\N{HEBREW POINT PATAH}', '_'),
    ('\N{HEBREW POINT QAMATS}', 'a'),  # ambiguous, could be Tg or Tq
    ('\N{HEBREW POINT QAMATS QATAN}', 'oa'),
    ('\N{HEBREW POINT HOLAM HASER FOR VAV}', 'hhfv'),
    ('\N{HEBREW POINT HOLAM}', 'o'),  # see "Note on plain holam" below
    ('\N{HEBREW POINT QUBUTS}', 'u'),
)
_HE_AND_NONHE_ACC_PAIRS = (
    ('\N{HEBREW POINT METEG}', '𝓂'),  # we consider it an accent not a point
    ('\N{HEBREW ACCENT ETNAHTA}', '⅄'),
    ('\N{HEBREW ACCENT SEGOL}', '∴'),  # ∴ aka THEREFORE
    ('\N{HEBREW ACCENT SHALSHELET}', '[sh]'),
    ('\N{HEBREW ACCENT ZAQEF QATAN}', 'ƶ'),
    ('\N{HEBREW ACCENT ZAQEF GADOL}', 'Ƶ'),
    ('\N{HEBREW ACCENT TIPEHA}', '[ti]'),
    ('\N{HEBREW ACCENT REVIA}', '◆'),  # ◆ aka BLACK DIAMOND
    ('\N{HEBREW ACCENT ZARQA}', '≁'),  # See: Note on zinor
    ('\N{HEBREW ACCENT PASHTA}', '[p]'),
    ('\N{HEBREW ACCENT YETIV}', '[ye]'),
    ('\N{HEBREW ACCENT TEVIR}', '⟓'),
    ('\N{HEBREW ACCENT GERESH}', '[ge]'),
    ('\N{HEBREW ACCENT GERESH MUQDAM}', 'γ'),  # Greek small gamma
    ('\N{HEBREW ACCENT GERSHAYIM}', '[G]'),
    ('\N{HEBREW ACCENT QARNEY PARA}', '[qp]'),
    ('\N{HEBREW ACCENT TELISHA GEDOLA}', '⌕'),  # aka TELEPHONE RECORDER
    ('\N{HEBREW ACCENT PAZER}', 'μ'),  # Greek small mu
    ('\N{HEBREW ACCENT ATNAH HAFUKH}', '[ah]'),
    ('\N{HEBREW ACCENT MUNAH}', '⅃'),
    ('\N{HEBREW ACCENT MAHAPAKH}', '<'),
    ('\N{HEBREW ACCENT MERKHA}', '[me]'),
    ('\N{HEBREW ACCENT MERKHA KEFULA}', '[mk]'),
    ('\N{HEBREW ACCENT DARGA}', '[da]'),
    ('\N{HEBREW ACCENT QADMA}', '[qa]'),
    ('\N{HEBREW ACCENT TELISHA QETANA}', '[tq]'),
    ('\N{HEBREW ACCENT YERAH BEN YOMO}', '[yy]'),
    ('\N{HEBREW ACCENT OLE}', '[ol]'),
    ('\N{HEBREW ACCENT ILUY}', '[il]'),
    ('\N{HEBREW ACCENT DEHI}', '[de]'),
    ('\N{HEBREW ACCENT ZINOR}', '~'),  # See: Note on zinor
)
_MISC_UNI_NAME_SHORTENINGS = {
    '\N{COMBINING GRAPHEME JOINER}': 'CGJ',
}
_HE_AND_NONHE_PAIRS = (
    _HE_AND_NONHE_LET_PAIRS +
    _HE_AND_NONHE_POINT_PAIRS +
    _HE_AND_NONHE_ACC_PAIRS)


def _mk_he_to_nonhe_dic():
    nonhe_set = set()
    for _, nonhe in _HE_AND_NONHE_PAIRS:  # _ is he
        assert nonhe not in nonhe_set
        nonhe_set.add(nonhe)
    return dict(_HE_AND_NONHE_PAIRS)


_HE_TO_NONHE_DIC = _mk_he_to_nonhe_dic()


def _shorten(word1, word2):
    return _SHORTEN_DIC.get((word1, word2)) or word1 + ' ' + word2


def shortened_unicode_name(char):
    if nonhe := _HE_TO_NONHE_DIC.get(char):
        return nonhe
    if muns := _MISC_UNI_NAME_SHORTENINGS.get(char):
        return muns
    fullname = unicodedata.name(char, str(ord(char)))
    whstrs = fullname.split()
    if len(whstrs) < 3:
        return fullname
    return _shorten(whstrs[0], whstrs[1]) + ' ' + ' '.join(whstrs[2:])


def comma_join_shortened_unicode_names(pre_line):
    return ','.join(map(shortened_unicode_name, pre_line))


if __name__ == '__main__':
    main()
