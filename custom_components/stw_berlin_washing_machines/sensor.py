from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType
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

    async_add_entities([WashingMachinesFreeCountSensor(coordinator)])

    time_remaining_entities = [
        WashingMachineTimeRemainingSensor(coordinator, machine)
        for machine in list(coordinator.data.values())
    ]

    async_add_entities(time_remaining_entities)


class WashingMachineTimeRemainingSensor(
    CoordinatorEntity[WashingMachineCoordinator], SensorEntity
):
    """Sensor showing number of time remaining for washing machines."""

    _attr_device_class = SensorDeviceClass.DURATION
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self, coordinator: WashingMachineCoordinator, machine: WashingMachine
    ) -> None:
        super().__init__(coordinator)
        self.machine_name = machine.name
        self.coordinator = coordinator
        self.machine = machine
        self._attr_unique_id = (
            f"{DOMAIN}_{coordinator.dorm}_time_remaining_{machine.name}"
        )
        self._attr_name = f"Time Remaining for Machine {machine.name}"

        self._attr_device_info = DeviceInfo(
            # entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, coordinator.dorm, machine.name)},
            manufacturer="STW Berlin",
            name=machine.name,
        )

    @property
    def native_value(self):
        return self.coordinator.data[self.machine_name].duration_minutes


class WashingMachinesFreeCountSensor(
    CoordinatorEntity[WashingMachineCoordinator], SensorEntity
):
    """Sensor showing number of free washing machines."""

    _attr_name = "Number of free Washing Machines"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        coordinator: WashingMachineCoordinator,
    ) -> None:
        super().__init__(coordinator)
        self.coordinator = coordinator
        self._attr_unique_id = f"{DOMAIN}_{coordinator.dorm}_free_count"

        self._attr_device_info = DeviceInfo(
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, coordinator.dorm)},
            manufacturer="STW Berlin",
            name="STW Berlin Washing Machines",
        )

    @property
    def native_value(self):
        return sum(
            not machine.is_occupied for machine in list(self.coordinator.data.values())
        )
