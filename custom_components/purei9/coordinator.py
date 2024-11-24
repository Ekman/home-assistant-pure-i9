"""Coordinate data updates from Pure i9."""
import logging
from datetime import timedelta
from asyncio import timeout
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
        async with timeout(10):
            return await self.hass.async_add_executor_job(
                self.update_and_create_params
            )

    def update_and_create_params(self):
        """Update and create the latest version of params."""
        purei9_fan_speed_list = list(map(lambda x: x.name, self._robot.getsupportedpowermodes()))
        fan_speed_list = purei9.fan_speed_list_to_hass(purei9_fan_speed_list)

        params = purei9.Params(self._robot.getid(), self._robot.getname(), fan_speed_list)

        pure_i9_battery = self._robot.getbattery()

        params.state = purei9.state_to_hass(
            self._robot.getstatus(), pure_i9_battery)

        params.fan_speed = purei9.fan_speed_to_hass(
            params.fan_speed_list, self._robot.getpowermode())

        params.name = self._robot.getname()
        params.battery = purei9.battery_to_hass(pure_i9_battery)
        params.available = self._robot.isconnected()
        params.firmware = self._robot.getfirmware()
        params.dustbin = purei9.dustbin_to_hass(self._robot.getdustbinstatus())

        params.last_cleaning_session = self.get_last_cleaning_session()
        _LOGGER.debug("Has last cleaning session? %s", params.last_cleaning_session is not None)

        # Temporarily commented out until we can figure out:
        # https://github.com/Phype/purei9_unofficial/issues/30
        #params.maps = list(map(purei9.params_map_create, self._robot.getMaps()))
        #_LOGGER.debug(
        #    "Downloaded \"%d\" maps for \"%s\".",
        #    len(params.maps),
        #    self._robot.getname()
        #)

        return params

    def get_last_cleaning_session(self):
        """Get the latest cleaning session"""
        purei9_cleaning_sessions = self._robot.getCleaningSessions()
        _LOGGER.debug(
            "Downloaded \"%d\" cleaning sessions for \"%s\".",
            len(purei9_cleaning_sessions),
            self._robot.getname()
        )

        return (
            purei9_cleaning_sessions[0]
            if purei9_cleaning_sessions
            else None
        )
