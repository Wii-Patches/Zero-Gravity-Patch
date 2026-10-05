# Zero Gravity Patch

Play **Sonic Riders: Zero Gravity** (Wii) with a **Classic Controller** — and, for
reference, with the **GameCube controller** the game already supports. Works with
the USA (`RS9E8P`), European (`RS9P8P`) and Japanese (`RS9J8P`, *Sonic Riders:
Shooting Star Story*) releases.

The patch is applied to your own copy of the game: run the patcher on a clean `.wbfs`
or `.iso` and play the result on a Wii (USB loader) or in Dolphin. Nothing from the
game is included in this repository.

## Status

Tested in Dolphin (scripted controller input) on all three releases:

- a Classic Controller drives the intro skip, title, save select, name entry, mode and course
  select and player entry, and steers in a race; a second Classic Controller joins as player 2
- the game's own input state for a Classic Controller matches the one for an emulated
  GameCube pad (buttons, both sticks, same full-scale stick value of 100)
- a GameCube pad keeps working with the patch applied
- the disc patcher (`.iso` through `wit`) produces an image that boots and behaves the same

**Not tested on a real Wii.** The patch only reuses what the game and the Wii SDK already do
(see [docs/TECHNICAL.md](docs/TECHNICAL.md)), but it has not been run on hardware.

## How it works in one paragraph

The game has no Classic Controller support, but it does have a complete GameCube
controller path: a per-frame `PADRead`, then one shared player-input structure for
every device. For every port with no real GameCube pad, the patch reads the Wii Remote
channel's Classic Controller data (the game already keeps it for the Wii Remote path)
and writes it into that port's `PADStatus`. The rest of the game sees an ordinary
GameCube controller, so every screen, every race mode and every player slot behave the
way they do with the real thing. A real GameCube pad in a port is never overridden.

## Controls

The Classic Controller acts as a GameCube controller. In the game, Classic Controller
players use the same layout as **Options → Control Settings → Nintendo GameCube
Controller**.

| Classic Controller | GameCube controller |
| --- | --- |
| Left stick | Control stick |
| Right stick | C-stick |
| A / B / X / Y | A / B / X / Y |
| + | Start |
| L / R (click) | L / R |
| ZL / ZR | Z |
| D-pad | D-pad |

HOME is left to the game and the Wii's HOME Menu.

- A second player joins at the player-entry screen by pressing A on their controller (tested
  with two Classic Controllers in Dolphin; players 3 and 4 are untested).
- Classic Controller *N* is Wii Remote channel *N*, and drives the same player as
  GameCube port *N*.

## Installing

### Patch your disc image

You need a clean `.wbfs` or `.iso`, Python 3 and [Wiimms ISO Tool](https://wit.wiimm.de/)
(`wit`) on your `PATH`:

```bash
python3 tools/patch_disc.py "Sonic Riders - Zero Gravity (USA).wbfs"
```

The patcher checks the disc id, patches `sys/main.dol`, rebuilds the image in the same
format and replaces your file, keeping the original next to it as `<name>.bak`. Other
releases, and images already modified by something else, are refused rather than
corrupted. Running it twice is harmless.

A drag-and-drop GUI (`python3 tools/gui.py`, needs tkinter) does the same. CI builds
standalone apps with `wit` bundled for macOS, Linux and Windows (`.github/workflows/build-gui.yml`),
plus zips of the Gecko codes and Riivolution patches; tagged `v*` pushes attach them to the release.

### Gecko codes (Dolphin)

Copy `codes/<disc id>.ini` (`RS9E8P`, `RS9P8P` or `RS9J8P`) into Dolphin's `GameSettings`
folder and enable **Classic Controller** under **Properties → Gecko Codes**. Connect a Wii
Remote with a Classic Controller in Wii Remote 1 (and 2…4).

The same code is in `codes/<disc id>.txt` in the plain layout loaders read. On a real
console with a loader's own code handler, prefer the patched disc.

### Riivolution

`riivolution/<disc id>.xml` is a Riivolution patch with one switch. It matches on the disc id
and version, so it cannot be applied to the wrong release.

### Patch a `main.dol` directly

```bash
python3 tools/patcher.py <retail main.dol> <patched main.dol>
```

## On a real Wii

- Play the patched image from a USB loader as usual. Turn the loader's **cheats /
  debugger off** for this game when using the patched image: the patch lives at
  `0x80001820`, next to where a Gecko code handler sits.

## Building from source

The patcher needs only Python 3 and `wit`. The routine it injects ships pre-assembled in
`tools/prebuilt/` (checked by `tools/check.py`). With
[devkitPPC](https://devkitpro.org/) and your own `main.dol` dumps you can rebuild it from
`src/`:

```bash
ZG_DOLS=/dir/with/RS9E8P.dol,RS9P8P.dol,RS9J8P.dol python3 tools/gen_prebuilt.py
python3 tools/build.py          # regenerate codes/ and riivolution/
python3 tools/check.py          # consistency checks (no game files needed)
ZG_DOLS=... python3 tools/verify.py   # checks the patch against the retail DOLs
python3 -m unittest tests/test_disc_ids.py
```

`tools/dev/` holds the Dolphin test harness (scripted pads over named pipes, GDB memory
access, save states) and the Ghidra helpers used to find the hook sites.

## License

MIT — see [LICENSE](LICENSE).

Copyright (c) 2026 quatric

### Modded images

Disc patchers match the first four characters of the game ID (ID4), so mods can change the
last two characters. The original disc ID and filename are preserved. Revision and
executable patch-site checks still apply; mods that change required code may be incompatible.
