"""Initial user configuration for the integration"""
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD, CONF_COUNTRY_CODE
from purei9_unofficial.cloudv3 import CloudClient
from .const import DOMAIN

class HiveOsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Configuration flow"""
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            try:
                # Validate that the provided credentials are correct
                email = user_input[CONF_EMAIL]
                password = user_input[CONF_PASSWORD]
                countrycode = user_input[CONF_COUNTRY_CODE]

                purei9_client = CloudClient(email, password, countrycode=countrycode)
                await self.hass.async_add_executor_job(purei9_client.tryLogin)

                return self.async_create_entry(
                    title=email,
                    data=user_input
                )
            # pylint: disable=broad-except
            except Exception:
                errors["base"] = "auth"

        schema = vol.Schema({
            vol.Required(CONF_EMAIL): str,
            vol.Required(CONF_PASSWORD): str,
            vol.Required(CONF_COUNTRY_CODE): str,
        })

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
