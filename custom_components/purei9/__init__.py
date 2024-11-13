"""Control your Electrolux Purei9 vacuum robot"""
import asyncio
from homeassistant.const import CONF_PASSWORD, CONF_EMAIL, CONF_COUNTRY_CODE
from purei9_unofficial.cloudv3 import CloudClient
from . import const, coordinator

PLATFORMS = ["vacuum", "sensor"]

async def async_setup_entry(hass, config_entry) -> bool:
    """Setup the integration after the config flow"""
    email = config_entry.data.get(CONF_EMAIL)
    password = config_entry.data.get(CONF_PASSWORD)
    countrycode = config_entry.data.get(CONF_COUNTRY_CODE)

    purei9_client = CloudClient(email, password, countrycode=countrycode)

    robots = await hass.async_add_executor_job(purei9_client.getRobots)
    robots = list(robots)

    # Download and cache all robots
    await asyncio.gather(
        *[hass.async_add_executor_job(robot.getid) for robot in robots]
    )

    # Create the coordinators
    coords = [coordinator.PureI9Coordinator(hass, robot.getid(), robot) for robot in robots]

    await asyncio.gather(
        *[coord.async_config_entry_first_refresh() for coord in coords]
    )

    # Continue with setting up devices and entities
    hass.data.setdefault(const.DOMAIN, {})
    hass.data[const.DOMAIN][config_entry.entry_id] = {const.COORDINATORS: coords}

    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

    return True
