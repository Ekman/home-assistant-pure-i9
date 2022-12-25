"""Coordinate data updates from Pure i9."""
import logging
from datetime import timedelta
import async_timeout
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)
from purei9_unofficial.cloudv2 import CloudRobot
from . import purei9

_LOGGER = logging.getLogger(__name__)

class PureI9Coordinator(DataUpdateCoordinator):
    """Coordinate data updates from Pure i9."""

    def __init__(self, hass, name, robot: CloudRobot):
        super().__init__(
            hass,
            _LOGGER,
            name=name,
            update_interval=timedelta(minutes=1),
        )
        self._robot = robot

    @property
    def robot(self) -> str:
        """Immutable robot"""
        return self._robot

    async def _async_update_data(self):
        """Fetch data from Pure i9."""
        try:
            async with async_timeout.timeout(10):
                return await self.hass.async_add_executor_job(
                    self.update_and_create_params
                )
        except Exception as ex:
            _LOGGER.error("Could not update data for \"%s\" due to: %s", self.name, ex)
            raise UpdateFailed from ex

    def update_and_create_params(self):
        """Update and create the latest version of params."""
        purei9_fan_speed_list = list(map(lambda x: x.name, self._robot.getsupportedpowermodes()))
        fan_speed_list = purei9.fan_speed_list_to_hass(purei9_fan_speed_list)

        params = purei9.Params(self._robot.getid(), self._robot.getname(), fan_speed_list)

        pure_i9_battery = self._robot.getbattery()
        purei9_dustbin = self._robot.getdustbinstatus()

        params.state = purei9.state_to_hass(
            self._robot.getstatus(), pure_i9_battery, purei9_dustbin)

        params.fan_speed = purei9.fan_speed_to_hass(
            params.fan_speed_list, self._robot.getpowermode())

        params.name = self._robot.getname()
        params.battery = purei9.battery_to_hass(pure_i9_battery)
        params.available = self._robot.isconnected()
        params.firmware = self._robot.getfirmware()
        params.dustbin = purei9.dustbin_to_hass(purei9_dustbin)

        #purei9_cleaning_sessions = self._robot.getCleaningSessions()
        #if purei9_cleaning_sessions:
        #    params.last_cleaning_session = purei9_cleaning_sessions[:0]

        return params
