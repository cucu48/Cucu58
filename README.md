# Cucu58

A 58-key split, wireless, low-profile ergonomic keyboard, designed from scratch. Named after its designer (Cucu) and its key count.

The whole design (key layout, outlines and PCB footprints) is described in a single [Ergogen](https://ergogen.xyz/) config, [`config.yaml`](config.yaml), which generates the KiCad PCB.

> **Status:** work in progress.
>
> - **Done:** key layout (matrix, thumb cluster and `thumb_extra` key), PCB outline, footprints for switches, diodes, MCU, power/reset switches and battery connector.
> - **Diodes:** one `diode_tht_sod123` per key, offset from its switch, with both SMD and through-hole pads (`include_tht`) joined by traces. This lets either diode type be soldered, since the final choice isn't made yet.
> - **Still to do:** the matrix wiring. The switch nets and the MCU pin mapping in `config.yaml` are still placeholders, not final.

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

## Repository layout

```
config.yaml   Ergogen config: units, points (layout), outlines, PCB footprints
AGENTS.md     Instructions for AI coding agents working on this repo
README.md     This file
output/       Generated files (not versioned)
```

## References

- Ergogen: [site](https://ergogen.xyz/) · [docs](https://docs.ergogen.xyz/)
- Footprints: [ceoloide/ergogen-footprints](https://github.com/ceoloide/ergogen-footprints/) · [ergogen built-ins](https://github.com/ergogen/ergogen/tree/develop/src/footprints) · [infused-kim/kb_ergogen_fp](https://github.com/infused-kim/kb_ergogen_fp)
