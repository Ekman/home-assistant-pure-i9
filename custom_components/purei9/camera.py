"""Home Assistant camera entity"""
import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components.camera import Camera, PLATFORM_SCHEMA
from purei9_unofficial.cloud import CloudRobot, CloudMap, CloudClient
from homeassistant.const import CONF_PASSWORD, CONF_EMAIL
from . import purei9

def setup_platform(
    hass: HomeAssistant, config: ConfigEntry, add_entities: AddEntitiesCallback, discovery_info=None
) -> None:
    """Register all Pure i9's in Home Assistant"""
    if discovery_info is not None:
        client = CloudClient(config[CONF_EMAIL], config[CONF_PASSWORD])

        cameras = []
        for robot in client.getRobots():
            robotName = robot.getname()
            for map in robot.getMaps():
                cameras.append(PureI9Map.create(map, robotName))

        if cameras:
            add_entities(cameras, update_before_add=True)

class PureI9Map(Camera):
    """Map displaying the vacuums cleaning areas"""
    def __init__(self, map: CloudMap, params: purei9.HomeAssistantCameraParams):
        super().__init__()
        self._map = map
        self._params = params

    @staticmethod
    def create(map: CloudMap, robotName: str):
        """Named constructor for creating a new instance from a CloudMap"""
        params = purei9.HomeAssistantCameraParams(map.id, robotName)
        return PureI9Map(map, params)

    @property
    def unique_id(self) -> str:
        """Unique identifier to the vacuum that this map belongs to"""
        return self._params.unique_id

    @property
    def name(self) -> str:
        """Name of the vacuum that this map belongs to"""
        return self._params.name

    def camera_image(self, width = None, height = None):
        return self._params.image

    def update(self) -> None:
        self._map.get()
        self._params.image = self._map.image

