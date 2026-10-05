# Sources

| File | Purpose |
| --- | --- |
| `cc_pad.s` | The hook body: Classic Controller → GameCube `PADStatus` (see [docs/TECHNICAL.md](../docs/TECHNICAL.md)) |
| `gen_cc.py` | Builds the feature for one release from a retail `main.dol`: finds the hook site and the KPAD buffer by signature, assembles `cc_pad.s` (needs devkitPPC) |

`python3 tools/gen_prebuilt.py` writes `tools/prebuilt/*.json`, which is what the patcher
ships and reads; end users need neither devkitPPC nor game files for that.

`KBASE` (the game's `KPADStatus` ring) is filled in per release at build time. Set `ZG_DBG=1`
to build a variant that keeps a call counter and the last KPAD fields at `0x80002F00`.
