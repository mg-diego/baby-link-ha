"""Binary sensor platform for Baby Link."""
from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import BabyTrackerCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up binary sensor platform."""
    coordinator: BabyTrackerCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([BabySleepingBinarySensor(coordinator, entry)])


class BabySleepingBinarySensor(CoordinatorEntity[BabyTrackerCoordinator], BinarySensorEntity):
    """Representation of a Baby Sleeping binary sensor."""

    _attr_device_class = BinarySensorDeviceClass.OCCUPANCY
    _attr_icon = "mdi:sleep"

    def __init__(self, coordinator: BabyTrackerCoordinator, entry: ConfigEntry) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.data['baby_id']}_is_sleeping"
        self._attr_name = f"{coordinator.data.get('name', 'Baby')} Sleeping"

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        current = self.coordinator.data.get("current_state", {})
        return current.get("is_sleeping", False)

    @property
    def extra_state_attributes(self) -> dict[str, str] | None:
        """Return extra state attributes."""
        current = self.coordinator.data.get("current_state", {})
        return {
            "sleep_type": current.get("current_sleep_type", "Unknown"),
            "sleeping_since": current.get("sleeping_since", ""),
        }