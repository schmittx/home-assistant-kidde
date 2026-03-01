"""Kidde API."""

from __future__ import annotations

from .device import Device
from .event import Event


class Location:
    """Location."""

    def __init__(self, api, data) -> None:
        """Initialize."""
        self.api = api
        self.data = data

    @property
    def id(self) -> int | None:
        """ID."""
        return self.data.get("id")

    @property
    def label(self) -> str | None:
        """Label."""
        return self.data.get("label")

    @property
    def label_long(self) -> str | None:
        """Name location."""
        if self.city and self.state:
            return f"{self.label} ({self.city}, {self.state})"
        if self.zip:
            return f"{self.label} ({self.zip})"
        return self.label

    @property
    def user_id(self) -> int | None:
        """User ID."""
        return self.data.get("user_id")

    @property
    def street(self) -> str | None:
        """Street."""
        return self.data.get("street")

    @property
    def city(self) -> str | None:
        """City."""
        return self.data.get("city")

    @property
    def state(self) -> str | None:
        """State."""
        return self.data.get("state")

    @property
    def location_country(self) -> str | None:
        """Country."""
        return self.data.get("country")

    @property
    def zip(self) -> str | None:
        """Zip."""
        return self.data.get("zip")

    @property
    def longitude(self) -> float | None:
        """Longitude."""
        return self.data.get("longitude")

    @property
    def latitude(self) -> float | None:
        """Latitude."""
        return self.data.get("latitude")

    @property
    def smoke_mitigation(self) -> bool | None:
        """Smoke mitigation."""
        return self.data.get("smoke_mitigation")

    @property
    def tvoc_mitigation(self) -> bool | None:
        """TVOC mitigation."""
        return self.data.get("tvoc_mitigation")

    @property
    def devices(self) -> list[Device]:
        """Devices."""
        return [
            Device(self.api, self, device) for device in self.data.get("devices", [])
        ]

    @property
    def events(self) -> list[Event]:
        """Events."""
        return [Event(self.api, self, event) for event in self.data.get("events", [])]
