"""Dev-time: find code that builds a given 32-bit address (lis + addi/ori) and strings in a DOL.

    python3 tools/dev/xref.py RS9E8P.dol str "RVL_SDK - KPAD"
    python3 tools/dev/xref.py RS9E8P.dol addr 0x803a1234
"""
import os, struct, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from dol import Dol

def text_words(d):
    for off, addr, size, i in d.secs:
        if i < 7:
            for k in range(0, size, 4):
                yield addr + k, struct.unpack('>I', d.data[off + k: off + k + 4])[0]

def xrefs(d, target):
    hi, lo = (target >> 16) & 0xFFFF, target & 0xFFFF
    hi_adj = (hi + (1 if lo & 0x8000 else 0)) & 0xFFFF
    lis = {}
    out = []
    for va, w in text_words(d):
        op = w >> 26
        rt, ra, imm = (w >> 21) & 31, (w >> 16) & 31, w & 0xFFFF
        if op == 15 and ra == 0:               # lis
            lis[rt] = (va, imm)
        elif op in (14, 24) and rt != 0 or op in (14, 24):      # addi / ori
            if op == 14 and ra in lis and lis[ra][1] == hi_adj and imm == lo:
                out.append(va)
            if op == 24 and (w >> 21 & 31) in lis and lis[(w >> 21) & 31][1] == hi and imm == lo:
                out.append(va)
    return out

def find_str(d, s):
    for off, addr, size, i in d.secs:
        k = d.data.find(s.encode(), off, off + size)
        while k != -1:
            yield addr + k - off
            k = d.data.find(s.encode(), k + 1, off + size)

if __name__ == '__main__':
    d = Dol(sys.argv[1])
    if sys.argv[2] == 'str':
        for a in find_str(d, sys.argv[3]):
            print('%08X' % a, [('%08X' % x) for x in xrefs(d, a)])
    else:
        print([('%08X' % x) for x in xrefs(d, int(sys.argv[3], 0))])
