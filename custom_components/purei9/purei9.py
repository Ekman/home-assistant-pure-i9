"""Pure i9 business logic"""
from typing import List
from purei9_unofficial.common import BatteryStatus, RobotStates, PowerMode
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

POWER_MODE_ECO = "ECO"
POWER_MODE_POWER = "POWER"
POWER_MODE_QUIET = "QUIET"
POWER_MODE_SMART = "SMART"

class Params:
    """Data available in the state"""
    battery: int = 100
    state: str = STATE_IDLE
    available: bool = True
    firmware: str = None
    fan_speed: str = POWER_MODE_POWER

    def __init__(self, unique_id: str, name: str, fan_speed_list: List[str]):
        self._unique_id = unique_id
        self.name = name
        self._fan_speed_list = fan_speed_list

    @property
    def unique_id(self) -> str:
        """Immutable unique identifier"""
        return self._unique_id

    @property
    def fan_speed_list(self) -> str:
        """Immutable fan speed list"""
        return self._fan_speed_list

def is_power_mode_v2(fan_speed_list: List[str]) -> bool:
    """Determine if the robot supports the new or old fan speed list """
    return len(fan_speed_list) == 3

def fan_speed_list_to_hass(fan_speed_list_purei9: List[str]) -> List[str]:
    """Convert the fan speed list to internal representation"""
    if is_power_mode_v2(fan_speed_list_purei9):
        return list([POWER_MODE_QUIET, POWER_MODE_SMART, POWER_MODE_POWER])

    return list([POWER_MODE_ECO, POWER_MODE_POWER])

def fan_speed_to_purei9(fan_speed_hass: str) -> PowerMode:
    """Convert our internal representation of a fan speed to one that Purei9 can understand"""
    if fan_speed_hass == POWER_MODE_POWER:
        return PowerMode.HIGH

    if fan_speed_hass == POWER_MODE_QUIET:
        return PowerMode.LOW

    return PowerMode.MEDIUM

def fan_speed_to_hass(fan_speed_list: List[str], fan_speed_purei9: PowerMode) -> str:
    """Convert Purei9 fan sped to our internal representation"""
    if is_power_mode_v2(fan_speed_list):
        if fan_speed_purei9 == PowerMode.LOW:
            return POWER_MODE_QUIET

        if fan_speed_purei9 == PowerMode.MEDIUM:
            return POWER_MODE_SMART
    elif fan_speed_purei9 == PowerMode.MEDIUM:
        return POWER_MODE_ECO

    return POWER_MODE_POWER
