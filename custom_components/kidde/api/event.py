"""Kidde API."""

from __future__ import annotations


class Event:
    """Event."""

    def __init__(self, api, location, data) -> None:
        """Initialize."""
        self.api = api
        self.location = location
        self.data = data

    @property
    def id(self) -> int | None:
        """ID."""
        return self.data.get("id")

    @property
    def event_type(self) -> str | None:
        """Event type."""
        return self.data.get("event_type")

    @property
    def created_time(self) -> str | None:
        """Created time."""
        return self.data.get("created_time")

    @property
    def updated_time(self) -> str | None:
        """Updated time."""
        return self.data.get("updated_time")

    @property
    def user_id(self) -> int | None:
        """User ID."""
        return self.data.get("user_id")

    @property
    def user_name(self) -> str | None:
        """User name."""
        return self.data.get("user_name")

    @property
    def can_delete(self) -> bool | None:
        """User name."""
        return self.data.get("can_delete")
