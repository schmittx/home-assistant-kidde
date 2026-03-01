"""Support for Kidde button entities."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.button import (
    ButtonDeviceClass,
    ButtonEntity,
    ButtonEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import KiddeEntity
from .const import CONF_DEVICES, CONF_LOCATIONS, DATA_COORDINATOR, DOMAIN


@dataclass(frozen=True)
class KiddeButtonEntityDescription(ButtonEntityDescription):
    """Class to describe a Kidde button entity."""

    entity_category: EntityCategory | None = EntityCategory.DIAGNOSTIC


BUTTON_DESCRIPTIONS: list[KiddeButtonEntityDescription] = [
    KiddeButtonEntityDescription(
        key="hush",
        name="Hush",
        entity_category=EntityCategory.CONFIG,
    ),
    KiddeButtonEntityDescription(
        key="identify",
        name="Identify",
        device_class=ButtonDeviceClass.IDENTIFY,
    ),
    KiddeButtonEntityDescription(
        key="test",
        name="Test",
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up a Kidde button entity based on a config entry."""
    entry = hass.data[DOMAIN][config_entry.entry_id]
    coordinator = entry[DATA_COORDINATOR]
    entities: list[KiddeButtonEntity] = []

    for location in coordinator.data:
        if location.id in entry[CONF_LOCATIONS]:
            for device in location.devices:
                if device.id in entry[CONF_DEVICES]:
                    entities.extend(
                        KiddeButtonEntity(
                            coordinator=coordinator,
                            location_id=location.id,
                            device_id=device.id,
                            entity_description=description,
                        )
                        for description in BUTTON_DESCRIPTIONS
                        if hasattr(device, description.key)
                    )

    async_add_entities(entities)


class KiddeButtonEntity(ButtonEntity, KiddeEntity):
    """Representation of a Kidde button entity."""

    entity_description: KiddeButtonEntityDescription

    async def async_press(self) -> None:
        """Press the button."""
        await getattr(self.device, self.entity_description.key)()
        await self.coordinator.async_request_refresh()
