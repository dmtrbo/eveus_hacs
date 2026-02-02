import logging
from datetime import datetime, timezone
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components.sensor import SensorStateClass, SensorDeviceClass
from homeassistant.util import dt as dt_util
from .const import DOMAIN, STATUS_MAP

_LOGGER = logging.getLogger(__name__)

SENSOR_DEFINITIONS = [
    ("state", "evse_energy_star_status", None, None, SensorDeviceClass.ENUM, ["startup", "system_test", "waiting", "connected", "charging", "charge_complete", "suspended", "error", "unknown"], True),
    ("currentSet", "evse_energy_star_current_set", "A", SensorStateClass.MEASUREMENT, SensorDeviceClass.CURRENT, None, True),
    ("curMeas1", "evse_energy_star_current_phase_1", "A", SensorStateClass.MEASUREMENT, SensorDeviceClass.CURRENT, None, True),
    ("voltMeas1", "evse_energy_star_voltage_phase_1", "V", SensorStateClass.MEASUREMENT, SensorDeviceClass.VOLTAGE, None, True),
    ("temperature1", "evse_energy_star_temperature_box", "°C", SensorStateClass.MEASUREMENT, SensorDeviceClass.TEMPERATURE, None, True),
    ("temperature2", "evse_energy_star_temperature_socket", "°C", SensorStateClass.MEASUREMENT, SensorDeviceClass.TEMPERATURE, None, True),
    ("leakValue", "evse_energy_star_leakage", "mA", SensorStateClass.MEASUREMENT, SensorDeviceClass.CURRENT, None, False),
    ("sessionEnergy", "evse_energy_star_session_energy", "kWh", SensorStateClass.TOTAL_INCREASING, SensorDeviceClass.ENERGY, None, True),
    ("sessionTime", "evse_energy_star_session_time", None, None, None, None, False),
    ("totalEnergy", "evse_energy_star_total_energy", "kWh", SensorStateClass.TOTAL_INCREASING, SensorDeviceClass.ENERGY, None, True),
    ("systemTime", "evse_energy_star_system_time", None, None, None, None, False),
]

THREE_PHASE_SENSORS = [
    ("curMeas2", "evse_energy_star_current_phase_2", "A", SensorStateClass.MEASUREMENT, SensorDeviceClass.CURRENT, None, True),
    ("curMeas3", "evse_energy_star_current_phase_3", "A", SensorStateClass.MEASUREMENT, SensorDeviceClass.CURRENT, None, True),
    ("voltMeas2", "evse_energy_star_voltage_phase_2", "V", SensorStateClass.MEASUREMENT, SensorDeviceClass.VOLTAGE, None, True),
    ("voltMeas3", "evse_energy_star_voltage_phase_3", "V", SensorStateClass.MEASUREMENT, SensorDeviceClass.VOLTAGE, None, True),
]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    device_type = entry.options.get("device_type", entry.data.get("device_type", "1_phase"))

    entities = [
        EVSESensor(coordinator, entry, key, trans_key, unit, state_class, device_class, options, enabled_default)
        for key, trans_key, unit, state_class, device_class, options, enabled_default in SENSOR_DEFINITIONS
    ]

    if device_type == "3_phase":
        entities += [
            EVSESensor(coordinator, entry, key, trans_key, unit, state_class, device_class, options, enabled_default)
            for key, trans_key, unit, state_class, device_class, options, enabled_default in THREE_PHASE_SENSORS
        ]

    entities.append(EVSEGroundStatus(coordinator, entry))
    async_add_entities(entities)

class EVSESensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, config_entry: ConfigEntry, key, translation_key, unit, state_class, device_class, options=None, enabled_default=True):
        super().__init__(coordinator)
        self.coordinator = coordinator
        self.config_entry = config_entry
        self._key = key
        self._attr_translation_key = translation_key
        self._attr_native_unit_of_measurement = unit
        self._attr_state_class = state_class
        self._attr_device_class = device_class
        self._attr_entity_registry_enabled_default = enabled_default
        if options:
            self._attr_options = options

        self._attr_has_entity_name = True
        self._attr_suggested_object_id = f"{self.coordinator.device_name_slug}_{self._attr_translation_key}"
        self._attr_unique_id = f"{translation_key}_{config_entry.entry_id}"

    @property
    def available(self) -> bool:
        return self.coordinator.last_update_success

    @property
    def native_value(self):
        value = self.coordinator.data.get(self._key)
        if value is None:
            return None
        try:
            if self._key == "curMeas1":
                return round(float(value), 2)
            if self._key in ["sessionEnergy", "totalEnergy"]:
                return round(float(value), 3)
            if self._key == "sessionTime":
                # Format as HH:MM:SS
                total_sec = int(float(value))
                h = total_sec // 3600
                m = (total_sec % 3600) // 60
                s = total_sec % 60
                return f"{h:02}:{m:02}:{s:02}"
            if self._key == "systemTime":
                # Convert Unix timestamp to time string
                timestamp = int(float(value))
                dt = datetime.fromtimestamp(timestamp)
                return dt.strftime("%H:%M:%S")
            if self._key == "state":
                # Return translation key from translations files
                return STATUS_MAP.get(value, "unknown")
            return value
        except Exception as err:
            _LOGGER.warning("sensor.py → error processing %s: %s", self._key, repr(err))
            return str(value)

    def _handle_coordinator_update(self):
        new_value = self.coordinator.data.get(self._key)
        if self._key == "systemTime":
            try:
                # Compare Unix timestamps directly
                old_timestamp = int(float(self.coordinator.data.get(self._key, 0)))
                new_timestamp = int(float(new_value))
                # Only update if difference is more than 2 seconds
                if abs(new_timestamp - old_timestamp) <= 2:
                    return
            except Exception as err:
                _LOGGER.debug("sensor.py → systemTime comparison: %s", repr(err))

        self._attr_native_value = new_value
        self.async_write_ha_state()

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.config_entry.entry_id)},
            "name": self.config_entry.data.get("device_name", "Eveus Pro"),
            "manufacturer": "Energy Star",
            "model": "EVSE",
            "sw_version": self.coordinator.data.get("fwVersion")
        }

class EVSEGroundStatus(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, config_entry: ConfigEntry):
        super().__init__(coordinator)
        self.coordinator = coordinator
        self.config_entry = config_entry
        self._attr_translation_key = "evse_energy_star_ground_status"
        self._attr_device_class = SensorDeviceClass.ENUM
        self._attr_options = ["✅", "❌"]
        self._attr_entity_registry_enabled_default = False

        self._attr_has_entity_name = True
        self._attr_suggested_object_id = f"{self.coordinator.device_name_slug}_{self._attr_translation_key}"
        self._attr_unique_id = f"ground_status_{config_entry.entry_id}"

    @property
    def available(self):
        return self.coordinator.last_update_success

    @property
    def native_value(self):
        return "✅" if bool(self.coordinator.data.get("ground", 0)) else "❌"

    @property
    def icon(self):
        return "mdi:checkbox-marked-circle" if self.native_value == "✅" else "mdi:close-circle-outline"

    def _handle_coordinator_update(self):
        self.async_write_ha_state()

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.config_entry.entry_id)},
            "name": self.config_entry.data.get("device_name", "Eveus Pro"),
            "manufacturer": "Energy Star",
            "model": "EVSE",
            "sw_version": self.coordinator.data.get("fwVersion")
        }
