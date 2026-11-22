# Cucu58

A 58-key split, wireless, low-profile ergonomic keyboard, designed from scratch. Named after its designer (Cucu) and its key count.

The whole design (key layout, outlines and PCB footprints) is described in a single [Ergogen](https://ergogen.xyz/) config, [`config.yaml`](config.yaml), which generates the KiCad PCB.

> **Status:** work in progress.
>
> - **Done:** key layout (matrix, thumb cluster and `thumb_extra` key), PCB outline, footprints for switches, diodes, MCU, power/reset switches and battery connector, and the matrix wiring (see [Wiring](#wiring)).
> - **Diodes:** one `diode_tht_sod123` per key, offset from its switch, with both SMD and through-hole pads (`include_tht`) joined by traces. This lets either diode type be soldered, since the final choice isn't made yet.
> - **Firmware:** ZMK config in this repo, built by GitHub Actions (see [Firmware](#firmware-zmk) and [FIRMWARE.md](FIRMWARE.md)). Not yet tested on hardware.
> - **Still to do:** make the battery connector reversible (see [Power](#power)), route the PCB in KiCad, and check the diode orientation and the right-half pin mapping on a real board.

## Overview

- **Layout:** staggered 6-column × 4-row matrix per half, plus a thumb cluster (Ferris Sweep-inspired, with a tighter thumb placement to keep the PCB small) and an extra key near the inner column.
- **Key spacing:** 18 × 17 mm (Ergogen's `cx` × `cy` Choc spacing). Keycaps are 17.5 × 16.5 mm, leaving 0.5 mm between caps.
- **Switches:** Kailh Choc V2 low profile (the `ceoloide/switch_choc_v1_v2` footprint also supports Choc V1), hotswap-free solder footprint, reversible.
- **MCU:** Supermini nRF52840 (nice!nano compatible clone), wireless via Bluetooth.
- **Power:** 110 mAh LiPo battery (3.7 V, JST PH 2-pin), SMD side power switch.
- **Other:** tactile reset switch, 1N4148W SOD-123 diodes.
- **PCB:** KiCad 8 template, reversible footprints so one PCB design serves both halves.

## Bill of materials

| Part | Notes |
| --- | --- |
| Switches | [Kailh Choc V2 low profile red](https://cdn.shopify.com/s/files/1/0657/6075/5954/files/SPEC-CPG135301D01_Kailh_Choc_V2_Low_Profile_Red_Switch.pdf?v=1666690444) |
| Keycaps | [Tai-Hao](https://shop.tai-hao.com/products/black) |
| Diodes | 1N4148W T4, SOD-123 |
| Reset switch | [C&K PTS636SL43 LFS](https://www.digikey.es/es/products/detail/c-k/PTS636SL43-LFS/10071714) |
| Power switch | SSSS811101 |
| Battery | [Li-Po 110 mAh 3.7 V 301230, PH2 2-pin](https://ampul.eu/en/batteries/5763-li-pol-battery-110mah-37v-301230-ph2-2pin) |
| Battery connector | JST PH 2-pin |
| MCU | [nice!nano](https://nicekeyboards.com/docs/nice-nano/) or [Supermini NRF52840](https://wiki.icbbuy.com/doku.php?id=developmentboard:nrf52840) (the config currently targets the Supermini) |
| Encoders | TBD |

## Wiring

All nets come from `config.yaml`: each key's `col_net` / `row_net`, plus the footprints' default nets. Pin names are the Pro Micro-style names printed on the MCU footprint (`P21` = `&pro_micro 21` in ZMK).

### Key matrix

- **Type:** diode matrix, **COL2ROW** (ZMK: `diode-direction = "col2row"`). Each key gets its own net named `<column>_<row>` (e.g. `pinky_home`).
- **Per key:** column net → switch → `<column>_<row>` → diode anode → diode cathode → row net.
- **Diodes:** the cathode (pad 1, the square through-hole pad / marked end) faces the row net. Solder **either** the SMD SOD-123 **or** a through-hole diode on each key, not both.
- **Size:** 6 columns × 5 rows = 30 positions for 29 keys (the outer column has no thumb key). That's 11 GPIOs per half.

| Row (net) ↓ / Column (net) → | outer (P21) | pinky (P20) | ring (P19) | middle (P18) | index (P15) | inner (P14) |
| --- | --- | --- | --- | --- | --- | --- |
| num (P2) | `matrix_outer_num` | `matrix_pinky_num` | `matrix_ring_num` | `matrix_middle_num` | `matrix_index_num` | `matrix_inner_num` |
| top (P3) | `matrix_outer_top` | `matrix_pinky_top` | `matrix_ring_top` | `matrix_middle_top` | `matrix_index_top` | `matrix_inner_top` |
| home (P4) | `matrix_outer_home` | `matrix_pinky_home` | `matrix_ring_home` | `matrix_middle_home` | `matrix_index_home` | `matrix_inner_home` |
| bottom (P5) | `matrix_outer_bottom` | `matrix_pinky_bottom` | `matrix_ring_bottom` | `matrix_middle_bottom` | `matrix_index_bottom` | `matrix_inner_bottom` |
| thumb (P6) | none | `thumb_super` | `thumb_inny` | `thumb_middy` | `thumb_reachy` | `thumb_extra` |

### MCU pins and the two halves

The PCB is reversible: the right half is the same board flipped over, with the MCU mounted on the other side. The MCU footprint uses `only_required_jumpers: true`, so only the top 4 pin rows (RAW, GND, RST, VCC, P0, P1) have solder jumpers and stay on the same pin on both halves. The other pins are **mirrored** on the flipped half: each net lands on the MCU pin across from it. So each half needs its own pin list in the firmware.

| PCB net | Role | Left half (as drawn by Ergogen) | Right half (flipped) |
| --- | --- | --- | --- |
| P21 | column outer | P21 | P2 |
| P20 | column pinky + `thumb_super` | P20 | P3 |
| P19 | column ring + `thumb_inny` | P19 | P4 |
| P18 | column middle + `thumb_middy` | P18 | P5 |
| P15 | column index + `thumb_reachy` | P15 | P6 |
| P14 | column inner + `thumb_extra` | P14 | P7 |
| P5 | row bottom | P5 | P18 |
| P4 | row home | P4 | P19 |
| P3 | row top | P3 | P20 |
| P2 | row num | P2 | P21 |
| P6 | row thumb | P6 | P15 |

Mirrored pin pairs (same row of the footprint): P21↔P2, P20↔P3, P19↔P4, P18↔P5, P15↔P6, P14↔P7, P16↔P8, P10↔P9.

Unused pins:

- **Left half:** P0, P1, P7, P8, P9, P10, P16.
- **Right half:** P0, P1, P8, P9, P10, P14, P16.
- P0 and P1 are jumpered, so they're the same pin on both halves, which makes them the easiest to use for a future add-on.
- P10 and P16 are the nRF52840's NFC pins. They only work as GPIO after setting `&uicr { nfct-pins-as-gpios; };` in ZMK. On the right half the PCB's P9 and P8 nets land on them.

These pin lists are what the firmware uses: see [`cucu58_left.overlay`](boards/shields/cucu58/cucu58_left.overlay) and [`cucu58_right.overlay`](boards/shields/cucu58/cucu58_right.overlay). The right half lists its columns inner → outer (its physical left-to-right order), which keeps the keymap a plain mirror of the left. The right-half mapping comes from the footprint geometry and hasn't been tested on a real board yet: check one column and one row with a multimeter on the first assembled right half.

### Power

```
battery + ── JST pin 2 ── BAT_P ── power switch ── RAW (MCU B+)
battery − ── JST pin 1 ── GND ──────────────────── GND (MCU)
reset button: RST ── GND
```

- **Power switch** (SSSS811101, `power_switch_smd_side`, reversible): the common pin 2 goes to `RAW`, one end pin to `BAT_P`, and the other end pin is unconnected. ON/OFF is on the same physical side on both halves. The front and back pads aren't joined by vias, so route both in KiCad.
- **USB charging only works with the switch ON.** The switch sits between the battery and the MCU's charger input (`RAW` / B+), so OFF disconnects the battery from the charger too.
- **`VCC`** (the MCU's 3.3 V output) is unused, since there are no LEDs or displays.
- **⚠ Battery polarity on the right half:** the JST connector footprint (`molex_connector`) is currently **not** reversible. On the flipped half the connector's pins end up in mirrored holes, so the battery would be connected **backwards** and can destroy the MCU. Fix it before ordering by adding `reversible: true` to its `params`, which adds polarity jumpers. Then bridge the jumpers on the side the connector is soldered on.
- **Check the battery leads:** not every seller wires JST PH batteries the same way. Before plugging in, compare the red wire with the +/− silkscreen.

## Building the PCB

### Option A: web version (what's used currently)

1. Open [ergogen.xyz](https://ergogen.xyz/) and paste the contents of `config.yaml`.
2. Download the generated PCB (`.kicad_pcb`) and outlines, then open the PCB in KiCad.

### Option B: command line

Requires [Node.js](https://nodejs.org/) and Ergogen.

```sh
npm install -g ergogen        # or: npx ergogen ...
ergogen config.yaml -o output --debug
```

Ergogen writes its results to `output/`:

- `output/pcbs/split.kicad_pcb`: the PCB, to open in KiCad 8
- `output/outlines/`: DXF outlines (e.g. `pcb_edge`)
- `output/points/`, `output/source/`: debug/intermediate data (with `--debug`)

The config uses the `kicad8` template. The PCB it generates also opens in newer KiCad versions (e.g. KiCad 10), which upgrade the file on save, so there is no need to install KiCad 8. Open the generated PCB in KiCad, then route and finish it there. Regenerating overwrites the file, so **make design changes in `config.yaml`, not in the generated output**, unless you are doing the final routing.

The footprints come from the Ergogen community libraries. Ergogen 4.1.0 is the targeted engine (see `meta.engine`).

## Firmware (ZMK)

The keyboard runs [ZMK](https://zmk.dev/). The firmware config lives in this repo and GitHub Actions builds it on every push that touches it. **[FIRMWARE.md](FIRMWARE.md)** explains how ZMK works, how to edit the keymap, and how to flash and pair the halves.

Quick version:

1. Edit [`config/cucu58.keymap`](config/cucu58.keymap) and push.
2. On GitHub, open **Actions → Build ZMK firmware → latest run → Artifacts** and download `firmware.zip`.
3. Plug in a half, double-tap its reset button (it shows up as a USB drive), and copy `cucu58_left-nice_nano_v2-zmk.uf2` or `cucu58_right-nice_nano_v2-zmk.uf2` onto it.

## Repository layout

```
config.yaml             Ergogen config: units, points (layout), outlines, PCB footprints
config/                 ZMK: keymap (cucu58.keymap), settings (cucu58.conf), ZMK version (west.yml)
boards/shields/cucu58/  ZMK: hardware description of the keyboard (pins, matrix, layout)
build.yaml              ZMK: which firmware files GitHub Actions builds
zephyr/module.yml       ZMK: lets the build find boards/shields/
.github/workflows/      GitHub Actions workflow that builds the firmware
scripts/                Helpers (zmk_physical_layout.py: Ergogen points -> ZMK layout)
FIRMWARE.md             ZMK guide for this keyboard
AGENTS.md               Instructions for AI coding agents working on this repo
README.md               This file
output/                 Generated files (not versioned)
```

## References

- ZMK: [docs](https://zmk.dev/docs) · [keycodes](https://zmk.dev/docs/keymaps/list-of-keycodes) · [behaviors](https://zmk.dev/docs/keymaps/behaviors) · [new shield guide](https://zmk.dev/docs/development/hardware-integration/new-shield)
- Ergogen: [site](https://ergogen.xyz/) · [docs](https://docs.ergogen.xyz/)
- Footprints: [ceoloide/ergogen-footprints](https://github.com/ceoloide/ergogen-footprints/) · [ergogen built-ins](https://github.com/ergogen/ergogen/tree/develop/src/footprints) · [infused-kim/kb_ergogen_fp](https://github.com/infused-kim/kb_ergogen_fp)
