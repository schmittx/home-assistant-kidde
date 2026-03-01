"""Kidde API."""

from __future__ import annotations

import datetime
from enum import StrEnum
from http import HTTPMethod

MODEL_MAP = {
    "EssWFAC": "30CUAR-W",
}
MODEL_UNKNOWN = "Unknown"


class BatteryState(StrEnum):
    """Battery state."""

    GOOD = "Good"


class Device:
    """Device."""

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
    def serial_number(self) -> str | None:
        """Serial number."""
        return self.data.get("serial_number")

    @property
    def model(self) -> str | None:
        """Model."""
        model = self.data.get("model", MODEL_UNKNOWN)
        return MODEL_MAP.get(model, model)

    @property
    def location_id(self) -> int | None:
        """Model."""
        return self.data.get("location_id")

    @property
    def label(self) -> str | None:
        """Label."""
        return self.data.get("label")

    @property
    def last_seen(self) -> datetime.datetime | None:
        """Last seen."""
        if last_seen := self.data.get("last_seen"):
            return datetime.datetime.strptime(
                last_seen.strip("Z").split(".")[0], "%Y-%m-%dT%H:%M:%S"
            ).replace(tzinfo=datetime.UTC)
        return last_seen

    @property
    def co_alarm(self) -> bool | None:
        """CO alarm."""
        return self.data.get("co_alarm")

    @property
    def hardwire_co(self) -> bool | None:
        """Hardwire CO."""
        return self.data.get("hardwire_co")

    @property
    def smoke_alarm(self) -> bool | None:
        """Smoke alarm."""
        return self.data.get("smoke_alarm")

    @property
    def hardwire_smoke(self) -> bool | None:
        """Hardwire smoke."""
        return self.data.get("hardwire_smoke")

    @property
    def offline(self) -> bool | None:
        """Offline."""
        return self.data.get("offline")

    @property
    def online(self) -> bool:
        """Online."""
        return not self.data.get("offline")

    @property
    def announcement(self) -> str | None:
        """Announcement."""
        if announcement := self.data.get("announcement"):
            return announcement.title()
        return announcement

    @property
    def alarm_version(self) -> str | None:
        """Alarm version."""
        return self.data.get("ver_mb")

    @property
    def firmware_version(self) -> str | None:
        """Firmware version."""
        return self.data.get("ver_wb")

    @property
    def battery_state(self) -> str | None:
        """Battery state."""
        return self.data.get("battery_state")

    @property
    def low_battery(self) -> bool:
        """Low battery."""
        return self.battery_state != BatteryState.GOOD

    @property
    def signal_strength(self) -> int | None:
        """Signal strength."""
        return self.data.get("ap_rssi")

    async def hush(self) -> None:
        """Hush."""
        await self.api.call(
            method=HTTPMethod.POST,
            path=f"location/{self.location.id}/device/{self.id}/hush",
        )

    async def identify(self) -> None:
        """Identify."""
        await self.api.call(
            method=HTTPMethod.POST,
            path=f"location/{self.location.id}/device/{self.id}/identify",
        )

    async def test(self) -> None:
        """Test."""
        await self.api.call(
            method=HTTPMethod.POST,
            path=f"location/{self.location.id}/device/{self.id}/test",
        )

    @property
    def no_chirp_enabled(self) -> bool | None:
        """No chirp enabled."""
        return self.data.get("no_chirp_enabled")

    @property
    def notify_contact(self) -> bool | None:
        """Notify contact."""
        return self.data.get("notify_contact")

    @property
    def notify_eol(self) -> bool | None:
        """Notify EOL."""
        return self.data.get("notify_eol")

    async def set_property(self, key: str, value: bool) -> None:
        """Set property."""
        if not isinstance(key, str) or not isinstance(value, bool):
            return
        await self.api.call(
            method=HTTPMethod.PATCH,
            path=f"location/{self.location.id}/device/{self.id}",
            payload={key: value},
        )
