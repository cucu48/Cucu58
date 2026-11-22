# AGENTS.md

Guidance for AI coding agents working on the **Cucu58**, a 58-key split wireless low-profile keyboard. See [README.md](README.md) for the project overview and bill of materials.

## What this repo is

A hardware design repo. The source of truth for the hardware is one [Ergogen](https://docs.ergogen.xyz/) config, `config.yaml` (engine 4.1.0), which generates the KiCad 8 PCB and outlines.

It also hosts the **ZMK firmware** config (pinned to ZMK `v0.3`, board `nice_nano_v2`, shields `cucu58_left` / `cucu58_right`), laid out like ZMK's unified-zmk-config-template so GitHub Actions can build it: `build.yaml`, `config/` (west.yml, `cucu58.keymap`, `cucu58.conf`), `boards/shields/cucu58/`, `zephyr/module.yml`, `.github/workflows/build.yml`. Don't confuse the `config/` directory (ZMK) with `config.yaml` (Ergogen). See FIRMWARE.md.

## Commands

```sh
ergogen config.yaml -o output --debug   # regenerate everything into output/
```

`output/` is generated: never hand-edit it for design changes, and don't commit it unless asked. After any edit to `config.yaml`, run the command above and check that it completes without errors and that the PCB/outline files are produced. If Ergogen isn't installed, say so rather than claiming the config works.

## Firmware (ZMK) rules

- Pins in `boards/shields/cucu58/cucu58_left.overlay` / `cucu58_right.overlay` must match the README wiring table. The right half's pins are mirrored (flipped PCB) and its columns are listed inner → outer.
- The keymap order is defined by the matrix transform in `cucu58.dtsi`: 4 rows × 12, then 10 thumbs. Every layer must have exactly 58 bindings, and `cucu58-layout.dtsi` must list keys in the same order (regenerate it with `scripts/zmk_physical_layout.py`).
- Bump the ZMK version in `config/west.yml` and `.github/workflows/build.yml` together.
- To check a firmware change locally, build it in the `zmkfirmware/zmk-build-arm:3.5` container (see FIRMWARE.md). If you can't build it, say so.

## `config.yaml` structure

- `meta`: engine version, config version, author.
- `units`: custom units and defaults (`cx`/`cy` are Ergogen's built-in Choc key spacing, 18 × 17 mm; `U` = 19.05 mm MX spacing and `u` = 19 mm are only used for staggers). Note that `$default_*` values reference `cx`/`cy`.
- `points.zones`:
  - `matrix`: main 6 columns (`outer, pinky, ring, middle, index, inner`) × 4 rows (`bottom, home, top, num`) with per-column `stagger`.
  - `thumb`: anchored to `matrix_ring_bottom`; keys `thumb_super`, `thumb_inny`, `thumb_middy`, `thumb_reachy` (the last two are splayed and rotated with a custom `origin`).
  - `thumb_extra`: single key in its own zone, anchored to `matrix_inner_bottom` (`shift: [1cx, 1/2cy]`), named `thumb_extra`. It is a separate zone because `anchor` only works at zone level, and `adjust` can only reference points in its own zone.
- `outlines.pcb_edge`: rectangle with fillet around the keys.
- `pcbs.split`: KiCad 8 template with footprints from `ceoloide/*`: Choc V1/V2 switches (reversible), one `diode_tht_sod123` per key (reversible, with both SMD and THT pads joined by traces via `include_tht` + `include_traces_vias`, offset with `adjust.shift`), SMD side power switch, THT reset switch, JST PH2 battery connector, Supermini nRF52840 MCU with its pin-to-net mapping.

Key names follow `<zone>_<column>_<row>` (e.g. `matrix_inner_home`); thumb keys use their explicit `name`.

## Conventions

- Keep the layout reversible (one PCB design for both halves): keep `reversible: true` on footprints that support it.
- Prefer relative placement (`ref` + `shift`) over absolute coordinates so the layout survives changes upstream.
- Use the `cx`/`cy`/`U` units rather than hardcoded millimetres where possible; comment any magic numbers (the file already explains the thumb shift values).
- Keep comments in the YAML explaining *why* a value was chosen.
- Footprint parameters must exist in the chosen footprint; check the [ceoloide footprint docs](https://github.com/ceoloide/ergogen-footprints/) before adding or renaming params.
- Don't swap components (switches, MCU, diodes, battery, connectors) without asking, since the BOM in README.md is deliberate.

## Project state

`config.yaml` is a work-in-progress template. The layout and the diode footprints are done; the matrix wiring (switch nets and MCU pin-to-net mapping) is not, so don't treat the current nets or pin assignments as intentional. The author currently uses the Ergogen web app, and Ergogen may not be installed locally; KiCad 10 is used (the `kicad8` template output opens fine in it). Key spacing is Ergogen's default Choc `cx`=18 mm × `cy`=17 mm; keycaps are 17.5 × 16.5 mm.

## Known issues to be aware of

- The MCU mapping uses `P8: thumb_tucky`, but no thumb key has that name (the defined ones are `thumb_super`, `thumb_inny`, `thumb_middy`, `thumb_reachy`). Net names must match real keys.
- The switch footprint uses `from: "{{col_net}}"` / `to: "{{col_row}}"`, while the diodes use `{{colrow}}` / `{{row_net}}`. Ergogen's built-in names are `column_net`, `row_net` and `colrow`, so the switch nets likely don't match the diodes and need fixing when the wiring is done.
- Once diodes are wired, the MCU `P*` mappings should point at column and row nets (not individual keys). The thumb zone also needs its own row/column names so its nets don't collide with the matrix.
- Diode orientation (which pad is the cathode, facing the row net) is not yet verified in KiCad.
- Some footprint IDs contain typos (`power_swich`, `reset_swich`, `molex_connector` for a JST PH2). They're only internal names, but renaming is safe only if nothing references them.

Flag these to the user when relevant instead of silently "fixing" them if the intent is ambiguous.

## Git

- Commit only when asked. Keep commits small and focused on one design change.
- Don't commit generated output or editor/KiCad backup files.
