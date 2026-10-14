# How the Classic Controller patch works

Addresses are USA (`RS9E8P`); the other releases are found by signature search
(`tools/sig.py`) and the generated files carry their own.

## What the game does

Zero Gravity keeps **one input structure per player slot** (`0x803B53A0`, `0x70` bytes per
slot) and fills it from two places:

- **GameCube pads** — `FUN_80026444` calls `PADRead` once per frame into a `PADStatus[4]`
  buffer (`r20+0x80`), clamps it, and converts it to the slot structure.
- **Wii Remotes** — `FUN_800273c4` reads each channel with `KPADRead` into the game's own
  ring at `0x803B5BF0` (`0x840` bytes per channel, 16 samples of `0x84`) and converts that,
  according to the player's control scheme (*Hold Sideways*, *Hold Forward*).

A Classic Controller is a Wii Remote extension (device type `2` in the `KPADStatus` sample).
The unpatched game ignores it: with only a Classic Controller attached the intro movie
loops and never reaches the title screen.

Options → Control Settings already lists **Nintendo GameCube Controller**, so everything
downstream of the slot structure (menus, name entry, player entry, racing) already works with
a pad. That is what the patch feeds.

## The hook

| | |
| --- | --- |
| Site | `0x800264C0` — `lwz r3,0x80(r20)` straight after `PADRead` and before `PADClamp` |
| Body | `src/cc_pad.s`, assembled to `0x80001820` |
| Displaced instruction | run at the end of the body, then back to `site+4` |

For each of the four ports whose `PADStatus` error byte is non-zero (no real pad answered),
the body looks at the same channel's newest `KPADStatus` sample. If its device type is `2`
(Classic) and its extension error is `0`, it fills the port's `PADStatus`:

| `KPADStatus` (offset in a `0x84` sample) | `PADStatus` |
| --- | --- |
| `+0x60` Classic hold bits | button bits (table below) |
| `+0x6C/+0x70` left stick floats (-1..1) | stick X/Y, x 100 |
| `+0x74/+0x78` right stick floats | C-stick X/Y, x 100 |
| `+0x7C/+0x80` L/R trigger floats (0..1) | analog L/R, x 200 |

and clears the error byte. A port with a real pad (error `0`) is left alone, so GameCube
pads and Classic Controllers can be mixed.

The stick scale is 100. Measured in the game's slot structure: a full-deflection GameCube pad
gives 100, a `PADStatus` byte of 80 gave only 90 (Classic steering 10 % short), and a byte of
100 gives the same 100 as the pad.

Button bits:

| Classic (`hold`) | → | GameCube (`PADStatus.button`) |
| --- | --- | --- |
| A `0x0010` | | A `0x0100` |
| B `0x0040` | | B `0x0200` |
| X `0x0008` | | X `0x0400` |
| Y `0x0020` | | Y `0x0800` |
| + `0x0400` | | Start `0x1000` |
| L `0x2000` / R `0x0200` | | L `0x0040` / R `0x0020` |
| ZL `0x0080` / ZR `0x0004` | | Z `0x0010`, and L `0x0040` / R `0x0020` (the game ignores Z, so ZL/ZR also act as L/R) |
| Up `0x0001` Left `0x0002` Down `0x4000` Right `0x8000` | | Up `0x0008` Left `0x0001` Down `0x0004` Right `0x0002` |

## Why it is safe

- It uses data the game already reads (`KPADRead` into its own buffer) and a structure the game
  already has (`PADStatus`); no hardware registers are touched, so the Dolphin/hardware
  difference that hurts SI-level patches does not apply.
- It touches only volatile registers that are dead at the site (`r0, r3-r6, r8, r9, f0, f10, f11`,
  CR0; the site sits between two calls and `r3` is reloaded by the displaced instruction), uses a
  `0x40`-byte stack frame, and keeps no state of its own.
- The new code lives in a text section added to the DOL at `0x80001820`
  (`tools/layout.py`), below `0x80003000`.

## Test harness

`tools/dev/dolphin.py` runs Dolphin with a private user folder, Wii Remotes and GameCube pads
as named pipes, a GDB-stub memory reader, and save states. The slot comparison in the README
was made by pushing the same input through a GameCube pad and a Classic Controller and
reading `0x803B53A0` over GDB:

```
              GameCube pad            Classic Controller
stick right   btn=08000000 x=100      btn=08000000 x=100
stick up      btn=01000000 y=100      btn=01000000 y=100
A             btn=00000001            btn=00000001
```
