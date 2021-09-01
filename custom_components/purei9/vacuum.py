"""Home Assistant vacuum entity"""
import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.components.vacuum import (
    SUPPORT_BATTERY,
    SUPPORT_PAUSE,
    SUPPORT_RETURN_HOME,
    SUPPORT_START,
    SUPPORT_STATE,
    SUPPORT_STOP,
    SUPPORT_TURN_ON,
    SUPPORT_TURN_OFF,
    StateVacuumEntity,
    PLATFORM_SCHEMA,
    STATE_CLEANING,
    STATE_PAUSED,
    STATE_IDLE
)
from homeassistant.const import CONF_PASSWORD, CONF_EMAIL
from purei9_unofficial.cloud import CloudClient, CloudRobot
from . import purei9

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_EMAIL): cv.string,
    vol.Required(CONF_PASSWORD): cv.string
})

def setup_platform(_hass, config, add_entities) -> None:
    """Register all Pure i9's in Home Assistant"""
    client = CloudClient(config[CONF_EMAIL], config.get(CONF_PASSWORD))
    entities = map(PureI9.create, client.getRobots())
    add_entities(entities)

class PureI9(StateVacuumEntity):
    """The main Pure i9 vacuum entity"""
    def __init__(
            self,
            robot: CloudRobot,
            _id: str,
            name: str,
            battery: int = 100,
            state: str = STATE_IDLE,
            available: bool = True
        ):
        self._robot = robot
        self._id = _id
        self._name = name
        self._battery = battery
        self._state = state
        self._available = available
        # The Pure i9 library caches results. When we do state updates, the next update
        # is sometimes cached. Override that so we can get the desired state quicker.
        self._override_next_state_update = None

    @staticmethod
    def create(robot: CloudRobot):
        """Named constructor for creating a new instance from a CloudRobot"""
        _id = robot.getid()
        name = robot.getname()
        return PureI9(robot, _id, name)

    @property
    def unique_id(self) -> str:
        """Unique identifier to the vacuum"""
        return self._id

    @property
    def available(self) -> bool:
        """If the robot is connected to the cloud and ready for commands"""
        return self._available

    @property
    def supported_features(self) -> int:
        """Explain to Home Assistant what features are implemented"""
        return (
            SUPPORT_BATTERY
            | SUPPORT_START
            | SUPPORT_RETURN_HOME
            | SUPPORT_STOP
            | SUPPORT_PAUSE
            | SUPPORT_TURN_ON
            | SUPPORT_TURN_OFF
            | SUPPORT_STATE
        )

    @property
    def name(self) -> str:
        """Name of the vacuum"""
        return self._name

    @property
    def battery_level(self) -> int:
        """Battery level, between 0-100"""
        return self._battery

    @property
    def state(self) -> str:
        """Check Home Assistant state variables"""
        return self._state

    @property
    def error(self) -> str:
        """If the vacuum reports STATE_ERROR then explain the error"""
        # According to documentation then this is required if the entity
        # can report error states. However, I can't fetch any error message.
        return "Error"

    @property
    def is_on(self) -> bool:
        """If the vacuum is on or off"""
        return self._state == STATE_CLEANING

    def start(self) -> None:
        """Start cleaning"""
        # According to Home Assistant, pause should be an idempotent action.
        # However, the Pure i9 will toggle pause on/off if called multiple
        # times. Circumvent that.
        if self._state != STATE_CLEANING:
            self._robot.startclean()
            self._override_next_state_update = self._state = STATE_CLEANING

    def return_to_base(self, **kwargs) -> None:
        """Return to the dock"""
        self._robot.gohome()

    def stop(self, **kwargs) -> None:
        """Stop cleaning"""
        self._robot.stopclean()

    def pause(self) -> None:
        """Pause cleaning"""
        if self._state != STATE_PAUSED:
            self._robot.pauseclean()
            # According to Home Assistant, pause should be an idempotent
            # action. However, the Pure i9 will toggle pause on/off if
            # called multiple times. Circumvent that.
            self._override_next_state_update = self._state = STATE_PAUSED

    def turn_on(self) -> None:
        """Turn the vacuum on"""
        self.start()

    def turn_off(self) -> None:
        """Turn the vacuum off"""
        self.stop()
        self.return_to_base()

    def update(self) -> None:
        """
        Called by Home Assistant asking the vacuum to update to the latest state.
        Can contain IO code.
        """
        pure_i9_battery = self._robot.getbattery()

        self._battery = purei9.battery_to_hass(pure_i9_battery)
        self._state = (self._override_next_state_update
                        or purei9.state_to_hass(self._robot.getstatus(), pure_i9_battery))
        self._available = self._robot.isconnected()

        self._override_next_state_update = None
