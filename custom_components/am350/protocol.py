"""AM350 (BLE name "AMS350-RV-TX") notification decoding.

Reverse-engineered from captures. Characteristic 0000ff03-... notifies 7 bytes:

    03 03 | X (int16 LE) | Y (int16 LE) | checksum
    checksum = sum(bytes[0:6]) & 0xFF   (verified on every captured packet)

ASSUMPTIONS TO VERIFY WITH A KNOWN ANGLE:
  * ANGLE_SCALE: raw unit -> degrees (0.1 is a guess)
  * which axis is front/back vs side/side
"""
from __future__ import annotations

import struct
from dataclasses import dataclass

NOTIFY_CHAR_UUID = "0000ff03-0000-1000-8000-00805f9b34fb"
LOCAL_NAME_PREFIX = "AMS350"
ANGLE_SCALE = 0.1


@dataclass(frozen=True)
class AM350Data:
    x: float
    y: float


def parse_notification(data: bytes | bytearray) -> AM350Data | None:
    if len(data) != 7 or data[0] != 0x03 or data[1] != 0x03:
        return None
    if (sum(data[:6]) & 0xFF) != data[6]:
        return None
    x, y = struct.unpack_from("<hh", data, 2)
    return AM350Data(round(x * ANGLE_SCALE, 1), round(y * ANGLE_SCALE, 1))
