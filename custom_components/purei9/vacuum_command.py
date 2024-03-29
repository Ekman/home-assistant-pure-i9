"""Vacuum commands"""
from typing import Dict, Any
from . import exception, utility

COMMAND_CLEAN_ZONES = "clean_zones"

class CommandBase:
    """Base class for all vacuum commands"""
    def __init__(self, hass, robot, params):
        super().__init__()
        self.hass = hass
        self.robot = robot
        self.params = params

    # pylint: disable=unused-argument
    def input_valid_or_throw(self, params: Dict[str, Any]) -> None:
        """Check for required input data"""

    # pylint: disable=unused-argument
    async def execute(self, params: Dict[str, Any]) -> None:
        """Execute the command"""
        return None

class CommandCleanZones(CommandBase):
    """Command to clean zones"""
    def input_valid_or_throw(self, params: Dict[str, Any]) -> None:
        if params is None:
            raise exception.CommandParamException("params", "Dict")

        if not "map" in params:
            raise exception.CommandParamException("map", "string")

        if not "zones" in params:
            raise exception.CommandParamException("zones", "List")

    async def execute(self, params: Dict[str, Any]) -> None:
        map_name = params["map"]

        _map = utility.first_or_default(
            self.params.maps,
            lambda _map: _map["name"] == map_name
        )

        if _map is None:
            raise exception.CommandException(
                f"Map \"{map_name}\" does not exist for robot \"{self.params.name}\"."
            )

        # Search all zones inside this map for the ones we are looking for
        zone_ids = [zone["id"] for zone in _map["zones"] if zone["name"] in params["zones"]]

        if len(zone_ids) == 0:
            raise exception.CommandException(f"Could not find any zones in map \"{map_name}\".")

        # Everything done, now send the robot to clean those maps and zones we found
        await self.hass.async_add_executor_job(self.robot.cleanZones, _map["id"], zone_ids)

def create_command(command_name, hass, robot, params) -> CommandBase:
    """Creates a command object from a command name"""
    if command_name == COMMAND_CLEAN_ZONES:
        return CommandCleanZones(hass, robot, params)

    return None
