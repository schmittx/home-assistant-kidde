"""Support for Kidde time entities."""

from dataclasses import dataclass
from datetime import time

from homeassistant.components.time import TimeEntity, TimeEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import KiddeEntity
from .const import CONF_DEVICES, CONF_LOCATIONS, DATA_COORDINATOR, DOMAIN


@dataclass(frozen=True)
class KiddeTimeEntityDescription(TimeEntityDescription):
    """Class to describe a Kidde time entity."""

    entity_category: EntityCategory | None = EntityCategory.CONFIG


TIME_DESCRIPTIONS: list[KiddeTimeEntityDescription] = [
    KiddeTimeEntityDescription(
        key="no_chirp_on_time",
        name="No Chirp On Time",
    ),
    KiddeTimeEntityDescription(
        key="no_chirp_off_time",
        name="No Chirp Off Time",
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up a Kidde time entity based on a config entry."""
    entry = hass.data[DOMAIN][config_entry.entry_id]
    coordinator = entry[DATA_COORDINATOR]
    entities: list[KiddeTimeEntity] = []

    for location in coordinator.data.locations:
        if location.id in entry[CONF_LOCATIONS]:
            for device in location.devices:
                if device.id in entry[CONF_DEVICES]:
                    entities.extend(
                        KiddeTimeEntity(
                            coordinator=coordinator,
                            location_id=location.id,
                            device_id=device.id,
                            entity_description=description,
                        )
                        for description in TIME_DESCRIPTIONS
                        if hasattr(device, description.key)
                    )

    async_add_entities(entities)


class KiddeTimeEntity(TimeEntity, KiddeEntity):
    """Representation of a Kidde time entity."""

    entity_description: KiddeTimeEntityDescription

    @property
    def native_value(self) -> time | None:
        """Return the value reported by the time."""
        return getattr(self.device, self.entity_description.key)

    async def async_set_value(self, value: time) -> None:
        """Change the time."""
        if self.device:
            await self.device.set_property(self.entity_description.key, value)
            self.async_write_ha_state()
            await self.coordinator.async_request_refresh()
