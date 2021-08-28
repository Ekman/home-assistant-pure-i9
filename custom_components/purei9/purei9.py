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
    RobotStates[6]: STATE_RETURNING,
    RobotStates[7]: STATE_RETURNING,
    RobotStates[8]: STATE_PAUSED,
    RobotStates[9]: STATE_DOCKED,
    RobotStates[10]: STATE_DOCKED,
    RobotStates[11]: STATE_ERROR,
    RobotStates[12]: STATE_DOCKED,
    # RobotStates[13]: ???,
    RobotStates[14]: STATE_DOCKED
}

def state_to_hass(pure_i9_state: str) -> str:
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
    return PURE_I9_BATTERY_MAP.get(pure_i9_battery, 0)
