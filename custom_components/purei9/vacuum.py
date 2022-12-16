"""Home Assistant vacuum entity"""
from typing import List, Optional, Any, Mapping
from datetime import timedelta
import logging
import voluptuous as vol
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.components.vacuum import (
    SUPPORT_BATTERY,
    SUPPORT_PAUSE,
    SUPPORT_RETURN_HOME,
    SUPPORT_START,
    SUPPORT_STATE,
    SUPPORT_STOP,
    SUPPORT_FAN_SPEED,
    StateVacuumEntity,
    PLATFORM_SCHEMA,
    STATE_CLEANING,
    STATE_PAUSED,
    STATE_RETURNING,
    STATE_IDLE
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.const import CONF_PASSWORD, CONF_EMAIL
from purei9_unofficial.cloudv2 import CloudClient, CloudRobot
from purei9_unofficial.common import DustbinStates
from . import purei9, const

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_EMAIL): str,
    vol.Required(CONF_PASSWORD): str
})

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Initial setup for the workers. Download and identify all workers."""
    data = hass.data[const.DOMAIN][config_entry.entry_id]
    
    entities = []

    for entity_meta in data["entities_meta"]:
        coordinator = entity_meta["coordinator"]
        robot = entity_meta["robot"]

        entities.append(
            PureI9(coordinator, robot, coordinator.data)
        )

    async_add_entities(entities, update_before_add=True)

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
            SUPPORT_BATTERY
            | SUPPORT_START
            | SUPPORT_RETURN_HOME
            | SUPPORT_STOP
            | SUPPORT_PAUSE
            | SUPPORT_STATE
            | SUPPORT_FAN_SPEED
        )

    @property
    def device_info(self) -> DeviceInfo:
        """Return information for the device registry"""
        # See: https://developers.home-assistant.io/docs/device_registry_index/
        return {
            "identifiers": {(const.DOMAIN, self._params.unique_id)},
            "name": self._params.name,
            "manufacturer": const.MANUFACTURER,
            "sw_version": self._params.firmware,
            # We don't know the exact model, i.e. Pure i9 or Pure i9.2,
            # so only report a default model
            "default_model": const.MODEL
        }

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
        if self._params.dustbin == DustbinStates.empty:
            return "The dustbin is missing"

        if self._params.dustbin == DustbinStates.full:
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
        return {"dustbin": self._params.dustbin.name}

    async def async_start(self):
        """Start cleaning"""
        # If you click on start after clicking return, it will continue
        # returning. So we'll need to call stop first, then start in order
        # to start a clean.
        if self._params.state == STATE_RETURNING:
            await self.hass.async_add_executor_job(self._robot.stopclean)

        # According to Home Assistant, pause should be an idempotent action.
        # However, the Pure i9 will toggle pause on/off if called multiple
        # times. Circumvent that.
        if self._params.state != STATE_CLEANING:
            await self.hass.async_add_executor_job(self._robot.startclean)
            self._params.state = STATE_CLEANING
            self.async_write_ha_state()

    async def async_return_to_base(self, **kwargs):
        """Return to the dock"""
        await self.hass.async_add_executor_job(self._robot.gohome)
        self._params.state = STATE_RETURNING
        self.async_write_ha_state()

    async def async_stop(self, **kwargs):
        """Stop cleaning"""
        await self.hass.async_add_executor_job(self._robot.stopclean)
        self._params.state = STATE_IDLE
        self.async_write_ha_state()

    async def async_pause(self):
        """Pause cleaning"""
        # According to Home Assistant, pause should be an idempotent
        # action. However, the Pure i9 will toggle pause on/off if
        # called multiple times. Circumvent that.
        if self._params.state != STATE_PAUSED:
            await self.hass.async_add_executor_job(self._robot.pauseclean)
            self._params.state = STATE_PAUSED
            self.async_write_ha_state()

    async def async_set_fan_speed(self, fan_speed: str, **kwargs: Any):
        """Set the fan speed of the robot"""
        await self.hass.async_add_executor_job(
            self._robot.setpowermode,
            purei9.fan_speed_to_purei9(fan_speed)
        )
        self._params.fan_speed = fan_speed
        self.async_write_ha_state()

    async def _handle_coordinator_update(self):
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

        self.async_write_ha_state()

#####################################
### Below this is deprecated code ###
#####################################

SCAN_INTERVAL = timedelta(minutes=1)

# Deprecated way to setup this integration. Will be removed in v2.x.
def setup_platform(_hass, config, add_entities, _discovery_info=None) -> None:
    """Register all Pure i9's in Home Assistant"""
    _LOGGER.warning(
        "DEPRECATED: Setup the integration using integration UI instead of configuration.yml."
    )
    client = CloudClient(config[CONF_EMAIL], config.get(CONF_PASSWORD))
    entities = map(PureI9Legacy.create, client.getRobots())
    add_entities(entities, update_before_add=True)

