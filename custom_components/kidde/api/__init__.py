"""Kidde API."""

from __future__ import annotations

from http import HTTPMethod
import json
import logging
from pathlib import Path
from typing import Any, Literal

import aiofiles
import aiohttp

from .location import Location

_LOGGER = logging.getLogger(__name__)

API_PREFIX = "https://api.homesafe.kidde.com/api/v4"


class KiddeAPIAuthError(Exception):
    """Exception to indicate an authentication error."""


class KiddeAPI:
    """KiddeAPI."""

    def __init__(
        self,
        cookies: dict[str, str] | None = None,
        save_location: str | None = None,
    ) -> None:
        """Initialize."""
        self.cookies = cookies
        self.save_location = save_location
        self.user_id = None

    async def login(self, email: str, password: str) -> dict[str, Any]:
        """Login."""
        path = "auth/login"
        payload = {"email": email, "password": password}
        async with aiohttp.request(
            method=HTTPMethod.POST, url=f"{API_PREFIX}/{path}", json=payload
        ) as response:
            if response.status == 403:
                raise KiddeAPIAuthError
            response.raise_for_status()
            result = await self.save_result(result=await response.json(), name=path)
            self.cookies = {c.key: c.value for c in response.cookies.values()}
            self.user_id = result["id"]
            return result

    async def call(
        self,
        method: Literal[HTTPMethod.GET, HTTPMethod.PATCH, HTTPMethod.POST],
        path: str,
        payload: dict[str, Any] | None = None,
    ) -> Any:
        """Make a request."""
        url = f"{API_PREFIX}/{path}"
        if payload is None:
            payload = {}
        async with aiohttp.request(
            method=method, url=url, cookies=self.cookies, json=payload
        ) as response:
            if response.status == 403:
                raise KiddeAPIAuthError
            response.raise_for_status()
            if response.status == 204:
                return None
            return await self.save_result(result=await response.json(), name=path)

    async def save_result(
        self, result: dict[str, Any], name: str = "result"
    ) -> dict[str, Any]:
        """Save the result to a file."""
        if self.save_location and result:
            if not Path(self.save_location).is_dir():
                _LOGGER.debug("Creating directory: %s", self.save_location)
                Path(self.save_location).mkdir()
            name = name.replace("/", "_").replace(".", "_")
            file_path_name = f"{self.save_location}/{name}.json"
            _LOGGER.debug("Saving result: %s", file_path_name)
            async with aiofiles.open(file_path_name, mode="w") as file:
                await file.write(
                    json.dumps(
                        result,
                        default=lambda o: "not-serializable",
                        indent=4,
                        sort_keys=True,
                    )
                )
        return result

    async def update(
        self,
        target_locations: list[int] | None = None,
    ) -> list[Location]:
        """Update."""
        data = []
        locations = await self.call(method=HTTPMethod.GET, path="location")
        if locations and isinstance(locations, list):
            for location in locations:
                if location and isinstance(location, dict):
                    location_id = location["id"]
                    if any(
                        [
                            target_locations is None,
                            target_locations and location_id in target_locations,
                        ]
                    ):
                        location["devices"] = await self.call(
                            method=HTTPMethod.GET, path=f"location/{location_id}/device"
                        )
                        events = await self.call(
                            method=HTTPMethod.GET, path=f"location/{location_id}/event"
                        )
                        if events and isinstance(events, dict):
                            location["events"] = events.get("events")
                        data.append(Location(self, location))
        return data
