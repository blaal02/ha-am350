"""Reverse-engineering helper. Run on any machine with Bluetooth: pip install bleak

1. python capture.py scan            -> find the AM350, note its address/name
2. python capture.py adv <ADDR>      -> print raw advertisement bytes live
3. python capture.py gatt <ADDR>     -> list services/characteristics, subscribe to notifies

Tilt the transmitter to known angles (level, nose up, left side up) and note
which bytes change. Send me those samples and I'll finish protocol.py.
"""
import asyncio, sys
try:
    from bleak import BleakClient, BleakScanner
except ImportError:
    sys.exit("bleak is not installed. Run: pip install bleak   (or: pip install -r requirements.txt)")


async def scan():
    for d, a in (await BleakScanner.discover(timeout=10, return_adv=True)).values():
        print(d.address, repr(d.name), a.rssi, dict(a.manufacturer_data), dict(a.service_data))


async def adv(addr):
    def cb(d, a):
        if d.address.lower() == addr.lower():
            print(a.rssi, {k: v.hex() for k, v in a.manufacturer_data.items()},
                  {k: v.hex() for k, v in a.service_data.items()})
    async with BleakScanner(cb):
        await asyncio.sleep(60)


async def gatt(addr):
    async with BleakClient(addr) as c:
        for s in c.services:
            print("SERVICE", s.uuid)
            for ch in s.characteristics:
                val = ""
                if "read" in ch.properties:
                    try: val = (await c.read_gatt_char(ch)).hex()
                    except Exception as e: val = f"<{e}>"
                print("  ", ch.uuid, ch.properties, val)
                if "notify" in ch.properties:
                    await c.start_notify(ch, lambda _, d, u=ch.uuid: print("NOTIFY", u, d.hex()))
        await asyncio.sleep(30)


cmd, *arg = sys.argv[1:] or ["scan"]
asyncio.run({"scan": scan, "adv": adv, "gatt": gatt}[cmd](*arg))
