"""Dev-time: build a patched main.dol for one release straight from the generators.

    python3 tools/quick.py RS9E8P in.dol out.dol [cc ...]
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '..', 'src'))
from dol import Dol
from ops import apply_static
import importlib
if __name__ == '__main__':
    region, src, dst, *feats = sys.argv[1:]
    d = Dol(src)
    mods = [importlib.import_module('gen_' + n) for n in (feats or ['cc'])]
    for m in mods:
        if hasattr(m, 'USA_DOL'):
            m.USA_DOL = Dol(os.environ.get('ZG_USA_DOL', os.path.join(HERE, '..', 'dumps', 'dols', 'RS9E8P.dol')))
    fs = [m.build(region, d) for m in mods]
    apply_static(d, fs)
    d.save(dst)
    print('wrote', dst)
