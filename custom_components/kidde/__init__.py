"""The Kidde integration."""

from __future__ import annotations

from asyncio import timeout
from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_EMAIL, CONF_SCAN_INTERVAL, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from .api import KiddeAPI, KiddeAPIAuthError
from .api.device import Device as KiddeDevice
from .api.location import Location as KiddeLocation
from .const import (
    CONF_COOKIES,
    CONF_DEVICES,
    CONF_LOCATIONS,
    CONF_SAVE_RESPONSES,
    CONF_TIMEOUT,
    DATA_COORDINATOR,
    DEFAULT_SAVE_LOCATION,
    DEFAULT_SAVE_RESPONSES,
    DEVICE_MANUFACTURER,
    DOMAIN,
    UNDO_UPDATE_LISTENER,
    ScanInterval,
    Timeout,
)

PLATFORMS = (Platform.BINARY_SENSOR, Platform.BUTTON, Platform.SENSOR, Platform.SWITCH)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up a config entry."""
    data = config_entry.data
    options = config_entry.options

    conf_locations = options.get(CONF_LOCATIONS, data.get(CONF_LOCATIONS, []))
    conf_devices = options.get(CONF_DEVICES, data.get(CONF_DEVICES, []))
    conf_identifiers = [(DOMAIN, conf_id) for conf_id in conf_locations + conf_devices]

    device_registry = dr.async_get(hass)
    device_entries = dr.async_entries_for_config_entry(
        registry=device_registry,
        config_entry_id=config_entry.entry_id,
    )
    for device_entry in device_entries:
        orphan_identifiers = [
            bool(device_identifier not in conf_identifiers)
            for device_identifier in device_entry.identifiers
        ]
        if all(orphan_identifiers):
            device_registry.async_remove_device(device_entry.id)

    api = KiddeAPI(
        cookies=data[CONF_COOKIES],
        save_location=DEFAULT_SAVE_LOCATION
        if options.get(CONF_SAVE_RESPONSES, DEFAULT_SAVE_RESPONSES)
        else None,
    )

    async def async_update_data() -> list[KiddeLocation]:
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """
        try:
            async with timeout(
                options.get(CONF_TIMEOUT, data.get(CONF_TIMEOUT, Timeout.DEFAULT))
            ):
                return await api.update(target_locations=conf_locations)
        except KiddeAPIAuthError as exception:
            raise ConfigEntryAuthFailed from exception
        except Exception as exception:
            raise UpdateFailed(
                f"{type(exception).__name__} while communicating with API: {exception}"
            ) from exception

    coordinator = DataUpdateCoordinator(
        hass=hass,
        logger=_LOGGER,
        name=f"Kidde ({data[CONF_EMAIL]})",
        update_method=async_update_data,
        update_interval=timedelta(
            seconds=options.get(CONF_SCAN_INTERVAL, ScanInterval.DEFAULT)
        ),
    )
    await coordinator.async_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][config_entry.entry_id] = {
        CONF_LOCATIONS: conf_locations,
        CONF_DEVICES: conf_devices,
        DATA_COORDINATOR: coordinator,
        UNDO_UPDATE_LISTENER: config_entry.add_update_listener(async_update_listener),
    }

    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(
        entry=config_entry,
        platforms=PLATFORMS,
    )
    if unload_ok:
        hass.data[DOMAIN][config_entry.entry_id][UNDO_UPDATE_LISTENER]()
        hass.data[DOMAIN].pop(config_entry.entry_id)

    return unload_ok


async def async_update_listener(hass: HomeAssistant, config_entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(config_entry.entry_id)


class KiddeEntity(CoordinatorEntity):
    """Representation of a Kidde entity."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        location_id: int,
        device_id: int,
        entity_description: EntityDescription | None = None,
    ) -> None:
        """Initialize the device."""
        super().__init__(coordinator)
        self.location_id = location_id
        self.device_id = device_id
        if entity_description:
            self.entity_description = entity_description

    @property
    def location(self) -> KiddeLocation | None:
        """Return a KiddeLocation object."""
        data: list[KiddeLocation] = self.coordinator.data  # pyright: ignore[reportAssignmentType]
        systems = {system.id: system for system in data}
        return systems.get(self.location_id)

    @property
    def device(self) -> KiddeDevice | None:
        """Return a KiddeDevice object."""
        devices = (
            {device.id: device for device in self.location.devices}
            if self.location
            else {}
        )
        return devices.get(self.device_id)

    @property
    def device_info(self) -> dr.DeviceInfo | None:
        """Return device specific attributes.

        Implemented by platform classes.
        """
        if self.device:
            return dr.DeviceInfo(
                hw_version=self.device.alarm_version,
                identifiers={(DOMAIN, str(self.device.id))},
                manufacturer=DEVICE_MANUFACTURER,
                model=self.device.model,
                name=self.device.label,
                serial_number=self.device.serial_number,
                suggested_area=self.device.announcement,
                sw_version=self.device.firmware_version,
            )
        return None

    @property
    def name(self) -> str | None:
        """Return the name of the entity."""
        name = self.device.label if self.device else None
        if description := self.entity_description.name:
            return f"{name} {description}"
        return name

    @property
    def unique_id(self) -> str | None:
        """Return a unique ID."""
        unique_id = str(self.device.id) if self.device else None
        if key := self.entity_description.key:
            return f"{unique_id}-{key}"
        return unique_id
