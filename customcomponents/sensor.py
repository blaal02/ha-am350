"""AM350 tilt sensors."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import DEGREE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import CONNECTION_BLUETOOTH, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import AM350ConfigEntry
from .const import DOMAIN
from .coordinator import AM350Coordinator

DESCRIPTIONS = (
    SensorEntityDescription(
        key="x", translation_key="tilt_x", native_unit_of_measurement=DEGREE,
        state_class=SensorStateClass.MEASUREMENT, icon="mdi:angle-acute",
    ),
    SensorEntityDescription(
        key="y", translation_key="tilt_y", native_unit_of_measurement=DEGREE,
        state_class=SensorStateClass.MEASUREMENT, icon="mdi:angle-obtuse",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: AM350ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coord = entry.runtime_data
    async_add_entities(AM350Sensor(coord, d) for d in DESCRIPTIONS)


class AM350Sensor(CoordinatorEntity[AM350Coordinator], SensorEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator: AM350Coordinator, description: SensorEntityDescription):
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.address}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.address)},
            connections={(CONNECTION_BLUETOOTH, coordinator.address)},
            name=coordinator.title, manufacturer="AOMOSUR", model="AM350 (AMS350-RV-TX)",
        )

    @property
    def native_value(self):
        data = self.coordinator.data
        return getattr(data, self.entity_description.key) if data else None

    @property
    def available(self) -> bool:
        return self.coordinator.connected and self.coordinator.data is not None
