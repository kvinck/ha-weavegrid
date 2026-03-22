"""WeaveGrid GraphQL API client."""

from __future__ import annotations

import aiohttp

from .const import (
    API_URL,
    LOGGER,
    QUERY_CHARGE_AGGREGATES,
    QUERY_DASHBOARD_DATA,
    QUERY_DEVICE_STATUS,
    QUERY_LOGIN,
)
from .models import ChargeAggregates, LoginResult, McPlanStatus, Vehicle


class WeaveGridAuthError(Exception):
    """Raised when authentication fails."""


class WeaveGridConnectionError(Exception):
    """Raised when a connection error occurs."""


class WeaveGridClient:
    """Client for the WeaveGrid GraphQL API."""

    def __init__(self, session: aiohttp.ClientSession) -> None:
        """Initialize the client."""
        self._session = session
        self._utility_acronym: str | None = None

    async def login(self, email: str, password: str) -> LoginResult:
        """Authenticate with the WeaveGrid API."""
        data = await self._execute(
            query=QUERY_LOGIN,
            variables={
                "email": email,
                "password": password,
                "useMagicLink": False,
            },
            operation_name="LoginDriver",
        )
        result = LoginResult.from_dict(data["data"])
        if not result.is_logged_in:
            raise WeaveGridAuthError(
                f"Login failed with status: {result.status}"
            )
        self._utility_acronym = result.utility_acronym
        return result

    async def get_dashboard_data(self) -> list[Vehicle]:
        """Fetch dashboard data with vehicle list."""
        data = await self._execute(
            query=QUERY_DASHBOARD_DATA,
            variables={},
            operation_name="DashboardData",
        )
        return [
            Vehicle.from_dict(v)
            for v in data["data"]["viewer"]["vehicles"]["data"]
        ]

    async def get_device_status(self, vehicle_id: str) -> McPlanStatus | None:
        """Fetch device status for a vehicle."""
        data = await self._execute(
            query=QUERY_DEVICE_STATUS,
            variables={"vehicleId": vehicle_id},
            operation_name="DeviceStatusCard",
        )
        vehicles = data["data"]["viewer"]["vehicles"]["data"]
        if vehicles and vehicles[0].get("mcPlanStatus"):
            return McPlanStatus.from_dict(vehicles[0]["mcPlanStatus"])
        return None

    async def get_charge_aggregates(
        self,
        vehicle_id: str,
        start_dttm: str,
        end_dttm: str,
    ) -> ChargeAggregates:
        """Fetch charge event aggregates for a vehicle."""
        data = await self._execute(
            query=QUERY_CHARGE_AGGREGATES,
            variables={
                "vehicleId": vehicle_id,
                "startDttm": start_dttm,
                "endDttm": end_dttm,
                "limit": 1000,
            },
            operation_name="ChargeEventAggregates",
        )
        charge_events = (
            data["data"]["viewer"]["vehicles"]["data"][0]["chargeEvents"]
        )
        return ChargeAggregates.from_dict(charge_events)

    async def _execute(
        self,
        query: str,
        variables: dict,
        operation_name: str | None = None,
    ) -> dict:
        """Execute a GraphQL operation."""
        payload: dict = {
            "query": query,
            "variables": variables,
        }
        if operation_name:
            payload["operationName"] = operation_name

        headers: dict[str, str] = {"Content-Type": "application/json"}
        if self._utility_acronym:
            headers["x-wg-utility-acronym"] = self._utility_acronym

        try:
            async with self._session.post(
                API_URL, json=[payload], headers=headers
            ) as resp:
                response_text = await resp.text()
                LOGGER.debug(
                    "WeaveGrid API response (status=%s): %s",
                    resp.status,
                    response_text[:500],
                )
                if resp.status == 401:
                    raise WeaveGridAuthError("Authentication failed (HTTP 401)")
                if resp.status != 200:
                    raise WeaveGridConnectionError(
                        f"Unexpected status code: {resp.status}"
                    )
                result = await resp.json(content_type=None)
        except WeaveGridAuthError:
            raise
        except WeaveGridConnectionError:
            raise
        except aiohttp.ClientError as err:
            LOGGER.debug("WeaveGrid aiohttp error: %s", err)
            raise WeaveGridConnectionError(
                f"Error communicating with WeaveGrid: {err}"
            ) from err
        except Exception as err:
            LOGGER.debug(
                "WeaveGrid unexpected error: %s: %s", type(err).__name__, err
            )
            raise WeaveGridConnectionError(
                f"Unexpected error communicating with WeaveGrid: {err}"
            ) from err

        # API returns arrays - unwrap first element
        if isinstance(result, list):
            result = result[0]

        if errors := result.get("errors"):
            first_error = errors[0].get("message", "Unknown error")
            LOGGER.debug("WeaveGrid GraphQL error: %s", errors)
            if "auth" in first_error.lower() or "credentials" in first_error.lower():
                raise WeaveGridAuthError(first_error)
            raise WeaveGridConnectionError(first_error)

        return result
