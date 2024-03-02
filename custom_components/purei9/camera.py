"""Home Assistant camera entity"""
import logging
from homeassistant.components.camera import Camera
from purei9_unofficial.cloud import CloudMap
from . import const

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Initial setup for the workers. Download and identify all workers."""
    data = hass.data[const.DOMAIN][config_entry.entry_id]

    entities = []

    for coord in data[const.COORDINATORS]:
        robot_id = await hass.async_add_executor_job(coord.robot.getid)
        maps = await hass.async_add_executor_job(coord.robot.getMaps)

        for map in maps:
            entities.append(PureI9Map.create(robot_id, map))

    async_add_entities(entities)

class PureI9Map(Camera):
    """Map displaying the vacuums cleaning areas"""
    def __init__(
        self,
        robot_id,
        map: CloudMap,
        unique_id,
        name,
        image
    ):
        self._robot_id = robot_id
        self._map = map
        self._unique_id = unique_id
        self._name = name
        self._image = image

    @staticmethod
    def create(robot_id: str, map: CloudMap):
        """Named constructor for creating a new instance from a CloudMap"""
        return PureI9Map(robot_id, map, map.id, map.name, map.image)

    @property
    def device_info(self):
        """Return information for the device registry"""
        # See: https://developers.home-assistant.io/docs/device_registry_index/
        return {
            "identifiers": {
                (const.DOMAIN, self._robot_id),
                (const.DOMAIN, self._unique_id)
            },
            "name": self._name,
            "manufacturer": const.MANUFACTURER,
            # We don't know the exact model, i.e. Pure i9 or Pure i9.2,
            # so only report a default model
            "default_model": const.MODEL
        }

    @property
    def unique_id(self) -> str:
        """Unique identifier to the vacuum that this map belongs to"""
        return self._unique_id

    @property
    def name(self) -> str:
        """Name of the vacuum that this map belongs to"""
        return self._name

    def camera_image(self, width = None, height = None):
        return self._image

    async def async_update(self):
        await self.hass.async_add_executor_job(self._map.get)
        self._image = self._map.image
