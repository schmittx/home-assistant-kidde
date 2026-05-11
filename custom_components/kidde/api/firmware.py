"""Kidde API."""

from __future__ import annotations


class Firmware:
    """Firmware."""

    def __init__(self, api, data) -> None:
        """Initialize."""
        self.api = api
        self.data = data

    @property
    def model(self) -> str | None:
        """Model."""
        return self.data.get("model")

    @property
    def rev(self) -> str | None:
        """Revision."""
        return self.data.get("rev")

    @property
    def url(self) -> str | None:
        """URL."""
        return self.data.get("url")

    @property
    def ota_upgrade_from(self) -> str | None:
        """OTA upgrade from."""
        return self.data.get("ota_upgrade_from")

    @property
    def mb_rev(self) -> str | None:
        """Motherboard revision."""
        return self.data.get("mb_rev")

    @property
    def mb_url(self) -> str | None:
        """Motherboard URL."""
        return self.data.get("mb_url")
