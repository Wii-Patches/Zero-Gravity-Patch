"""Build the Classic Controller feature for one release from a retail main.dol."""
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'tools'))
import asm
from layout import CC_BASE, CC_END
from ops import Feature, Hook

# USA addresses (RS9E8P); other releases are found by signature search
POLL_HOOK = (0x800264C0, 6, 6)          # `lwz r3,0x80(r20)` right after PADRead in the pad poll
KPAD_BUF = 0x803B5BF0                   # the game's KPADStatus ring, 0x840 per channel
KPAD_BUF_SITE = (0x80028B24, 4, 6)      # `addi r4,r4,lo` in the per-channel KPAD read (its `lis r4` is a few words earlier)


USA_DOL = None                          # set by gen_prebuilt.py; the retail RS9E8P main.dol
USA_ID = 'RS9E8P'


def build(region, dol, usa_dol=None):
    from sig import find_unique
    if region != USA_ID and usa_dol is None:
        usa_dol = USA_DOL
        if usa_dol is None:
            raise SystemExit('%s needs the USA main.dol to find its sites: set gen_cc.USA_DOL' % region)
    site = POLL_HOOK[0] if usa_dol is None else find_unique(usa_dol, dol, *POLL_HOOK)
    orig = struct.unpack('>I', dol.read(site, 4))[0]
    if orig != 0x80740080:
        raise SystemExit('%s: poll hook site is 0x%08X' % (region, orig))
    kbase = KPAD_BUF if usa_dol is None else _kpad_buf(usa_dol, dol)
    body = asm.words(asm.assemble(open(os.path.join(HERE, 'cc_pad.s')).read(), CC_BASE, {'KBASE': kbase}, {'DBG': int(os.environ.get('ZG_DBG', '0'))})) + [0]
    ops = [Hook(site, orig, body, CC_BASE, note='pad poll: Classic Controller -> GameCube PADStatus')]
    if CC_BASE + len(body) * 4 > CC_END:
        raise SystemExit('cc code overflows its window')
    return Feature('cc', 'Classic Controller', region, ops)


def _kpad_buf(usa_dol, dol):
    """The KPAD ring address in `dol`, read from the lis/addi pair that builds it in the same place as in USA."""
    from sig import find_unique
    addi_at = find_unique(usa_dol, dol, *KPAD_BUF_SITE)
    addi = struct.unpack('>I', dol.read(addi_at, 4))[0]
    lis = next((w for w in (struct.unpack('>I', dol.read(addi_at - 4 * k, 4))[0] for k in range(1, 6))
                if w >> 16 == 0x3C80), None)
    if lis is None or addi >> 16 != 0x3884:
        raise SystemExit('%s: unexpected KPAD buffer load at 0x%08X' % (dol.path, addi_at))
    lo = addi & 0xFFFF
    return (((lis & 0xFFFF) << 16) + (lo - 0x10000 if lo & 0x8000 else lo)) & 0xFFFFFFFF
