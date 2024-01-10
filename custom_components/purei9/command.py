from typing import Protocol, Dict, Any
from asyncio import Future
from . import exception, utility

COMMAND_CLEAN_ZONES = "clean_zones"

class CommandBase(Protocol):
    def __init(self, hass, robot, params):
        self.hass = hass
        self.robot = robot
        self.params = params

    @property
    def name(self) -> str:
        return "vacuum_command"

    def valid_or_throw(params: Dict[str, Any]) -> None:
        """Check for required input data"""
        return

    def execute() -> Future:
        return None

class CommandCleanZones(CommandBase):
    def __init(self, hass, robot, params):
        super().__init__(hass, robot, params)

    @property
    def name(self) -> str:
        return COMMAND_CLEAN_ZONES

    def valid_or_throw(params: Dict[str, Any]) -> None:
        """Check for required input data"""
        if params is None:
            raise exception.CommandParamException("params", "Dict")

        if not "map" in params:
            raise exception.CommandParamException("map", "string")

        if not "zones" in params:
            raise exception.CommandParamException("zones", "List")

    async def execute(params: Dict[str, Any]) -> Future:
        m = utility.first_or_default(self._params.maps, params["map"])

        if m is None:
            raise exception.CommandException("Map \"%s\" does not exist.", params["map"])

        # Search all zones inside this map for the ones we are looking for
        zone_ids = [zone.id for zone in m.zones if zone.name in params["zones"]]

        if len(zone_ids) == 0:
            raise exception.CommandException("Could not find any zones in map \"%s\".", m.name)

        # Everything done, now send the robot to clean those maps and zones we found
        await self.hass.async_add_executor_job(cself._robot.cleanZones, m.id, zone_ids)

def create_command(command: str) -> CommandBase:
    if command == COMMAND_CLEAN_ZONES:
        return CommandCleanZones()

    return None
