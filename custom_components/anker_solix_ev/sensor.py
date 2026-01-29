from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    CHARGING_STATUS_MAP,
    OPERATING_MODE_MAP,
    CHARGING_MODE_MAP,
    CP_ACQ_VOLTAGE_MAP,
)
from .coordinator import AnkerSolixCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    coord: AnkerSolixCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        ChargingStatusSensor(coord, entry),
        U32Sensor(coord, entry, "Total Active Power", "power_w", "W"),
        U32Sensor(coord, entry, "Session Energy", "energy_wh", "Wh"),
        U32Sensor(coord, entry, "Session Duration", "duration_s", "s"),

        ScaledU16Sensor(coord, entry, "L1-N Voltage", "v_l1n", "V", 10),
        ScaledU16Sensor(coord, entry, "L2-N Voltage", "v_l2n", "V", 10),
        ScaledU16Sensor(coord, entry, "L3-N Voltage", "v_l3n", "V", 10),
        ScaledU16Sensor(coord, entry, "L1-L2 Voltage", "v_l12", "V", 10),
        ScaledU16Sensor(coord, entry, "L2-L3 Voltage", "v_l23", "V", 10),
        ScaledU16Sensor(coord, entry, "L3-L1 Voltage", "v_l31", "V", 10),

        ScaledU16Sensor(coord, entry, "L1 Current", "i_l1", "A", 100),
        ScaledU16Sensor(coord, entry, "L2 Current", "i_l2", "A", 100),
        ScaledU16Sensor(coord, entry, "L3 Current", "i_l3", "A", 100),

        U32Sensor(coord, entry, "L1 Active Power", "p_l1", "W"),
        U32Sensor(coord, entry, "L2 Active Power", "p_l2", "W"),
        U32Sensor(coord, entry, "L3 Active Power", "p_l3", "W"),

        U32Sensor(coord, entry, "L1 Reactive Power", "q_l1", "W"),
        U32Sensor(coord, entry, "L2 Reactive Power", "q_l2", "W"),
        U32Sensor(coord, entry, "L3 Reactive Power", "q_l3", "W"),

        U32Sensor(coord, entry, "L1 Apparent Power", "s_l1", "W"),
        U32Sensor(coord, entry, "L2 Apparent Power", "s_l2", "W"),
        U32Sensor(coord, entry, "L3 Apparent Power", "s_l3", "W"),

        EnumSensor(coord, entry, "Operating Mode", "operating_mode", OPERATING_MODE_MAP),
        EnumSensor(coord, entry, "Charging Mode", "charging_mode", CHARGING_MODE_MAP),
        EnumSensor(coord, entry, "CP Acquisition Voltage", "cp_acq_voltage", CP_ACQ_VOLTAGE_MAP),

        U16Sensor(coord, entry, "LED Brightness", "led_brightness", "%"),
        U16Sensor(coord, entry, "Relay 1 Temperature", "relay1_temp", "°C"),
        U16Sensor(coord, entry, "Relay 2 Temperature", "relay2_temp", "°C"),
    ])


class _Base(SensorEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator: AnkerSolixCoordinator, entry: ConfigEntry):
        self.coordinator = coordinator
        self.entry = entry

    async def async_added_to_hass(self):
        self.async_on_remove(self.coordinator.async_add_listener(self.async_write_ha_state))


class ChargingStatusSensor(_Base):
    _attr_name = "Charging Status"

    @property
    def unique_id(self):
        return f"{self.entry.entry_id}_charging_status"

    @property
    def native_value(self):
        raw = self.coordinator.data.get("charging_status")
        if raw is None:
            return None
        raw = int(raw)
        return CHARGING_STATUS_MAP.get(raw, f"unknown_{raw}")


class U16Sensor(_Base):
    def __init__(self, coordinator: AnkerSolixCoordinator, entry: ConfigEntry, name: str, key: str, unit: str | None):
        super().__init__(coordinator, entry)
        self._attr_name = name
        self._key = key
        self._attr_native_unit_of_measurement = unit

    @property
    def unique_id(self):
        return f"{self.entry.entry_id}_{self._key}"

    @property
    def native_value(self):
        val = self.coordinator.data.get(self._key)
        return int(val) if val is not None else None


class U32Sensor(_Base):
    def __init__(self, coordinator: AnkerSolixCoordinator, entry: ConfigEntry, name: str, key: str, unit: str | None):
        super().__init__(coordinator, entry)
        self._attr_name = name
        self._key = key
        self._attr_native_unit_of_measurement = unit

    @property
    def unique_id(self):
        return f"{self.entry.entry_id}_{self._key}"

    @property
    def native_value(self):
        val = self.coordinator.data.get(self._key)
        return int(val) if val is not None else None


class ScaledU16Sensor(_Base):
    def __init__(self, coordinator: AnkerSolixCoordinator, entry: ConfigEntry, name: str, key: str, unit: str, gain: int):
        super().__init__(coordinator, entry)
        self._attr_name = name
        self._key = key
        self._attr_native_unit_of_measurement = unit
        self._gain = gain

    @property
    def unique_id(self):
        return f"{self.entry.entry_id}_{self._key}"

    @property
    def native_value(self):
        raw = self.coordinator.data.get(self._key)
        if raw is None:
            return None
        return float(int(raw)) / float(self._gain)


class EnumSensor(_Base):
    def __init__(self, coordinator: AnkerSolixCoordinator, entry: ConfigEntry, name: str, key: str, mapping: dict[int, str]):
        super().__init__(coordinator, entry)
        self._attr_name = name
        self._key = key
        self._map = mapping

    @property
    def unique_id(self):
        return f"{self.entry.entry_id}_{self._key}"

    @property
    def native_value(self):
        raw = self.coordinator.data.get(self._key)
        if raw is None:
            return None
        raw = int(raw)
        return self._map.get(raw, f"unknown_{raw}")
