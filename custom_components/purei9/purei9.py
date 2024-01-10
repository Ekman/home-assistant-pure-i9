"""Pure i9 business logic"""
from typing import List, TypedDict
from enum import Enum
from purei9_unofficial.common import (
    BatteryStatus,
    RobotStates,
    PowerMode,
    DustbinStates,
    CleaningSession,
)
from homeassistant.components.vacuum import (
    STATE_CLEANING,
    STATE_DOCKED,
    STATE_ERROR,
    STATE_IDLE,
    STATE_PAUSED,
    STATE_RETURNING
)
from . import const

# See: https://github.com/Phype/purei9_unofficial/blob/master/src/purei9_unofficial/common.py
PURE_I9_STATE_MAP = {
    RobotStates.Cleaning: STATE_CLEANING,
    RobotStates.Paused_Cleaning: STATE_PAUSED,
    RobotStates.Spot_Cleaning: STATE_CLEANING,
    RobotStates.Paused_Spot_Cleaning: STATE_PAUSED,
    RobotStates.Return: STATE_RETURNING,
    RobotStates.Paused_Return: STATE_PAUSED,
    RobotStates.Return_for_Pitstop: STATE_RETURNING,
    RobotStates.Paused_Return_for_Pitstop: STATE_PAUSED,
    RobotStates.Charging: STATE_DOCKED,
    # RobotStates.Sleeping: Special case, see function,
    RobotStates.Error: STATE_ERROR,
    RobotStates.Pitstop: STATE_DOCKED,
    # RobotStates.Manual_Steering: Manual steering?,
    RobotStates.Firmware_Upgrade: STATE_DOCKED
}

def state_to_hass(
    pure_i9_state: str,
    pure_i9_battery: str,
    purei9_dustbin: DustbinStates=DustbinStates.connected
    ) -> str:
    """Translate Pure i9 data into a Home Assistant state constant"""
    # The Pure i9 will become "Sleeping" when docked and charged 100% OR when stopped.
    # In order to detect if it's docket or if it's just idling in the middle of a room
    # check the battery level. If it's full then we're docked.
    if purei9_dustbin in (DustbinStates.empty, DustbinStates.full):
        return STATE_ERROR

    if pure_i9_state == RobotStates.Sleeping:
        return STATE_DOCKED if pure_i9_battery == BatteryStatus.High else STATE_IDLE

    return PURE_I9_STATE_MAP.get(pure_i9_state, STATE_IDLE)

# See: https://github.com/Phype/purei9_unofficial/blob/master/src/purei9_unofficial/common.py
PURE_I9_BATTERY_MAP = {
    BatteryStatus.Dead: 0,
    BatteryStatus.CriticalLow: 20,
    BatteryStatus.Low: 40,
    BatteryStatus.Medium: 60,
    BatteryStatus.Normal: 80,
    BatteryStatus.High: 100
}

def battery_to_hass(pure_i9_battery: str) -> int:
    """Translate Pure i9 data into a Home Assistant battery level"""
    return PURE_I9_BATTERY_MAP.get(pure_i9_battery, 0)

POWER_MODE_ECO = "ECO"
POWER_MODE_POWER = "POWER"
POWER_MODE_QUIET = "QUIET"
POWER_MODE_SMART = "SMART"

class Dustbin(Enum):
    """Contains possible values for the dustbin"""
    UNKNOWN = 1
    CONNECTED = 2
    DISCONNECTED = 3
    FULL = 4

class ParamsIdName(TypedDict):
    id: str
    name: str

class ParamsZone(ParamsIdName):
    id: str

def params_zone_create(zone) -> ParamsZone:
    return {
        "id": zone.id,
        "name": zone.name
    }

class ParamsMap(ParamsIdName):
    zones: List[ParamsZone]

def params_map_create(m) -> ParamsMap:
    return {
        "id": m.id,
        "name": m.name,
        "zones": list(map(params_zone_create, m.zones))
    }

# pylint: disable=too-many-instance-attributes
class Params:
    """Data available in the state"""
    battery: int = 100
    state: str = STATE_IDLE
    available: bool = True
    firmware: str = None
    fan_speed: str = POWER_MODE_POWER
    dustbin: Dustbin = Dustbin.CONNECTED
    last_cleaning_session: CleaningSession = None
    maps: List[ParamsMap] = []

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

def dustbin_to_hass(dustbin: DustbinStates) -> Dustbin:
    """Conver the Pure i9 dustbin into an internal representation"""
    if dustbin == DustbinStates.unset:
        return Dustbin.UNKNOWN

    if dustbin == DustbinStates.connected:
        return Dustbin.CONNECTED

    if dustbin == DustbinStates.empty:
        return Dustbin.DISCONNECTED

    return Dustbin.FULL

def create_device_attrs(params: Params):
    """Return information for the device registry"""
    # See: https://developers.home-assistant.io/docs/device_registry_index/
    return {
        "identifiers": {(const.DOMAIN, params.unique_id)},
        "name": params.name,
        "manufacturer": const.MANUFACTURER,
        "sw_version": params.firmware,
        # We don't know the exact model, i.e. Pure i9 or Pure i9.2,
        # so only report a default model
        "model": const.MODEL
    }
