"""Config flow: pick the AM350 transmitter from discovered Bluetooth devices."""
from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.components.bluetooth import (
    BluetoothServiceInfoBleak,
    async_discovered_service_info,
)
from homeassistant.config_entries import ConfigEntry, ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.core import callback
from homeassistant.helpers.selector import (
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
)
from homeassistant.const import CONF_ADDRESS

from .const import CONF_SET_TO_CURRENT, CONF_X_OFFSET, CONF_Y_OFFSET, DOMAIN
from .protocol import LOCAL_NAME_PREFIX


class AM350ConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        return AM350OptionsFlow()

    def __init__(self) -> None:
        self._discovered: dict[str, str] = {}

    async def async_step_bluetooth(
        self, discovery_info: BluetoothServiceInfoBleak
    ) -> ConfigFlowResult:
        await self.async_set_unique_id(discovery_info.address)
        self._abort_if_unique_id_configured()
        self.context["title_placeholders"] = {"name": discovery_info.name}
        self._discovered = {discovery_info.address: discovery_info.name}
        return await self.async_step_user()

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            address = user_input[CONF_ADDRESS]
            await self.async_set_unique_id(address, raise_on_progress=False)
            self._abort_if_unique_id_configured()
            name = self._discovered.get(address, address)
            return self.async_create_entry(title=name, data={CONF_ADDRESS: address})

        current = self._async_current_ids()
        for info in async_discovered_service_info(self.hass, True):
            if info.address not in current and (info.name or "").startswith(LOCAL_NAME_PREFIX):
                self._discovered[info.address] = f"{info.name} ({info.address})"
        if not self._discovered:
            return self.async_abort(reason="no_devices_found")
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_ADDRESS): vol.In(self._discovered)}),
        )


_ANGLE = NumberSelector(
    NumberSelectorConfig(
        min=-45, max=45, step=0.1, mode=NumberSelectorMode.BOX, unit_of_measurement="°"
    )
)


class AM350OptionsFlow(OptionsFlow):
    """Calibration offsets, subtracted from the received angles."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        opts = self.config_entry.options

        if user_input is not None:
            if user_input.get(CONF_SET_TO_CURRENT):
                raw = getattr(self.config_entry.runtime_data, "raw", None)
                if raw is None:
                    errors["base"] = "no_reading"
                else:
                    return self.async_create_entry(
                        data={CONF_X_OFFSET: raw.x, CONF_Y_OFFSET: raw.y}
                    )
            else:
                return self.async_create_entry(
                    data={
                        CONF_X_OFFSET: user_input[CONF_X_OFFSET],
                        CONF_Y_OFFSET: user_input[CONF_Y_OFFSET],
                    }
                )

        schema = vol.Schema(
            {
                vol.Required(CONF_X_OFFSET, default=opts.get(CONF_X_OFFSET, 0.0)): _ANGLE,
                vol.Required(CONF_Y_OFFSET, default=opts.get(CONF_Y_OFFSET, 0.0)): _ANGLE,
                vol.Optional(CONF_SET_TO_CURRENT, default=False): bool,
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema, errors=errors)
