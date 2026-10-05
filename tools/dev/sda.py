"""Dev-time: list code that touches an SDA (r13/r2) variable, given its absolute address.

    python3 tools/dev/sda.py RS9E8P.dol 0x80608F78
"""
import os, struct, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from dol import Dol
SDA = {13: 0x80610900, 2: 0x80613460}      # USA: set per region by the caller if different
def find(d, addr, sda=SDA):
    out = []
    for off, base, size, i in d.secs:
        if i >= 7: continue
        for k in range(0, size, 4):
            w = struct.unpack('>I', d.data[off + k: off + k + 4])[0]
            ra = (w >> 16) & 31
            if ra in sda and (w >> 26) in range(14, 56):
                imm = w & 0xFFFF
                if imm & 0x8000: imm -= 0x10000
                if (sda[ra] + imm) & 0xFFFFFFFF == addr:
                    out.append(base + k)
    return out
if __name__ == '__main__':
    d = Dol(sys.argv[1])
    print(['%08X' % x for x in find(d, int(sys.argv[2], 0))])
