"""Initial user configuration for the integration"""
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD
from purei9_unofficial.cloudv2 import CloudClient
from .const import DOMAIN

class HiveOsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Configuration flow"""
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            try:
                # Validate that the provided access token is correct
                email = user_input[CONF_EMAIL]
                password = user_input[CONF_PASSWORD]

                purei9_client = CloudClient(email, password)
                await self.hass.async_add_executor_job(purei9_client.tryLogin)

                return self.async_create_entry(
                    title="Home",
                    data=user_input
                )
            except:
                errors["base"] = "auth"

        schema = vol.Schema({
            vol.Required(CONF_EMAIL): str,
            vol.Required(CONF_PASSWORD): str
        })

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
