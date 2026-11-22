<p align="center">
  <img src="https://raw.githubusercontent.com/blaal02/ha-am350/main/custom_components/am350/brand/icon@2x.png" width="160" alt="AM350 RV Leveler">
</p>

# AM350 RV Leveler for Home Assistant

[![hacs][hacs-badge]][hacs-url]

Reads tilt data from the **AM350 wireless RV leveling system** (AOMOSUR / AUTOSIRS;
transmitter advertises as `AMS350-RV-TX`) over Bluetooth Low Energy and exposes it
as Home Assistant sensors.

> **Unofficial.** Not affiliated with the manufacturer. The BLE protocol was
> reverse-engineered from captures; see [`PROTOCOL.md`](PROTOCOL.md).

## Features

- Automatic Bluetooth discovery
- **Tilt X** and **Tilt Y** sensors (degrees)
- Calibration offsets, subtracted from the received values (Configure → *Use current reading as zero*)
- Works through ESPHome Bluetooth proxies
- Auto-reconnect

## Requirements

- Home Assistant 2025.1.0 or newer with the Bluetooth integration enabled
- A Bluetooth adapter or ESPHome Bluetooth proxy within range of the transmitter

## Installation

### HACS

1. HACS → ⋮ → **Custom repositories**
2. Add `https://github.com/blaal02/ha-am350`, category **Integration**
3. Download **AM350 RV Leveler** and restart Home Assistant

### Manual

Copy `custom_components/am350` into your `config/custom_components/` folder and restart.

## Setup

The device should be discovered automatically; otherwise go to
**Settings → Devices & services → Add integration → AM350 RV Leveler**.

**Power off the AM350 display first.** The transmitter probably accepts only one
connection at a time, so Home Assistant can't connect while the display is.

## Calibration

Open the device's entry and choose **Configure**:

- **Tilt X / Y offset (°)**: subtracted from each reading.
- **Use current reading as zero**: with the RV level, sets both offsets from the latest reading.

## Known limitations

- Angle scale (0.1° per unit) and axis naming are assumptions; see `PROTOCOL.md`.
- No battery level: none was found in the data captured so far.
- Display and Home Assistant can't be connected at the same time (see above).

## Troubleshooting

Enable debug logging:

```yaml
logger:
  logs:
    custom_components.am350: debug
```

To help with protocol work, run `tools/capture.py` (`pip install bleak`) and
open an issue with the output.

[hacs-badge]: https://img.shields.io/badge/HACS-Custom-orange.svg
[hacs-url]: https://hacs.xyz
