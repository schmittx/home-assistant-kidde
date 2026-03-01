"""Support for Kidde sensor entities."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import SIGNAL_STRENGTH_DECIBELS_MILLIWATT
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

from . import KiddeEntity
from .const import CONF_DEVICES, CONF_LOCATIONS, DATA_COORDINATOR, DOMAIN


@dataclass(frozen=True)
class KiddeSensorEntityDescription(SensorEntityDescription):
    """Class to describe a Kidde sensor entity."""

    entity_category: EntityCategory | None = EntityCategory.DIAGNOSTIC


SENSOR_DESCRIPTIONS: list[KiddeSensorEntityDescription] = [
    KiddeSensorEntityDescription(
        key="last_seen",
        name="Last Seen",
        device_class=SensorDeviceClass.TIMESTAMP,
    ),
    KiddeSensorEntityDescription(
        key="signal_strength",
        name="Signal Strength",
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up a Kidde sensor entity based on a config entry."""
    entry = hass.data[DOMAIN][config_entry.entry_id]
    coordinator = entry[DATA_COORDINATOR]
    entities: list[KiddeSensorEntity] = []

    for location in coordinator.data:
        if location.id in entry[CONF_LOCATIONS]:
            for device in location.devices:
                if device.id in entry[CONF_DEVICES]:
                    entities.extend(
                        KiddeSensorEntity(
                            coordinator=coordinator,
                            location_id=location.id,
                            device_id=device.id,
                            entity_description=description,
                        )
                        for description in SENSOR_DESCRIPTIONS
                        if hasattr(device, description.key)
                    )

    async_add_entities(entities)


class KiddeSensorEntity(SensorEntity, KiddeEntity):
    """Representation of a Kidde sensor entity."""

    entity_description: KiddeSensorEntityDescription

    @property
    def native_value(self) -> StateType | date | datetime:
        """Return the value reported by the sensor."""
        return getattr(self.device, self.entity_description.key)
