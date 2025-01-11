"""Home Assistant vacuum entity"""
from typing import List, Optional, Any, Mapping, Dict
import logging
import voluptuous as vol
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.components.vacuum import (
    StateVacuumEntity,
    PLATFORM_SCHEMA,
    VacuumActivity,
    VacuumEntityFeature
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.const import CONF_PASSWORD, CONF_EMAIL, CONF_COUNTRY_CODE
from purei9_unofficial.cloudv3 import CloudRobot
from . import purei9, const, vacuum_command, exception, utility

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_EMAIL): str,
    vol.Required(CONF_PASSWORD): str,
    vol.Required(CONF_COUNTRY_CODE): str
})

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Initial setup for the workers. Download and identify all workers."""
    data = hass.data[const.DOMAIN][config_entry.entry_id]

    async_add_entities(
        [PureI9(coord, coord.robot, coord.data) for coord in data[const.COORDINATORS]]
    )

# pylint: disable=R0904
class PureI9(CoordinatorEntity, StateVacuumEntity):
    """The main Pure i9 vacuum entity"""
    def __init__(
            self,
            coordinator,
            robot: CloudRobot,
            params: purei9.Params,
        ):
        super().__init__(coordinator)
        self._robot = robot
        self._params = params

    @property
    def supported_features(self) -> int:
        """Explain to Home Assistant what features are implemented"""
        # Turn on, turn off and is on is not supported by vacuums anymore
        # See: https://github.com/home-assistant/core/issues/36503
        return (
            VacuumEntityFeature.BATTERY
            | VacuumEntityFeature.START
            | VacuumEntityFeature.RETURN_HOME
            | VacuumEntityFeature.STOP
            | VacuumEntityFeature.PAUSE
            | VacuumEntityFeature.STATE
            | VacuumEntityFeature.FAN_SPEED
            | VacuumEntityFeature.SEND_COMMAND
        )

    @property
    def device_info(self) -> DeviceInfo:
        """Return information for the device registry"""
        return purei9.create_device_attrs(self._params)

    @property
    def unique_id(self) -> str:
        """Unique identifier to the vacuum"""
        return self._params.unique_id

    @property
    def name(self) -> str:
        """Name of the vacuum"""
        return self._params.name

    @property
    def battery_level(self) -> int:
        """Battery level, between 0-100"""
        return self._params.battery

    @property
    def state(self) -> str:
        """Check Home Assistant state variables"""
        return self._params.state

    @property
    def available(self) -> bool:
        """If the robot is connected to the cloud and ready for commands"""
        return self._params.available

    @property
    def error(self) -> str:
        """If the vacuum reports STATE_ERROR then explain the error"""
        # According to documentation then this is required if the entity
        # can report error states. However, I can't fetch any error message.
        if self._params.dustbin == purei9.Dustbin.DISCONNECTED:
            return "The dustbin is missing"

        if self._params.dustbin == purei9.Dustbin.FULL:
            return "The dustbin needs to be emptied"

        return "Error"

    @property
    def fan_speed(self) -> Optional[str]:
        """Return the fan speed of the vacuum cleaner."""
        return self._params.fan_speed

    @property
    def fan_speed_list(self) -> List[str]:
        """Get the list of available fan speed steps of the vacuum cleaner."""
        return self._params.fan_speed_list

    @property
    def extra_state_attributes(self) -> Mapping[str, Any]:
        """Get extra state attributes"""
        return {
            "maps": utility.array_join(
                [_map["name"] for _map in self._params.maps],
            ),
            "zones": utility.array_join(
                [zone["name"] for _map in self._params.maps for zone in _map["zones"]]
            )
        }

    async def async_start(self):
        """Start cleaning"""
        # If you click on start after clicking return, it will continue
        # returning. So we'll need to call stop first, then start in order
        # to start a clean.
        if self._params.state == VacuumActivity.RETURNING:
            await self.hass.async_add_executor_job(self._robot.stopclean)

        # According to Home Assistant, pause should be an idempotent action.
        # However, the Pure i9 will toggle pause on/off if called multiple
        # times. Circumvent that.
        if self._params.state != VacuumActivity.CLEANING:
            await self.hass.async_add_executor_job(self._robot.startclean)
            self._params.state = VacuumActivity.CLEANING
            self.async_write_ha_state()

    def start(self):
        raise NotImplementedError

    async def async_return_to_base(self, **kwargs):
        """Return to the dock"""
        await self.hass.async_add_executor_job(self._robot.gohome)
        self._params.state = VacuumActivity.RETURNING
        self.async_write_ha_state()

    def return_to_base(self, **kwargs):
        raise NotImplementedError

    async def async_stop(self, **kwargs):
        """Stop cleaning"""
        await self.hass.async_add_executor_job(self._robot.stopclean)
        self._params.state = VacuumActivity.IDLE
        self.async_write_ha_state()

    def stop(self, **kwargs):
        raise NotImplementedError

    async def async_pause(self):
        """Pause cleaning"""
        # According to Home Assistant, pause should be an idempotent
        # action. However, the Pure i9 will toggle pause on/off if
        # called multiple times. Circumvent that.
        if self._params.state != VacuumActivity.PAUSED:
            await self.hass.async_add_executor_job(self._robot.pauseclean)
            self._params.state = VacuumActivity.PAUSED
            self.async_write_ha_state()

    def pause(self):
        raise NotImplementedError

    async def async_set_fan_speed(self, fan_speed: str, **kwargs: Any):
        """Set the fan speed of the robot"""
        await self.hass.async_add_executor_job(
            self._robot.setpowermode,
            purei9.fan_speed_to_purei9(fan_speed)
        )
        self._params.fan_speed = fan_speed
        self.async_write_ha_state()

    def set_fan_speed(self, fan_speed, **kwargs):
        raise NotImplementedError

    async def async_send_command(
        self,
        command: str,
        params: Optional[Dict[str, Any]] = None,
        **kwargs: Any
    ) -> None:
        """Send a custom command to the robot. Currently only used to clean specific zones."""
        cmd = vacuum_command.create_command(command, self.hass, self._robot, self._params)

        if cmd is None:
            _LOGGER.error("Command \"%s\" not implemented.", command)
            return

        try:
            cmd.input_valid_or_throw(params)

            await cmd.execute(params)
        except exception.CommandParamException as ex:
            _LOGGER.error(
                "Need parameter \"%s\" of type \"%s\" for command \"%s\".",
                ex.param_name,
                ex.param_type,
                command
            )
        except exception.CommandException as ex:
            _LOGGER.error("Could not execute command \"%s\" due to: %s", command, ex)

    def send_command(
        self,
        command: str,
        params: dict[str, Any] | list[Any] | None = None,
        **kwargs: Any,
    ):
        raise NotImplementedError

    def _handle_coordinator_update(self):
        """
        Called by Home Assistant asking the vacuum to update to the latest state.
        Can contain IO code.
        """
        params = self.coordinator.data

        self._params.state = params.state
        self._params.fan_speed = params.fan_speed
        self._params.name = params.name
        self._params.battery = params.battery
        self._params.available = params.available
        self._params.firmware = params.firmware
        self._params.dustbin = params.dustbin
        self._params.last_cleaning_session = params.last_cleaning_session
        self._params.maps = params.maps

        self.async_write_ha_state()

    def locate(self, **kwargs):
        raise NotImplementedError

    def clean_spot(self, **kwargs):
        raise NotImplementedError