class PureI9Legacy(StateVacuumEntity):
    """The main Pure i9 vacuum entity"""
    def __init__(
            self,
            robot: CloudRobot,
            params: purei9.Params,
        ):
        self._robot = robot
        self._params = params
        # The Pure i9 library caches results. When we do state updates, the next update
        # is sometimes cached. Override that so we can get the desired state quicker.
        self._assumed_next_state = None
        self._assumed_next_fan_speed = None

    @staticmethod
    def create(robot: CloudRobot):
        """Named constructor for creating a new instance from a CloudRobot"""
        purei9_fan_speed_list = list(map(lambda x: x.name, robot.getsupportedpowermodes()))
        fan_speed_list = purei9.fan_speed_list_to_hass(purei9_fan_speed_list)

        params = purei9.Params(robot.getid(), robot.getname(), fan_speed_list)
        return PureI9(robot, params)

    @property
    def supported_features(self) -> int:
        """Explain to Home Assistant what features are implemented"""
        # Turn on, turn off and is on is not supported by vacuums anymore
        # See: https://github.com/home-assistant/core/issues/36503
        return (
            SUPPORT_BATTERY
            | SUPPORT_START
            | SUPPORT_RETURN_HOME
            | SUPPORT_STOP
            | SUPPORT_PAUSE
            | SUPPORT_STATE
            | SUPPORT_FAN_SPEED
        )

    @property
    def device_info(self) -> DeviceInfo:
        """Return information for the device registry"""
        # See: https://developers.home-assistant.io/docs/device_registry_index/
        return {
            "identifiers": {(const.DOMAIN, self._params.unique_id)},
            "name": self._params.name,
            "manufacturer": const.MANUFACTURER,
            "sw_version": self._params.firmware,
            # We don't know the exact model, i.e. Pure i9 or Pure i9.2,
            # so only report a default model
            "default_model": const.MODEL
        }

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
        if self._params.dustbin == DustbinStates.empty:
            return "The dustbin is missing"

        if self._params.dustbin == DustbinStates.full:
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
    def assumed_state(self) -> bool:
        """Assume the next state after sending a command"""
        return (self._assumed_next_state is not None
            or self._assumed_next_fan_speed is not None)

    @property
    def extra_state_attributes(self) -> Mapping[str, Any]:
        return {"dustbin": self._params.dustbin.name}

    def start(self) -> None:
        """Start cleaning"""
        # If you click on start after clicking return, it will continue
        # returning. So we'll need to call stop first, then start in order
        # to start a clean.
        if self._params.state == STATE_RETURNING:
            self._robot.stopclean()

        # According to Home Assistant, pause should be an idempotent action.
        # However, the Pure i9 will toggle pause on/off if called multiple
        # times. Circumvent that.
        if self._params.state != STATE_CLEANING:
            self._robot.startclean()
            self._assumed_next_state = STATE_CLEANING

    def return_to_base(self, **kwargs) -> None:
        """Return to the dock"""
        self._robot.gohome()
        self._assumed_next_state = STATE_RETURNING

    def stop(self, **kwargs) -> None:
        """Stop cleaning"""
        self._robot.stopclean()
        self._assumed_next_state = STATE_IDLE

    def pause(self) -> None:
        """Pause cleaning"""
        # According to Home Assistant, pause should be an idempotent
        # action. However, the Pure i9 will toggle pause on/off if
        # called multiple times. Circumvent that.
        if self._params.state != STATE_PAUSED:
            self._robot.pauseclean()
            self._assumed_next_state = STATE_PAUSED

    def set_fan_speed(self, fan_speed: str, **kwargs: Any) -> None:
        """Set the fan speed of the robot"""
        self._robot.setpowermode(purei9.fan_speed_to_purei9(fan_speed))
        self._assumed_next_fan_speed = fan_speed

    def update(self) -> None:
        """
        Called by Home Assistant asking the vacuum to update to the latest state.
        Can contain IO code.
        """
        pure_i9_battery = self._robot.getbattery()
        purei9_dustbin = self._robot.getdustbinstatus()

        if self._assumed_next_state is not None:
            self._params.state = self._assumed_next_state
            self._assumed_next_state = None
        else:
            self._params.state = purei9.state_to_hass(
                self._robot.getstatus(), pure_i9_battery, purei9_dustbin)

        if self._assumed_next_fan_speed is not None:
            self._params.fan_speed = self._assumed_next_fan_speed
            self._assumed_next_fan_speed = None
        else:
            self._params.fan_speed = purei9.fan_speed_to_hass(
                self._params.fan_speed_list, self._robot.getpowermode())

        self._params.name = self._robot.getname()
        self._params.battery = purei9.battery_to_hass(pure_i9_battery)
        self._params.available = self._robot.isconnected()
        self._params.firmware = self._robot.getfirmware()
        self._params.dustbin = purei9.dustbin_to_hass(purei9_dustbin)
