"""AM350 RV Leveler integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ADDRESS, Platform
from homeassistant.core import HomeAssistant

from .coordinator import AM350Coordinator

PLATFORMS = [Platform.SENSOR]
type AM350ConfigEntry = ConfigEntry[AM350Coordinator]


async def async_setup_entry(hass: HomeAssistant, entry: AM350ConfigEntry) -> bool:
    coordinator = AM350Coordinator(hass, entry, entry.data[CONF_ADDRESS])
    entry.runtime_data = coordinator
    entry.async_on_unload(coordinator.stop)
    entry.async_on_unload(entry.add_update_listener(_options_updated))
    entry.async_create_background_task(
        hass, coordinator.run(), f"am350 {coordinator.address}"
    )
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: AM350ConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def _options_updated(hass: HomeAssistant, entry: AM350ConfigEntry) -> None:
    entry.runtime_data.async_apply_options()
