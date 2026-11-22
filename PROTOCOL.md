# AM350 BLE protocol (reverse-engineered)

Device name: `AMS350-RV-TX`. Vendor string (0x2A29): `GL Co.,Ltd.`; firmware revision 1.0.0.15.

Tilt data arrives as notifications on characteristic `0000ff03-0000-1000-8000-00805f9b34fb`
(service `0000ff01-...`), roughly several per second, no write needed to start them.

| Bytes | Meaning |
|-------|---------|
| 0-1   | `03 03` header |
| 2-3   | X, int16 little-endian |
| 4-5   | Y, int16 little-endian |
| 6     | checksum = sum(bytes 0..5) mod 256 |

Example: `03 03 0e 00 f7 ff 0a` → X = 14, Y = -9.

Unverified: raw unit (assumed 0.1°), which axis is pitch vs roll.
Unexplored: writable characteristics `0000ff02` and `00000003`/`8ec90001` (Nordic DFU service `fe59`).
Do **not** write to the DFU service; it may brick the transmitter.
