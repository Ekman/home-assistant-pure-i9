import homeassistant.helpers.config_validation as cv
import voluptuous as vol

from homeassistant.components.vacuum import (
    SUPPORT_BATTERY,
    SUPPORT_PAUSE,
    SUPPORT_RETURN_HOME,
    SUPPORT_START,
    SUPPORT_STATE,
    SUPPORT_STATUS,
    SUPPORT_STOP,
    StateVacuumEntity,
    PLATFORM_SCHEMA
)
from homeassistant.const import CONF_PASSWORD, CONF_EMAIL
from purei9_unofficial.cloud import CloudClient, CloudRobot
from . import purei9

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_EMAIL): cv.string,
    vol.Required(CONF_PASSWORD): cv.string
})

def setup_platform(hass, config, add_entities, discovery_info = None) -> None:
    client = CloudClient(config[CONF_EMAIL], config.get(CONF_PASSWORD))
    entities = map(PureI9.create, client.getRobots())
    add_entities(entities)

class PureI9(StateVacuumEntity):
    def __init__(self, robot: CloudRobot, id: str, name: str, battery: int, state: str, available: bool):
        self._robot = robot
        self._id = id
        self._name = name
        self._battery = battery
        self._state = state
        self._available = available

    @staticmethod
    def create(robot: CloudRobot):
        id = robot.getid()
        name = robot.getname()
        battery = purei9.battery_to_hass(robot.getbattery())
        state = purei9.state_to_hass(robot.getstatus())
        available = robot.isconnected()
        return PureI9(robot, id, name, battery, state, available)

    @property
    def unique_id(self) -> str:
        return self._id

    @property
    def available(self) -> bool:
        return self._available

    @property
    def supported_features(self) -> int:
        return SUPPORT_BATTERY | SUPPORT_START | SUPPORT_RETURN_HOME | SUPPORT_STOP | SUPPORT_PAUSE | SUPPORT_STATE

    @property
    def name(self) -> str:
        return self._name

    @property
    def battery_level(self) -> int:
        return self._battery

    @property
    def state(self) -> str:
        return self._state

    @property
    def error(self) -> str:
        # According to documentation then this is required if the entity can report error states
        # However, I can't fetch any error message
        return "Error"

    def start(self) -> None:
        self._robot.startclean()

    def return_to_base(self) -> None:
        self._robot.gohome()

    def stop(self) -> None:
        self._robot.stopclean()

    def pause(self) -> None:
        self._robot.pauseclean()

    def update(self) -> None:
        self._battery = purei9.battery_to_hass(self._robot.getbattery())
        self._state = purei9.state_to_hass(self._robot.getstatus())
        self._available = self._robot.isconnected()
