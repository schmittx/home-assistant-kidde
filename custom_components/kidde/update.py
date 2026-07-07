"""Support for Kidde update entities."""

from dataclasses import dataclass

from homeassistant.components.update import (
    UpdateDeviceClass,
    UpdateEntity,
    UpdateEntityDescription,
    UpdateEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import KiddeEntity
from .const import CONF_DEVICES, CONF_LOCATIONS, DATA_COORDINATOR, DOMAIN


@dataclass(frozen=True)
class KiddeUpdateEntityDescription(UpdateEntityDescription):
    """Class to describe a Kidde update entity."""

    device_class: UpdateDeviceClass | None = UpdateDeviceClass.FIRMWARE
    entity_category: EntityCategory | None = EntityCategory.CONFIG


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up a Kidde update entity based on a config entry."""
    entry = hass.data[DOMAIN][config_entry.entry_id]
    coordinator = entry[DATA_COORDINATOR]
    entities: list[KiddeUpdateEntity] = []

    for location in coordinator.data.locations:
        if location.id in entry[CONF_LOCATIONS]:
            entities.extend(
                KiddeUpdateEntity(
                    coordinator=coordinator,
                    location_id=location.id,
                    device_id=device.id,
                    entity_description=KiddeUpdateEntityDescription(
                        key="update",
                        name="Firmware",
                    ),
                )
                for device in location.devices
                if device.id in entry[CONF_DEVICES]
            )

    async_add_entities(entities)


class KiddeUpdateEntity(UpdateEntity, KiddeEntity):
    """Representation of a Kidde update entity."""

    entity_description: KiddeUpdateEntityDescription

    @property
    def installed_version(self) -> str | None:
        """Version installed and in use."""
        return self.device.firmware_version if self.device else None

    @property
    def latest_version(self) -> str | None:
        """Latest version available for install."""
        return self.firmware.mb_rev if self.firmware else None

    @property
    def release_summary(self) -> str | None:
        """Summary of the release notes or changelog.

        This is not suitable for long changelogs, but merely suitable
        for a short excerpt update description of max 255 characters.
        """
        return None

    def release_notes(self) -> str | None:
        """Return full release notes.

        This is suitable for a long changelog that does not fit in the release_summary property.
        The returned string can contain markdown.
        """
        return self.release_summary

    @property
    def release_url(self) -> str | None:
        """URL to the full release notes of the latest version available."""
        return None

    @property
    def supported_features(self) -> UpdateEntityFeature:
        """Flag supported features."""
        return UpdateEntityFeature(0)
