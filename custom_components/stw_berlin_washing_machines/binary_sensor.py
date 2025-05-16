from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api_parser import WashingMachine
from .const import DOMAIN
from .coordinator import WashingMachineCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry[WashingMachineCoordinator],
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor from config entry."""
    coordinator = entry.runtime_data

    occupied_entities = [
        WashingMachineOccupiedSensor(coordinator, machine)
        for machine in list(coordinator.data.values())
    ]

    async_add_entities(occupied_entities)


class WashingMachineOccupiedSensor(
    CoordinatorEntity[WashingMachineCoordinator], BinarySensorEntity
):
    _attr_device_class = BinarySensorDeviceClass.RUNNING

    def __init__(
        self, coordinator: WashingMachineCoordinator, machine: WashingMachine
    ) -> None:
        super().__init__(coordinator)
        self.machine_name = machine.name
        self.coordinator = coordinator
        self.machine = machine
        self._attr_unique_id = f"{DOMAIN}_{coordinator.dorm}_occupied_{machine.name}"
        self._attr_name = f"Is {machine.name} occupied"

        self._attr_device_info = DeviceInfo(
            # entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, coordinator.dorm, machine.name)},
            manufacturer="STW Berlin",
            name=machine.name,
        )

    @property
    def is_on(self):
        return self.coordinator.data[self.machine_name].is_occupied
