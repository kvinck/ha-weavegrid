"""Support for WeaveGrid sensors."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import PERCENTAGE, UnitOfEnergy, UnitOfLength
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import WeaveGridConfigEntry, WeaveGridDataUpdateCoordinator
from .entity import WeaveGridEntity
from .models import WeaveGridData

PARALLEL_UPDATES = 0

MC_STATUS_OPTIONS = ["complete", "active", "inactive", "pending", "unknown"]


@dataclass(frozen=True, kw_only=True)
class WeaveGridSensorDescription(SensorEntityDescription):
    """Describe a WeaveGrid sensor."""

    value_fn: Callable[[WeaveGridData], float | str | None]


DESCRIPTIONS: tuple[WeaveGridSensorDescription, ...] = (
    WeaveGridSensorDescription(
        key="weekly_energy",
        translation_key="weekly_energy",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL,
        suggested_display_precision=1,
        value_fn=lambda data: data.aggregates.total_energy_kwh,
    ),
    WeaveGridSensorDescription(
        key="weekly_cost",
        translation_key="weekly_cost",
        device_class=SensorDeviceClass.MONETARY,
        native_unit_of_measurement="USD",
        state_class=SensorStateClass.TOTAL,
        suggested_display_precision=2,
        value_fn=lambda data: data.aggregates.total_charge_cost,
    ),
    WeaveGridSensorDescription(
        key="smart_score",
        translation_key="smart_score",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        value_fn=lambda data: data.aggregates.smart_score * 100,
    ),
    WeaveGridSensorDescription(
        key="last_charge_energy",
        translation_key="last_charge_energy",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        suggested_display_precision=1,
        value_fn=lambda data: (
            data.aggregates.daily[0].energy_kwh
            if data.aggregates.daily
            else None
        ),
    ),
    WeaveGridSensorDescription(
        key="last_charge_cost",
        translation_key="last_charge_cost",
        device_class=SensorDeviceClass.MONETARY,
        native_unit_of_measurement="USD",
        suggested_display_precision=2,
        value_fn=lambda data: (
            data.aggregates.daily[0].charge_cost
            if data.aggregates.daily
            else None
        ),
    ),
    WeaveGridSensorDescription(
        key="managed_charge_status",
        translation_key="managed_charge_status",
        device_class=SensorDeviceClass.ENUM,
        options=MC_STATUS_OPTIONS,
        value_fn=lambda data: (
            data.status.mc_status.lower() if data.status else None
        ),
    ),
    WeaveGridSensorDescription(
        key="miles_added",
        translation_key="miles_added",
        device_class=SensorDeviceClass.DISTANCE,
        native_unit_of_measurement=UnitOfLength.MILES,
        suggested_display_precision=0,
        value_fn=lambda data: (
            data.status.miles_added_by_ready_by_time if data.status else None
        ),
    ),
    WeaveGridSensorDescription(
        key="battery_level",
        translation_key="battery_level",
        device_class=SensorDeviceClass.BATTERY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: None,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: WeaveGridConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up WeaveGrid sensors based on a config entry."""
    coordinator = entry.runtime_data
    async_add_entities(
        WeaveGridSensorEntity(
            entry=entry,
            coordinator=coordinator,
            description=description,
            vehicle_id=vehicle_id,
        )
        for vehicle_id in coordinator.data
        for description in DESCRIPTIONS
    )


class WeaveGridSensorEntity(
    WeaveGridEntity, SensorEntity
):
    """Defines a WeaveGrid sensor."""

    entity_description: WeaveGridSensorDescription

    @property
    def native_value(self) -> float | str | None:
        """Return the state of the sensor."""
        return self.entity_description.value_fn(
            self.coordinator.data[self._vehicle_id]
        )
