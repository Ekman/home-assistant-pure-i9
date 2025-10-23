"""Home Assistant last cleaning start sensor entity"""
from datetime import timedelta
import logging
from homeassistant.components.sensor import (SensorEntity, SensorDeviceClass)
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from . import purei9, const

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Initial setup for the workers. Download and identify all workers."""
    data = hass.data[const.DOMAIN][config_entry.entry_id]

    entities = []

    for coord in data[const.COORDINATORS]:
        entities.append(
            PureI9LastCleaningStart(coord, coord.data)
        )

        entities.append(
            PureI9LastCleaningStop(coord, coord.data)
        )

        entities.append(
            PureI9LastCleaningDuration(coord, coord.data)
        )

        entities.append(
            PureI9Dustbin(coord, coord.data)
        )

        entities.append(
            PureI9Battery(coord, coord.data)
        )

    async_add_entities(entities)

class PureI9Sensor(CoordinatorEntity, SensorEntity):
    """Base class for Pure i9 sensor"""
    def __init__(
            self,
            coordinator,
            params: purei9.Params,
        ):
        super().__init__(coordinator)
        self._params = params

    @property
    def device_info(self):
        """Return information for the device registry"""
        return purei9.create_device_attrs(self._params)

    def _handle_coordinator_update(self):
        """
        Called by Home Assistant asking the vacuum to update to the latest state.
        Can contain IO code.
        """
        self._params = self.coordinator.data
        self.async_write_ha_state()

class PureI9LastCleaningStart(PureI9Sensor):
    """The main Pure i9 last cleaning start sensor entity"""
    @property
    def unique_id(self) -> str:
        """Unique identifier to the entity"""
        return f"{self._params.unique_id}_last_cleaning_start"

    @property
    def name(self):
        """The sensor name"""
        return f"{self._params.name} last cleaning start"

    @property
    def device_class(self):
        """The device class of the entity"""
        return "date"

    @property
    def native_value(self):
        return (
            self._params.last_cleaning_session.endtime
                - timedelta(seconds=self._params.last_cleaning_session.duration)
            if self._params.last_cleaning_session is not None
            else None
        )

class PureI9LastCleaningStop(PureI9Sensor):
    """The main Pure i9 last cleaning stop sensor entity"""
    @property
    def unique_id(self) -> str:
        """Unique identifier to the entity"""
        return f"{self._params.unique_id}_last_cleaning_stop"

    @property
    def name(self):
        """The sensor name"""
        return f"{self._params.name} last cleaning stop"

    @property
    def device_class(self):
        """The device class of the entity"""
        return "date"

    @property
    def native_value(self):
        return (
            self._params.last_cleaning_session.endtime
            if self._params.last_cleaning_session is not None
            else None
        )

class PureI9LastCleaningDuration(PureI9Sensor):
    """The main Pure i9 last cleaning duration sensor entity"""
    @property
    def unique_id(self) -> str:
        """Unique identifier to the entity"""
        return f"{self._params.unique_id}_last_cleaning_duration"

    @property
    def name(self):
        """The sensor name"""
        return f"{self._params.name} last cleaning duration"

    @property
    def device_class(self):
        """The device class of the entity"""
        return "duration"

    @property
    def native_unit_of_measurement(self):
        return "s"

    @property
    def native_value(self):
        return (
            self._params.last_cleaning_session.duration
            if self._params.last_cleaning_session is not None
            else None
        )

class PureI9Dustbin(PureI9Sensor):
    """The main Pure i9 dustin status"""
    @property
    def unique_id(self) -> str:
        """Unique identifier to the entity"""
        return f"{self._params.unique_id}_dustbin"

    @property
    def name(self):
        """The sensor name"""
        return f"{self._params.name} dustbin"

    @property
    def device_class(self):
        """The device class of the entity"""
        return "enum"

    @property
    def options(self):
        """Available options for the enum"""
        return list(status.name for status in purei9.Dustbin)

    @property
    def native_value(self):
        """The current value of the dustbin"""
        return self._params.dustbin.name

class PureI9Battery(PureI9Sensor):
    """The main Pure i9 battery level"""
    @property
    def unique_id(self) -> str:
        """Unique identifier to the entity"""
        return f"{self._params.unique_id}_battery"

    @property
    def name(self):
        """The sensor name"""
        return f"{self._params.name} battery"

    @property
    def device_class(self):
        """The device class of the entity"""
        return SensorDeviceClass.BATTERY

    @property
    def native_value(self):
        """The current value of the battery"""
        return self._params.battery
