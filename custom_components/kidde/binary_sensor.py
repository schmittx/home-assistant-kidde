"""Support for Kidde binary sensor entities."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import KiddeEntity
from .const import CONF_DEVICES, CONF_LOCATIONS, DATA_COORDINATOR, DOMAIN


@dataclass(frozen=True)
class KiddeBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Class to describe a Kidde binary sensor entity."""

    entity_category: EntityCategory | None = None


BINARY_SENSOR_DESCRIPTIONS: list[KiddeBinarySensorEntityDescription] = [
    KiddeBinarySensorEntityDescription(
        key="co_alarm",
        name="CO Alarm",
        device_class=BinarySensorDeviceClass.CO,
    ),
    KiddeBinarySensorEntityDescription(
        key="hardwire_co",
        name="Hardwire CO",
        device_class=BinarySensorDeviceClass.CO,
    ),
    KiddeBinarySensorEntityDescription(
        key="hardwire_smoke",
        name="Hardwire Smoke",
        device_class=BinarySensorDeviceClass.SMOKE,
    ),
    KiddeBinarySensorEntityDescription(
        key="low_battery",
        name="Low Battery",
        device_class=BinarySensorDeviceClass.BATTERY,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    KiddeBinarySensorEntityDescription(
        key="online",
        name="Online",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
    ),
    KiddeBinarySensorEntityDescription(
        key="smoke_alarm",
        name="Smoke Alarm",
        device_class=BinarySensorDeviceClass.SMOKE,
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up a Kidde binary sensor entity based on a config entry."""
    entry = hass.data[DOMAIN][config_entry.entry_id]
    coordinator = entry[DATA_COORDINATOR]
    entities: list[KiddeBinarySensorEntity] = []

    for location in coordinator.data:
        if location.id in entry[CONF_LOCATIONS]:
            for device in location.devices:
                if device.id in entry[CONF_DEVICES]:
                    entities.extend(
                        KiddeBinarySensorEntity(
                            coordinator=coordinator,
                            location_id=location.id,
                            device_id=device.id,
                            entity_description=description,
                        )
                        for description in BINARY_SENSOR_DESCRIPTIONS
                        if hasattr(device, description.key)
                    )

    async_add_entities(entities)


class KiddeBinarySensorEntity(BinarySensorEntity, KiddeEntity):
    """Representation of a Kidde binary sensor entity."""

    entity_description: KiddeBinarySensorEntityDescription

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        return getattr(self.device, self.entity_description.key)
