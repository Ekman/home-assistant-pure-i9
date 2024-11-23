"""Initial user configuration for the integration"""
import logging
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD, CONF_COUNTRY_CODE
from homeassistant.helpers.selector import CountrySelector
from purei9_unofficial.cloudv3 import CloudClient
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

class HiveOsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Configuration flow"""
    VERSION = 1

    def show_form(self, step_id, errors):
        schema = vol.Schema({
            vol.Required(CONF_EMAIL): str,
            vol.Required(CONF_PASSWORD): str,
            vol.Required(CONF_COUNTRY_CODE): CountrySelector(),
        })

        return self.async_show_form(step_id=step_id, data_schema=schema, errors=errors)

    def try_login(self, user_input):
        # Validate that the provided credentials are correct
        email = user_input[CONF_EMAIL]
        password = user_input[CONF_PASSWORD]
        countrycode = user_input[CONF_COUNTRY_CODE]

        purei9_client = CloudClient(email, password, countrycode=countrycode)
        return self.hass.async_add_executor_job(purei9_client.tryLogin)

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            try:
                await self.try_login(user_input)

                return self.async_create_entry(
                    title=email,
                    data=user_input
                )
            # pylint: disable=broad-except
            except Exception:
                errors["base"] = "auth"

        return self.show_form("user", errors)

    async def async_step_reconfigure(self, user_input=None):
        errors = {}

        if user_input is not None:
            try:
                await self.try_login(user_input)

                email = user_input[CONF_EMAIL]

                self.async_set_unique_id(email)
                self._abort_if_unique_id_mismatch()

                return self.async_update_reload_and_abort(
                    self._get_reconfigure_entry(),
                    data_updates=user_input,
                )
            # pylint: disable=broad-except
            except Exception:
                errors["base"] = "auth"

        return self.show_form("reconfigure", errors)
