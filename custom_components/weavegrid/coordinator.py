"""Data update coordinator for the WeaveGrid integration."""

from __future__ import annotations

from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .api import WeaveGridAuthError, WeaveGridClient, WeaveGridConnectionError
from .const import DOMAIN, LOGGER
from .models import WeaveGridData

type WeaveGridConfigEntry = ConfigEntry[WeaveGridDataUpdateCoordinator]


class WeaveGridDataUpdateCoordinator(
    DataUpdateCoordinator[dict[str, WeaveGridData]]
):
    """Coordinator fetching data for all vehicles."""

    config_entry: WeaveGridConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        entry: WeaveGridConfigEntry,
        client: WeaveGridClient,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            LOGGER,
            config_entry=entry,
            name=DOMAIN,
            update_interval=timedelta(minutes=5),
        )
        self.client = client

    async def _async_update_data(self) -> dict[str, WeaveGridData]:
        """Fetch data from the WeaveGrid API."""
        now = dt_util.now()
        end_dttm = now.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        start_dttm = (now - timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%S.000Z")

        try:
            vehicles = await self.client.get_dashboard_data()
            result: dict[str, WeaveGridData] = {}
            for vehicle in vehicles:
                device_status = await self.client.get_device_status(
                    vehicle.vehicle_id
                )
                aggregates = await self.client.get_charge_aggregates(
                    vehicle.vehicle_id, start_dttm, end_dttm
                )
                settings = await self.client.get_managed_charge_settings(
                    vehicle.vehicle_id
                )
                charge_history = await self.client.get_charge_history(
                    vehicle.vehicle_id
                )
                result[vehicle.vehicle_id] = WeaveGridData(
                    vehicle=vehicle,
                    device_status=device_status,
                    aggregates=aggregates,
                    settings=settings,
                    charge_history=charge_history,
                )
            return result
        except WeaveGridAuthError as err:
            raise ConfigEntryAuthFailed from err
        except WeaveGridConnectionError as err:
            raise UpdateFailed(
                f"Error communicating with WeaveGrid: {err}"
            ) from err
