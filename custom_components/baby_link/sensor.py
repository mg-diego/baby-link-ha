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
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import BabyTrackerCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensor platform."""
    coordinator: BabyTrackerCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    sensors = [
        BabyTodayFeedsSensor(coordinator, entry),
        BabyTodayDiapersSensor(coordinator, entry),
        BabyTodaySleepHoursSensor(coordinator, entry),
        BabyLastFeedSensor(coordinator, entry),
        BabyLastDiaperSensor(coordinator, entry),
    ]
    async_add_entities(sensors)


class BabyBaseSensor(CoordinatorEntity[BabyTrackerCoordinator], SensorEntity):
    """Base class for Baby Link sensors."""

    def __init__(self, coordinator: BabyTrackerCoordinator, entry: ConfigEntry, key: str) -> None:
        """Initialize base sensor."""
        super().__init__(coordinator)
        baby_name = coordinator.data.get("name", "Baby")
        self._attr_unique_id = f"{entry.data['baby_id']}_{key}"
        self.baby_name = baby_name


class BabyTodayFeedsSensor(BabyBaseSensor):
    """Sensor for total feeds today."""

    _attr_icon = "mdi:baby-bottle"
    _attr_state_class = SensorStateClass.TOTAL_INCREASING

    def __init__(self, coordinator: BabyTrackerCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, "today_feeds")
        self._attr_name = f"{self.baby_name} Today Feeds"

    @property
    def native_value(self) -> int:
        summary = self.coordinator.data.get("today_summary", {})
        return summary.get("total_feeds", 0)


class BabyTodayDiapersSensor(BabyBaseSensor):
    """Sensor for total diapers today."""

    _attr_icon = "mdi:human-baby-changing-table"
    _attr_state_class = SensorStateClass.TOTAL_INCREASING

    def __init__(self, coordinator: BabyTrackerCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, "today_diapers")
        self._attr_name = f"{self.baby_name} Today Diapers"

    @property
    def native_value(self) -> int:
        summary = self.coordinator.data.get("today_summary", {})
        return summary.get("total_diapers", 0)


class BabyTodaySleepHoursSensor(BabyBaseSensor):
    """Sensor for sleep hours today."""

    _attr_icon = "mdi:clock-time-four-outline"
    _attr_native_unit_of_measurement = "h"
    _attr_state_class = SensorStateClass.TOTAL

    def __init__(self, coordinator: BabyTrackerCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, "today_sleep_hours")
        self._attr_name = f"{self.baby_name} Today Sleep Hours"

    @property
    def native_value(self) -> float:
        summary = self.coordinator.data.get("today_summary", {})
        mins = summary.get("total_sleep_mins", 0)
        return round(mins / 60, 1)


class BabyLastFeedSensor(BabyBaseSensor):
    """Sensor timestamp for last feed."""

    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_icon = "mdi:clock-outline"

    def __init__(self, coordinator: BabyTrackerCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, "last_feed_time")
        self._attr_name = f"{self.baby_name} Last Feed Time"

    @property
    def native_value(self) -> datetime | None:
        events = self.coordinator.data.get("last_events", {})
        time_str = events.get("last_feed", {}).get("time")
        if not time_str:
            return None
        return datetime.fromisoformat(time_str.replace("Z", "+00:00"))

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        feed = self.coordinator.data.get("last_events", {}).get("last_feed", {})
        return {
            "type": feed.get("type", "unknown"),
            "amount_ml": feed.get("amount_ml", 0),
        }


class BabyLastDiaperSensor(BabyBaseSensor):
    """Sensor timestamp for last diaper."""

    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_icon = "mdi:clock-outline"

    def __init__(self, coordinator: BabyTrackerCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, "last_diaper_time")
        self._attr_name = f"{self.baby_name} Last Diaper Time"

    @property
    def native_value(self) -> datetime | None:
        events = self.coordinator.data.get("last_events", {})
        time_str = events.get("last_diaper", {}).get("time")
        if not time_str:
            return None
        return datetime.fromisoformat(time_str.replace("Z", "+00:00"))

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        diaper = self.coordinator.data.get("last_events", {}).get("last_diaper", {})
        return {
            "condition": diaper.get("condition", "unknown"),
        }