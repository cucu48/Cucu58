# Cucu58 firmware (ZMK)

This guide explains how the Cucu58 firmware works, assuming no prior ZMK knowledge.

## 1. What ZMK is

The keyboard's controller (the Supermini nRF52840) is a tiny computer. The **firmware** is the program it runs. Its job:

1. **Scan the matrix:** many times a second, check which switches are closed.
2. **Look up the keymap:** "row 2, column 3 on the left half is pressed" → "that's `D`".
3. **Send it** to the computer over USB or Bluetooth.

[ZMK](https://zmk.dev/) is an open-source keyboard firmware made for wireless boards like this one. It runs on top of [Zephyr](https://zephyrproject.org/), a small operating system for microcontrollers. That's why some files and words below come from Zephyr (devicetree, Kconfig, west).

You don't write code. You describe the keyboard in a few text files, and ZMK builds a firmware file (`.uf2`) from them.

## 2. How a split keyboard works in ZMK

Each half has its own controller and battery, so each half gets its **own firmware file**.

- **Left half = central.** It connects to your computer (USB or Bluetooth) and holds the keymap logic.
- **Right half = peripheral.** It only scans its own keys and sends "key X pressed/released" to the left half over Bluetooth.

Consequences:

- After changing the **keymap**, you normally only need to flash the **left** half (the right half only reports key positions). Flash both when you change pins, the matrix or the ZMK version.
- Pair the computer with the **left** half (the computer sees "Cucu58").
- The right half's battery drains a bit slower: it doesn't talk to the computer.

## 3. The files in this repo

```
build.yaml                         what to build: left, right, settings_reset
config/
  west.yml                         which ZMK version to download (pinned to v0.3)
  cucu58.keymap                    ★ what every key does. You'll edit this the most
  cucu58.conf                      settings: sleep, battery reporting, BT power…
boards/shields/cucu58/             hardware description ("shield" = board that plugs onto a controller)
  Kconfig.shield                   declares the shields cucu58_left / cucu58_right
  Kconfig.defconfig                defaults: name "Cucu58", split, left = central
  cucu58.dtsi                      matrix shared by both halves: size, diode direction, transform
  cucu58_left.overlay              left half's pins
  cucu58_right.overlay             right half's pins (mirrored: the PCB is flipped)
  cucu58-layout.dtsi               where keys are physically (for ZMK Studio / drawing tools)
  cucu58.zmk.yml                   metadata for ZMK tooling
zephyr/module.yml                  tells the build "this repo contains boards/shields"
.github/workflows/build.yml        GitHub Actions: build the firmware in the cloud
scripts/zmk_physical_layout.py     regenerates cucu58-layout.dtsi from Ergogen
```

### Why "shield" and "board"?

ZMK splits the hardware in two:

- **Board** = the controller: `nice_nano_v2`. The Supermini nRF52840 is a nice!nano v2 clone and uses the same firmware. ZMK already knows this board.
- **Shield** = your PCB that the controller plugs into: `cucu58_left` / `cucu58_right`. Defined in `boards/shields/cucu58/`.

A build is "board + shield", e.g. `nice_nano_v2` + `cucu58_left`. That's exactly what `build.yaml` lists.

### The hardware description (devicetree)

`.dtsi`, `.overlay` and `.keymap` files use **devicetree** syntax: nested blocks `name { property = value; };`. The pieces:

**kscan** (key scanner, in `cucu58.dtsi` + overlays): which GPIO pins are columns and rows, and the diode direction.

```dts
diode-direction = "col2row";                      // current: column → switch → diode → row
col-gpios = <&pro_micro 21 GPIO_ACTIVE_HIGH>, …;  // P21 = outer column on the left half
row-gpios = <&pro_micro 2 (GPIO_ACTIVE_HIGH | GPIO_PULL_DOWN)>, …;
```

`&pro_micro 21` means "the pin labeled 21 / P21 on a Pro Micro-shaped controller", the same names as the README wiring table and the KiCad footprint.

The two halves have different pins because the right PCB is flipped: P21 on the PCB lands on the controller's P2, and so on (README → *MCU pins and the two halves*).

**Matrix transform** (in `cucu58.dtsi`): turns electrical positions (row, column) into keymap positions 0–57. Each half has a 5 × 6 matrix; together they form a 5 × 12 matrix (the right half is shifted by `col-offset = <6>`). The thumb row has 10 keys, not 12: the outer columns have no thumb key.

```
 keymap positions:
  0  1  2  3  4  5 |  6  7  8  9 10 11      num row
 12 … 17           | 18 … 23                top row
 24 … 29           | 30 … 35                home row
 36 … 41           | 42 … 47                bottom row
    48 49 50 51 52 | 53 54 55 56 57         thumbs: super inny middy reachy extra | extra reachy middy inny super
```

You only touch the transform and the pins if the PCB wiring changes.

## 4. The keymap

`config/cucu58.keymap` has **layers**. Each layer is a list of 58 **bindings**, in the order above.

```dts
&kp Q          // "key press": sends Q
&mo LOWER      // "momentary": LOWER layer while held
&trans         // transparent: do whatever the layer below does
&none          // do nothing
```

Layers stack: holding `LOWER` makes the Lower layer active on top of Base. Wherever Lower has `&trans`, the Base key is used.

The starting keymap:

| Layer | How to get it | What's on it |
| --- | --- | --- |
| Base | default | QWERTY, numbers, Ctrl/Shift/GUI/Alt; thumbs: Space, Enter, Backspace; `thumb_extra` = `[` / `]` |
| Lower | hold left `thumb_reachy` | F1–F12, symbols `! @ # …`, `- = [ ] \ _ + { }` |
| Raise | hold right `thumb_reachy` | arrows, Home/End, PgUp/PgDn, media keys |
| Adjust | hold **both** | Bluetooth profiles, USB/BLE switch, bootloader, reset |

It's a starting point. Change it however you like: the comment above each layer is a drawing, and the binding lines below it are what counts. Keep 12 entries on each of the first 4 lines and 10 on the thumb line.

Useful things to read when customizing:

- Key names: <https://zmk.dev/docs/keymaps/list-of-keycodes>
- Behaviors (hold-tap / home-row mods, combos, macros, tap-dance, mouse keys…): <https://zmk.dev/docs/keymaps/behaviors>
- Visual keymap editor that edits this file: <https://nickcoutsos.github.io/keymap-editor/> (connect it to your GitHub repo)

## 5. Building the firmware

You don't install anything. GitHub builds it:

1. Push this repo to GitHub (Actions must be enabled, which is the default).
2. Every push that changes `config/`, `boards/`, `build.yaml` or the workflow starts a build. You can also start one by hand: **Actions → Build ZMK firmware → Run workflow**.
3. When it finishes (green check, ~3–5 min), open the run and download **firmware** under *Artifacts*. Inside:
   - `cucu58_left-nice_nano_v2-zmk.uf2`
   - `cucu58_right-nice_nano_v2-zmk.uf2`
   - `settings_reset-nice_nano_v2-zmk.uf2`

If the build fails (red ✗), open the failed job: the error usually points at a line in the keymap (a typo in a key name, a missing `;` or `>`, or the wrong number of keys).

### Building locally (optional)

Only if you want to build without GitHub. It needs Docker/Podman, and the first build downloads ~1–2 GB:

```sh
mkdir -p ~/zmk-ws && cp -r config ~/zmk-ws/
docker run --rm -it -v ~/zmk-ws:/ws:z -v "$PWD":/cucu58:ro,z -w /ws zmkfirmware/zmk-build-arm:3.5 sh -c '
  west init -l config && west update && west zephyr-export &&
  west build -p -s zmk/app -d build/left -b nice_nano_v2 -- -DSHIELD=cucu58_left \
      -DZMK_CONFIG=/cucu58/config -DZMK_EXTRA_MODULES=/cucu58'
# result: ~/zmk-ws/build/left/zephyr/zmk.uf2
```

## 6. Flashing

The controller has a **UF2 bootloader**, so flashing works like copying a file to a USB stick:

1. Connect **one half** with USB-C (power switch ON: it sits between battery and charger).
2. **Double-tap the reset button** quickly. A drive called `NICENANO` (or similar) appears.
3. Copy the matching `.uf2` onto it. The drive disappears by itself: that's normal, it's flashed.
4. Repeat for the other half with its own file.

Once the firmware is running, you can also enter the bootloader with the **BOOT** key on the Adjust layer, instead of the reset button.

## 7. Pairing

1. Flash both halves and switch both ON. The halves find each other automatically (the first time can take a few seconds).
2. On your computer, open Bluetooth settings and pair with **Cucu58**.
3. Up to 5 devices: Adjust layer → `BT0`–`BT4` selects a slot, then pair the new device in that slot. `BTCLR` forgets the device in the current slot.
4. With USB plugged in, ZMK sends keys over USB by default. Use `USB` / `BLE` on the Adjust layer to switch.

### If the halves stop talking to each other

1. Flash `settings_reset-nice_nano_v2-zmk.uf2` to **both** halves.
2. Flash the normal left/right firmware again.
3. Remove "Cucu58" from your computer's Bluetooth list and pair again.

## 8. First power-on checklist

- [ ] Before anything: check the **battery polarity** on each half (README → *Power*). The right half's connector isn't reversible yet.
- [ ] Left half over USB: open a key tester (e.g. <https://www.keyboardtester.com/>) and press every key on the left.
- [ ] Right half: same. If a whole **row or column** is dead or swapped on the right, the mirrored pin mapping in `cucu58_right.overlay` is off. Check with a multimeter which controller pin each row/column trace goes to, and fix the list.
- [ ] If **every** key does nothing, the diodes may be backwards: the firmware expects `col2row`. Changing `diode-direction` to `"row2col"` in `cucu58.dtsi` is the software fix.
- [ ] A single dead key is usually a solder joint or a diode.

## 9. Settings (`config/cucu58.conf`)

| Setting | Meaning |
| --- | --- |
| `CONFIG_ZMK_SLEEP=y` | deep sleep after `CONFIG_ZMK_IDLE_SLEEP_TIMEOUT` ms (15 min). A key press wakes it (the first press is used to wake up, then typing works) |
| `CONFIG_ZMK_SPLIT_BLE_CENTRAL_BATTERY_LEVEL_*` | the computer shows the right half's battery too |
| `# CONFIG_BT_CTLR_TX_PWR_PLUS_8=y` | uncomment for stronger Bluetooth if the connection drops |

All options: <https://zmk.dev/docs/config>.

## 10. Keeping firmware and PCB in sync

| If you change in `config.yaml`… | update in the firmware |
| --- | --- |
| a `col_net` / `row_net` (which pin a column/row uses) | the pin lists in both `.overlay` files (right half: use the mirrored pin, README table) |
| add/remove keys | `cucu58.dtsi` transform, every layer in `cucu58.keymap`, and regenerate the layout ↓ |
| key positions / rotation only | regenerate `cucu58-layout.dtsi` (cosmetic, only for drawing tools) |

Regenerate the physical layout:

```sh
ergogen config.yaml -o output --debug
python3 scripts/zmk_physical_layout.py output/points/points.yaml
# paste the printed lines into the `keys` property of boards/shields/cucu58/cucu58-layout.dtsi
```

## 11. Upgrading ZMK

The ZMK version is pinned to the `v0.3` release in two places: `config/west.yml` (`revision`) and `.github/workflows/build.yml` (`@v0.3`). Change both together. Newer ZMK versions (main branch, after Zephyr 4) renamed the board to `nice_nano//zmk` and may need small shield changes. Check the ZMK release notes first.
