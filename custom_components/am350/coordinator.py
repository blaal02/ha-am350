"""Holds a BLE connection to the AM350 transmitter and pushes tilt data."""
from __future__ import annotations

import asyncio
import logging

from bleak_retry_connector import BleakClientWithServiceCache, establish_connection
from homeassistant.components import bluetooth
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import CALLBACK_TYPE, HomeAssistant, callback
from homeassistant.helpers.event import async_call_later
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import CONF_X_OFFSET, CONF_Y_OFFSET
from .protocol import NOTIFY_CHAR_UUID, AM350Data, parse_notification

_LOGGER = logging.getLogger(__name__)

PUSH_INTERVAL = 1.0     # seconds; the device notifies many times per second
RECONNECT_DELAY = 10.0


class AM350Coordinator(DataUpdateCoordinator[AM350Data | None]):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, address: str) -> None:
        super().__init__(hass, _LOGGER, name=f"AM350 {address}", config_entry=entry)
        self.address = address
        self.title = entry.title
        self.connected = False
        self.data = None
        self.raw: AM350Data | None = None  # uncalibrated, degrees
        self._entry = entry
        self._flush_unsub: CALLBACK_TYPE | None = None

    @property
    def offsets(self) -> tuple[float, float]:
        o = self._entry.options
        return o.get(CONF_X_OFFSET, 0.0), o.get(CONF_Y_OFFSET, 0.0)

    def _device(self):
        return bluetooth.async_ble_device_from_address(
            self.hass, self.address, connectable=True
        )

    @callback
    def _set_connected(self, value: bool) -> None:
        if self.connected != value:
            self.connected = value
            self.async_update_listeners()

    @callback
    def _on_notify(self, _char, payload: bytearray) -> None:
        if (parsed := parse_notification(payload)) is None:
            _LOGGER.debug("Ignoring unrecognised packet: %s", payload.hex())
            return
        self.raw = parsed
        if self.data is None:
            self._flush()
        elif self._flush_unsub is None:
            self._flush_unsub = async_call_later(self.hass, PUSH_INTERVAL, self._flush)

    @callback
    def _flush(self, _now=None) -> None:
        self._flush_unsub = None
        if self.raw is None:
            return
        ox, oy = self.offsets
        calibrated = AM350Data(round(self.raw.x - ox, 1), round(self.raw.y - oy, 1))
        if calibrated != self.data:
            self.async_set_updated_data(calibrated)

    @callback
    def async_apply_options(self) -> None:
        """Re-publish the last reading using the current offsets."""
        self._flush()

    @callback
    def stop(self) -> None:
        if self._flush_unsub:
            self._flush_unsub()
            self._flush_unsub = None

    async def run(self) -> None:
        """Connect, subscribe, and reconnect forever (cancelled on unload)."""
        while True:
            client = None
            disconnected = asyncio.Event()
            try:
                if (device := self._device()) is None:
                    _LOGGER.debug("%s not in range", self.address)
                else:
                    client = await establish_connection(
                        BleakClientWithServiceCache,
                        device,
                        self.title,
                        disconnected_callback=lambda _c: disconnected.set(),
                        ble_device_callback=self._device,
                    )
                    await client.start_notify(NOTIFY_CHAR_UUID, self._on_notify)
                    self._set_connected(True)
                    await disconnected.wait()
            except asyncio.CancelledError:
                raise
            except Exception as err:  # noqa: BLE001
                _LOGGER.debug("Connection to %s failed: %s", self.address, err)
            finally:
                self._set_connected(False)
                if client is not None:
                    try:
                        await client.disconnect()
                    except Exception:  # noqa: BLE001
                        pass
            await asyncio.sleep(RECONNECT_DELAY)
