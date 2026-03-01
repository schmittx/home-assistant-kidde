"""Adds config flow for Kidde integration."""

import logging
from types import MappingProxyType
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import (
    CONF_EMAIL,
    CONF_PASSWORD,
    CONF_SCAN_INTERVAL,
    UnitOfTime,
)
from homeassistant.core import callback
from homeassistant.helpers.selector import (
    BooleanSelector,
    NumberSelector,
    NumberSelectorConfig,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from .api import KiddeAPI, KiddeAPIAuthError
from .api.location import Location as KiddeLocation
from .const import (
    CONF_COOKIES,
    CONF_DEVICES,
    CONF_LOCATIONS,
    CONF_SAVE_RESPONSES,
    CONF_TIMEOUT,
    DATA_COORDINATOR,
    DEFAULT_SAVE_RESPONSES,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_TIMEOUT,
    DOMAIN,
    MAX_SCAN_INTERVAL,
    MAX_TIMEOUT,
    MIN_SCAN_INTERVAL,
    MIN_TIMEOUT,
    STEP_SCAN_INTERVAL,
    STEP_TIMEOUT,
)

_LOGGER = logging.getLogger(__name__)


class KiddeConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Kidde integration."""

    VERSION = 1
    MINOR_VERSION = 0
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def __init__(self) -> None:
        """Initialize."""
        self.api: KiddeAPI = KiddeAPI()
        self.index = 0
        self.response: list[KiddeLocation] = []
        self.user_input: dict[str, Any] = {}

    @property
    def config_title(self) -> str:
        """Config title."""
        return self.user_input[CONF_EMAIL]

    async def async_step_user(self, user_input=None):
        """Async step user."""
        errors = {}

        if user_input is not None:
            self.user_input[CONF_EMAIL] = user_input[CONF_EMAIL]
            self.user_input[CONF_PASSWORD] = user_input[CONF_PASSWORD]
            self.api = KiddeAPI()

            try:
                await self.api.login(
                    email=self.user_input[CONF_EMAIL],
                    password=self.user_input[CONF_PASSWORD],
                )
            except KiddeAPIAuthError:
                errors["base"] = "invalid_auth"
            except Exception as exception:
                _LOGGER.exception("%s", type(exception).__name__)
                errors["base"] = "unknown"
            else:
                _LOGGER.debug("Login successful")
                return await self.async_finish_login(errors)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_EMAIL): TextSelector(
                        TextSelectorConfig(
                            type=TextSelectorType.EMAIL,
                        )
                    ),
                    vol.Required(CONF_PASSWORD): TextSelector(
                        TextSelectorConfig(
                            type=TextSelectorType.PASSWORD,
                        )
                    ),
                }
            ),
            errors=errors,
        )

    async def async_finish_login(self, errors):
        """Async finish login."""
        await self.async_set_unique_id(str(self.api.user_id))
        self._abort_if_unique_id_configured()

        self.user_input[CONF_COOKIES] = self.api.cookies
        try:
            self.response = await self.api.update()
        except KiddeAPIAuthError:
            errors["base"] = "update_failed"

        return await self.async_step_locations()

    async def async_step_locations(self, user_input=None):
        """Async step locations."""
        errors = {}

        if user_input is not None:
            self.user_input[CONF_LOCATIONS] = []

            for location in self.response:
                if location.label_long in user_input[CONF_LOCATIONS]:
                    self.user_input[CONF_LOCATIONS].append(location.id)

            return await self.async_step_devices()

        location_names = [
            location.label_long for location in self.response if location.label_long
        ]

        if not location_names:
            return await self.async_step_devices()

        return self.async_show_form(
            step_id="locations",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_LOCATIONS, default=location_names
                    ): SelectSelector(
                        SelectSelectorConfig(
                            options=location_names,
                            multiple=True,
                            mode=SelectSelectorMode.DROPDOWN,
                            sort=True,
                        )
                    ),
                }
            ),
            errors=errors,
        )

    async def async_step_devices(self, user_input=None):
        """Async step devices."""
        errors = {}

        if user_input is not None:
            if not self.user_input.get(CONF_DEVICES):
                self.user_input[CONF_DEVICES] = []

            for location in self.response:
                if location.id == self.user_input[CONF_LOCATIONS][self.index]:
                    for device in location.devices:
                        if device.label in user_input[CONF_DEVICES]:
                            self.user_input[CONF_DEVICES].append(device.id)
                    self.index += 1

        if self.index == len(self.user_input[CONF_LOCATIONS]):
            self.index = 0
            if self.show_advanced_options:
                return await self.async_step_advanced()
            return self.async_create_entry(
                title=self.config_title, data=self.user_input
            )

        for location in self.response:
            if location.id == self.user_input[CONF_LOCATIONS][self.index]:
                device_names = [
                    device.label for device in location.devices if device.label
                ]

                if not device_names:
                    self.index += 1
                    return await self.async_step_devices()

                return self.async_show_form(
                    step_id="devices",
                    data_schema=vol.Schema(
                        {
                            vol.Optional(
                                CONF_DEVICES, default=device_names
                            ): SelectSelector(
                                SelectSelectorConfig(
                                    options=device_names,
                                    multiple=True,
                                    mode=SelectSelectorMode.DROPDOWN,
                                    sort=True,
                                )
                            ),
                        }
                    ),
                    description_placeholders={
                        "location_name": location.label_long or ""
                    },
                    errors=errors,
                )
        return None

    async def async_step_advanced(self, user_input=None):
        """Handle a flow initialized by the user."""
        if user_input is not None:
            self.user_input[CONF_SAVE_RESPONSES] = user_input[CONF_SAVE_RESPONSES]
            self.user_input[CONF_SCAN_INTERVAL] = user_input[CONF_SCAN_INTERVAL]
            self.user_input[CONF_TIMEOUT] = user_input[CONF_TIMEOUT]
            return self.async_create_entry(
                title=self.config_title, data=self.user_input
            )

        return self.async_show_form(
            step_id="advanced",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_SAVE_RESPONSES, default=DEFAULT_SAVE_RESPONSES
                    ): BooleanSelector(),
                    vol.Optional(
                        CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL
                    ): NumberSelector(
                        NumberSelectorConfig(
                            min=MIN_SCAN_INTERVAL,
                            max=MAX_SCAN_INTERVAL,
                            step=STEP_SCAN_INTERVAL,
                            unit_of_measurement=UnitOfTime.SECONDS,
                        )
                    ),
                    vol.Optional(CONF_TIMEOUT, default=DEFAULT_TIMEOUT): NumberSelector(
                        NumberSelectorConfig(
                            min=MIN_TIMEOUT,
                            max=MAX_TIMEOUT,
                            step=STEP_TIMEOUT,
                            unit_of_measurement=UnitOfTime.SECONDS,
                        )
                    ),
                }
            ),
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Kidde options callback."""
        return KiddeOptionsFlowHandler()


class KiddeOptionsFlowHandler(config_entries.OptionsFlow):
    """Config flow options for Kidde."""

    def __init__(self) -> None:
        """Initialize Kidde options flow."""
        self.coordinator = None
        self.coordinator_data: list[KiddeLocation] = []
        self.index = 0
        self.user_input = {}

    @property
    def data(self) -> MappingProxyType[str, Any]:
        """Return the data from a config entry."""
        return self.config_entry.data

    @property
    def options(self) -> MappingProxyType[str, Any]:
        """Return the options from a config entry."""
        return self.config_entry.options

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        self.coordinator = self.hass.data[DOMAIN][self.config_entry.entry_id][
            DATA_COORDINATOR
        ]
        self.coordinator_data = self.coordinator.data
        return await self.async_step_locations()

    async def async_step_locations(self, user_input=None):
        """Handle a flow initialized by the user."""
        if user_input is not None:
            self.user_input[CONF_LOCATIONS] = [
                location.id
                for location in self.coordinator_data
                if location.label_long in user_input[CONF_LOCATIONS]
            ]
            return await self.async_step_devices()

        conf_locations = [
            location.label_long
            for location in self.coordinator_data
            if location.id
            in self.options.get(CONF_LOCATIONS, self.data[CONF_LOCATIONS])
        ]
        location_names = [
            location.label_long
            for location in self.coordinator_data
            if location.label_long
        ]

        return self.async_show_form(
            step_id="locations",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_LOCATIONS, default=conf_locations
                    ): SelectSelector(
                        SelectSelectorConfig(
                            options=location_names,
                            multiple=True,
                            mode=SelectSelectorMode.DROPDOWN,
                            sort=True,
                        )
                    ),
                }
            ),
        )

    async def async_step_devices(self, user_input=None):
        """Handle a flow initialized by the user."""
        if user_input is not None:
            for location in self.coordinator_data:
                if location.id == self.user_input[CONF_LOCATIONS][self.index]:
                    self.user_input[CONF_DEVICES].extend(
                        [
                            device.id
                            for device in location.devices
                            if device.label in user_input[CONF_DEVICES]
                        ]
                    )
                    self.index += 1

        if self.index == len(self.user_input[CONF_LOCATIONS]):
            if self.show_advanced_options:
                return await self.async_step_advanced()
            return self.async_create_entry(title="", data=self.user_input)
        if self.index == 0:
            self.user_input[CONF_DEVICES] = []

        for location in self.coordinator_data:
            if location.id == self.user_input[CONF_LOCATIONS][self.index]:
                conf_devices = [
                    device.label
                    for device in location.devices
                    if device.id
                    in self.options.get(CONF_DEVICES, self.data[CONF_DEVICES])
                ]
                device_names = [
                    device.label for device in location.devices if device.label
                ]

                return self.async_show_form(
                    step_id="devices",
                    data_schema=vol.Schema(
                        {
                            vol.Optional(
                                CONF_DEVICES, default=conf_devices
                            ): SelectSelector(
                                SelectSelectorConfig(
                                    options=device_names,
                                    multiple=True,
                                    mode=SelectSelectorMode.DROPDOWN,
                                    sort=True,
                                )
                            ),
                        }
                    ),
                    description_placeholders={
                        "location_name": location.label_long or ""
                    },
                )
        return None

    async def async_step_advanced(self, user_input=None):
        """Handle a flow initialized by the user."""
        if user_input is not None:
            self.user_input[CONF_SAVE_RESPONSES] = user_input[CONF_SAVE_RESPONSES]
            self.user_input[CONF_SCAN_INTERVAL] = user_input[CONF_SCAN_INTERVAL]
            self.user_input[CONF_TIMEOUT] = user_input[CONF_TIMEOUT]
            return self.async_create_entry(title="", data=self.user_input)

        conf_save_responses = self.options.get(
            CONF_SAVE_RESPONSES,
            self.data.get(CONF_SAVE_RESPONSES, DEFAULT_SAVE_RESPONSES),
        )
        conf_scan_interval = self.options.get(
            CONF_SCAN_INTERVAL, self.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
        )
        conf_timeout = self.options.get(
            CONF_TIMEOUT, self.data.get(CONF_TIMEOUT, DEFAULT_TIMEOUT)
        )

        return self.async_show_form(
            step_id="advanced",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_SAVE_RESPONSES, default=conf_save_responses
                    ): BooleanSelector(),
                    vol.Optional(
                        CONF_SCAN_INTERVAL, default=conf_scan_interval
                    ): NumberSelector(
                        NumberSelectorConfig(
                            min=MIN_SCAN_INTERVAL,
                            max=MAX_SCAN_INTERVAL,
                            step=STEP_SCAN_INTERVAL,
                            unit_of_measurement=UnitOfTime.SECONDS,
                        )
                    ),
                    vol.Optional(CONF_TIMEOUT, default=conf_timeout): NumberSelector(
                        NumberSelectorConfig(
                            min=MIN_TIMEOUT,
                            max=MAX_TIMEOUT,
                            step=STEP_TIMEOUT,
                            unit_of_measurement=UnitOfTime.SECONDS,
                        )
                    ),
                }
            ),
        )
