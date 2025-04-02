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
from purei9_unofficial.cloudv3 import CloudZone, CloudMap
from homeassistant.components.vacuum import (
    VacuumActivity
)
from . import const

# See: https://github.com/Phype/purei9_unofficial/blob/master/src/purei9_unofficial/common.py
PURE_I9_STATE_MAP = {
    RobotStates.Cleaning: VacuumActivity.CLEANING,
    RobotStates.Paused_Cleaning: VacuumActivity.PAUSED,
    RobotStates.Spot_Cleaning: VacuumActivity.CLEANING,
    RobotStates.Paused_Spot_Cleaning: VacuumActivity.PAUSED,
    RobotStates.Return: VacuumActivity.RETURNING,
    RobotStates.Paused_Return: VacuumActivity.PAUSED,
    RobotStates.Return_for_Pitstop: VacuumActivity.RETURNING,
    RobotStates.Paused_Return_for_Pitstop: VacuumActivity.PAUSED,
    RobotStates.Charging: VacuumActivity.DOCKED,
    # RobotStates.Sleeping: Special case, see function,
    RobotStates.Error: VacuumActivity.ERROR,
    RobotStates.Pitstop: VacuumActivity.DOCKED,
    # RobotStates.Manual_Steering: Manual steering?,
    RobotStates.Firmware_Upgrade: VacuumActivity.DOCKED
}

def state_to_hass(
    pure_i9_state: str,
    pure_i9_battery: str
    ) -> str:
    """Translate Pure i9 data into a Home Assistant state constant"""
    # The Pure i9 will become "Sleeping" when docked and charged 100% OR when stopped.
    # In order to detect if it's docket or if it's just idling in the middle of a room
    # check the battery level. If it's full then we're docked.
    if pure_i9_state == RobotStates.Sleeping:
        return VacuumActivity.DOCKED if pure_i9_battery == BatteryStatus.High else VacuumActivity.IDLE

    return PURE_I9_STATE_MAP.get(pure_i9_state, VacuumActivity.IDLE)

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

class ParamsZone(TypedDict):
    """Type for a map zone"""
    id: str
    name: str

def params_zone_create(cloud_zone: CloudZone) -> ParamsZone:
    """Create a map zone from a CloudZone"""
    return {
        "id": cloud_zone.id,
        "name": cloud_zone.name
    }

class ParamsMap(TypedDict):
    """Type for a map"""
    id: str
    name: str
    zones: List[ParamsZone]

def params_map_create(cloud_map: CloudMap) -> ParamsMap:
    """Create a map zone from a CloudRobot"""
    return {
        "id": cloud_map.id,
        "name": cloud_map.name,
        "zones": list(map(params_zone_create, cloud_map.zones))
    }

# pylint: disable=too-many-instance-attributes
class Params:
    """Data available in the state"""
    battery: int = 100
    state: str = VacuumActivity.IDLE
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
