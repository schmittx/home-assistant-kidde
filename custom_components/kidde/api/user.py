"""Kidde API."""

from __future__ import annotations


class User:
    """User."""

    def __init__(self, api, data) -> None:
        """Initialize."""
        self.api = api
        self.data = data

    @property
    def id(self) -> int | None:
        """ID."""
        return self.data.get("id")

    @property
    def name(self) -> str | None:
        """Name."""
        return self.data.get("name")

    @property
    def country_code(self) -> str | None:
        """Country code."""
        return self.data.get("country_code")

    @property
    def phone(self) -> str | None:
        """Phone."""
        return self.data.get("phone")

    @property
    def email(self) -> str | None:
        """Email."""
        return self.data.get("email")

    @property
    def timezone(self) -> str | None:
        """Timezone."""
        return self.data.get("timezone")
