"""Support for Kidde switch entities."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import KiddeEntity
from .const import CONF_DEVICES, CONF_LOCATIONS, DATA_COORDINATOR, DOMAIN


@dataclass(frozen=True)
class KiddeSwitchEntityDescription(SwitchEntityDescription):
    """Class to describe a Kidde switch entity."""

    entity_category: EntityCategory | None = EntityCategory.CONFIG


SWITCH_DESCRIPTIONS: list[KiddeSwitchEntityDescription] = [
    KiddeSwitchEntityDescription(
        key="no_chirp_enabled",
        name="No Chirp Enabled",
    ),
    KiddeSwitchEntityDescription(
        key="notify_contact",
        name="Notify Contact",
    ),
    KiddeSwitchEntityDescription(
        key="notify_eol",
        name="Notify EOL",
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up a Kidde switch entity based on a config entry."""
    entry = hass.data[DOMAIN][config_entry.entry_id]
    coordinator = entry[DATA_COORDINATOR]
    entities: list[KiddeSwitchEntity] = []

    for location in coordinator.data:
        if location.id in entry[CONF_LOCATIONS]:
            for device in location.devices:
                if device.id in entry[CONF_DEVICES]:
                    entities.extend(
                        KiddeSwitchEntity(
                            coordinator=coordinator,
                            location_id=location.id,
                            device_id=device.id,
                            entity_description=description,
                        )
                        for description in SWITCH_DESCRIPTIONS
                        if hasattr(device, description.key)
                    )

    async_add_entities(entities)


class KiddeSwitchEntity(SwitchEntity, KiddeEntity):
    """Representation of a Kidde switch entity."""

    entity_description: KiddeSwitchEntityDescription

    @property
    def is_on(self) -> bool:
        """Return True if entity is on."""
        return getattr(self.device, self.entity_description.key)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the entity on."""
        if self.device:
            await self.device.set_property(self.entity_description.key, True)
            await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the entity off."""
        if self.device:
            await self.device.set_property(self.entity_description.key, False)
            await self.coordinator.async_request_refresh()
