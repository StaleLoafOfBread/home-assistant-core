"""Config flow for Alert."""

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import (
    CONF_ENTITY_ID,
    CONF_NAME,
    CONF_REPEAT,
    CONF_STATE,
    STATE_ON,
)
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.selector import (
    EntitySelector,
    EntitySelectorConfig,
    ObjectSelector,
    TemplateSelector,
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)
from homeassistant.util import slugify

from .const import (
    CONF_ALERT_MESSAGE,
    CONF_CAN_ACK,
    CONF_DATA,
    CONF_DONE_MESSAGE,
    CONF_NOTIFIERS,
    CONF_SKIP_FIRST,
    CONF_TITLE,
    DEFAULT_CAN_ACK,
    DEFAULT_SKIP_FIRST,
    DOMAIN,
)

DEFAULT_REPEAT = 60

FORM_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): cv.string,
        vol.Required(CONF_ENTITY_ID): EntitySelector(),
        vol.Optional(CONF_TITLE): cv.string,
        vol.Optional(CONF_STATE, default=STATE_ON): cv.string,
        vol.Required(CONF_REPEAT, default=DEFAULT_REPEAT): TextSelector(
            TextSelectorConfig(type=TextSelectorType.NUMBER, multiple=True)
        ),
        vol.Optional(CONF_CAN_ACK, default=DEFAULT_CAN_ACK): cv.boolean,
        vol.Optional(CONF_SKIP_FIRST, default=DEFAULT_SKIP_FIRST): cv.boolean,
        vol.Optional(CONF_ALERT_MESSAGE): TemplateSelector(),
        vol.Optional(CONF_DONE_MESSAGE): TemplateSelector(),
        vol.Optional(CONF_NOTIFIERS): EntitySelector(
            EntitySelectorConfig(domain="notify")
        ),
        vol.Optional(CONF_DATA): ObjectSelector(),
    }
)


class AlertConfigFlow(ConfigFlow, domain=DOMAIN):
    """Alert config flow."""

    async def async_step_user(self, user_input) -> ConfigFlowResult:
        """Handle Alert config flow."""

        if user_input is None:
            return self.async_show_form(step_id="user", data_schema=FORM_DATA_SCHEMA)

        await self.async_set_unique_id(slugify(user_input[CONF_NAME]))
        self._abort_if_unique_id_configured()

        return self.async_create_entry(
            title=self.unique_id,
            data=user_input,
        )
