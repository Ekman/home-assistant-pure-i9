"""Control your Electrolux Purei9 vacuum robot"""

async def async_setup_entry(hass, config_entry) -> bool:
    """Setup the integration after the config flow"""
    await hass.config_entries.async_forward_entry_setups(config_entry, ["vacuum"])
    return True
