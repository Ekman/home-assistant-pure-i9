"""Pure i9 business logic"""
from purei9_unofficial.common import BatteryStatus, RobotStates
from homeassistant.components.vacuum import (
    STATE_CLEANING,
    STATE_DOCKED,
    STATE_ERROR,
    STATE_IDLE,
    STATE_PAUSED,
    STATE_RETURNING
)

# See: https://github.com/Phype/purei9_unofficial/blob/master/src/purei9_unofficial/common.py
PURE_I9_STATE_MAP = {
    RobotStates[1]: STATE_CLEANING,
    RobotStates[2]: STATE_PAUSED,
    RobotStates[3]: STATE_CLEANING,
    RobotStates[4]: STATE_PAUSED,
    RobotStates[5]: STATE_RETURNING,
    RobotStates[6]: STATE_PAUSED,
    RobotStates[7]: STATE_RETURNING,
    RobotStates[8]: STATE_PAUSED,
    RobotStates[9]: STATE_DOCKED,
    # RobotStates[10]: Special case, see function,
    RobotStates[11]: STATE_ERROR,
    RobotStates[12]: STATE_DOCKED,
    # RobotStates[13]: Manual steering?,
    RobotStates[14]: STATE_DOCKED
}

def state_to_hass(pure_i9_state: str, pure_i9_battery: str) -> str:
    """Translate Pure i9 data into a Home Assistant state constant"""
    # The Pure i9 will become "Sleeping" when docked and charged 100% OR when stopped.
    # In order to detect if it's docket or if it's just idling in the middle of a room
    # check the battery level. If it's full then we're docked.
    if pure_i9_state == RobotStates[10]:
        return STATE_DOCKED if pure_i9_battery == BatteryStatus[6] else STATE_IDLE

    return PURE_I9_STATE_MAP.get(pure_i9_state, STATE_IDLE)

# See: https://github.com/Phype/purei9_unofficial/blob/master/src/purei9_unofficial/common.py
PURE_I9_BATTERY_MAP = {
    BatteryStatus[1]: 0,
    BatteryStatus[2]: 20,
    BatteryStatus[3]: 40,
    BatteryStatus[4]: 60,
    BatteryStatus[5]: 80,
    BatteryStatus[6]: 100
}

def battery_to_hass(pure_i9_battery: str) -> int:
    """Translate Pure i9 data into a Home Assistant battery level"""
    return PURE_I9_BATTERY_MAP.get(pure_i9_battery, 0)

class Params:
    """Data available in the state"""
    battery: int = 100
    state: str = STATE_IDLE
    available: bool = True
    firmware: str = ""

    def __init__(self, unique_id: str, name: str):
        self._unique_id = unique_id
        self._name = name

    @property
    def unique_id(self) -> str:
        """Immutable unique identifier"""
        return self._unique_id

    @property
    def name(self) -> str:
        """Immutable name"""
        return self._name
