"""Sensor platform for Baby Link."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
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
    """Set up sensor platform."""
    coordinator: BabyLinkCoordinator = hass.data[DOMAIN][entry.entry_id]

    sensors = [
        BabyTodayFeedsSensor(coordinator, entry),
        BabyTodayDiapersSensor(coordinator, entry),
        BabyTodaySleepHoursSensor(coordinator, entry),
        BabyLastFeedSensor(coordinator, entry),
        BabyLastDiaperSensor(coordinator, entry),
    ]
    async_add_entities(sensors)


class BabyBaseSensor(CoordinatorEntity[BabyLinkCoordinator], SensorEntity):
    """Base class for Baby Link sensors."""

    _attr_has_entity_name = True

    def __init__(
        self, coordinator: BabyLinkCoordinator, entry: ConfigEntry, key: str
    ) -> None:
        """Initialize base sensor."""
        super().__init__(coordinator)
        
        baby_id = entry.data["baby_id"]
        baby_name = (
            coordinator.data.get("name", "Baby") if coordinator.data else "Baby"
        )

        self._attr_unique_id = f"{baby_id}_{key}"
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


class BabyTodayFeedsSensor(BabyBaseSensor):
    """Sensor for total feeds today."""

    _attr_icon = "mdi:baby-bottle"
    _attr_state_class = SensorStateClass.TOTAL_INCREASING

    def __init__(self, coordinator: BabyLinkCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, "today_feeds")
        self._attr_name = "Today Feeds"

    @property
    def native_value(self) -> int | None:
        if not self.coordinator.data:
            return None
        summary = self.coordinator.data.get("today_summary", {})
        return summary.get("total_feeds", 0)


class BabyTodayDiapersSensor(BabyBaseSensor):
    """Sensor for total diapers today."""

    _attr_icon = "mdi:human-baby-changing-table"
    _attr_state_class = SensorStateClass.TOTAL_INCREAS = SensorStateClass.TOTAL_INCREASING

    def __init__(self, coordinator: BabyLinkCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, "today_diapers")
        self._attr_name = "Today Diapers"

    @property
    def native_value(self) -> int | None:
        if not self.coordinator.data:
            return None
        summary = self.coordinator.data.get("today_summary", {})
        return summary.get("total_diapers", 0)


class BabyTodaySleepHoursSensor(BabyBaseSensor):
    """Sensor for sleep hours today."""

    _attr_icon = "mdi:clock-time-four-outline"
    _attr_native_unit_of_measurement = "h"
    _attr_state_class = SensorStateClass.TOTAL

    def __init__(self, coordinator: BabyLinkCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, "today_sleep_hours")
        self._attr_name = "Today Sleep Hours"

    @property
    def native_value(self) -> float | None:
        if not self.coordinator.data:
            return None
        summary = self.coordinator.data.get("today_summary", {})
        mins = summary.get("total_sleep_mins", 0)
        return round(mins / 60, 1)


class BabyLastFeedSensor(BabyBaseSensor):
    """Sensor timestamp for last feed."""

    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_icon = "mdi:clock-outline"

    def __init__(self, coordinator: BabyLinkCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, "last_feed_time")
        self._attr_name = "Last Feed Time"

    @property
    def native_value(self) -> datetime | None:
        if not self.coordinator.data:
            return None
        events = self.coordinator.data.get("last_events", {})
        time_str = events.get("last_feed", {}).get("time")
        if not time_str:
            return None
        return datetime.fromisoformat(time_str.replace("Z", "+00:00"))

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        if not self.coordinator.data:
            return None
        feed = self.coordinator.data.get("last_events", {}).get("last_feed", {})
        return {
            "type": feed.get("type", "unknown"),
            "amount_ml": feed.get("amount_ml", 0),
        }


class BabyLastDiaperSensor(BabyBaseSensor):
    """Sensor timestamp for last diaper."""

    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_icon = "mdi:clock-outline"

    def __init__(self, coordinator: BabyLinkCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, "last_diaper_time")
        self._attr_name = "Last Diaper Time"

    @property
    def native_value(self) -> datetime | None:
        if not self.coordinator.data:
            return None
        events = self.coordinator.data.get("last_events", {})
        time_str = events.get("last_diaper", {}).get("time")
        if not time_str:
            return None
        return datetime.fromisoformat(time_str.replace("Z", "+00:00"))

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        if not self.coordinator.data:
            return None
        diaper = self.coordinator.data.get("last_events", {}).get("last_diaper", {})
        return {
            "condition": diaper.get("condition", "unknown"),
        }