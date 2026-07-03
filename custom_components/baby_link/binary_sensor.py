"""Binary sensor platform for Baby Link."""
from __future__ import annotations

from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import BabyLinkCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up binary sensor platform."""
    coordinator: BabyLinkCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([BabySleepingBinarySensor(coordinator, entry)])


class BabySleepingBinarySensor(
    CoordinatorEntity[BabyLinkCoordinator], BinarySensorEntity
):
    """Representation of a Baby Sleeping binary sensor."""

    _attr_device_class = BinarySensorDeviceClass.OCCUPANCY
    _attr_icon = "mdi:sleep"
    _attr_has_entity_name = True

    def __init__(self, coordinator: BabyLinkCoordinator, entry: ConfigEntry) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        
        baby_id = entry.data["baby_id"]
        baby_name = (
            coordinator.data.get("name", "Baby") if coordinator.data else "Baby"
        )

        self._attr_unique_id = f"{baby_id}_is_sleeping"
        self._attr_name = "Sleeping"

        # Agrupa la entidad dentro del dispositivo principal en HA
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, baby_id)},
            name=baby_name,
            manufacturer="Baby Link",
            model="Baby Link",
        )

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return super().available and self.coordinator.data is not None

    @property
    def is_on(self) -> bool | None:
        """Return true if the baby is currently sleeping."""
        if not self.coordinator.data:
            return None
            
        current = self.coordinator.data.get("current_state", {})
        return current.get("is_sleeping", False)

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return extra state attributes."""
        if not self.coordinator.data:
            return None

        current = self.coordinator.data.get("current_state", {})
        is_sleeping = current.get("is_sleeping", False)

        return {
            "sleep_type": current.get("current_sleep_type", "Awake"),
            "sleeping_since": current.get("sleeping_since") if is_sleeping else None,
        }