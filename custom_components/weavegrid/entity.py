"""Base entity for the WeaveGrid integration."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import WeaveGridConfigEntry, WeaveGridDataUpdateCoordinator


class WeaveGridEntity(CoordinatorEntity[WeaveGridDataUpdateCoordinator]):
    """Defines a WeaveGrid entity."""

    _attr_has_entity_name = True

    def __init__(
        self,
        *,
        entry: WeaveGridConfigEntry,
        coordinator: WeaveGridDataUpdateCoordinator,
        description: EntityDescription,
        vehicle_id: str,
    ) -> None:
        """Initialize the WeaveGrid entity."""
        super().__init__(coordinator=coordinator)
        self.entity_description = description
        self._vehicle_id = vehicle_id
        self._attr_unique_id = f"{vehicle_id}_{description.key}"

        vehicle = coordinator.data[vehicle_id].vehicle
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, vehicle_id)},
            name=vehicle.display_name,
            manufacturer=vehicle.oem_name.title(),
            model="EVSE" if vehicle.is_evse else "Vehicle",
        )
