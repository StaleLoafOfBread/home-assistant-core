"""Support for repeating alerts when conditions are met."""

from __future__ import annotations

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_ENTITY_ID,
    CONF_NAME,
    CONF_REPEAT,
    CONF_STATE,
    SERVICE_TOGGLE,
    SERVICE_TURN_OFF,
    SERVICE_TURN_ON,
    STATE_ON,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.entity_component import EntityComponent
from homeassistant.helpers.typing import ConfigType
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
    LOGGER,
)
from .entity import AlertEntity

ALERT_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): cv.string,
        vol.Required(CONF_ENTITY_ID): cv.entity_id,
        vol.Optional(CONF_STATE, default=STATE_ON): cv.string,
        vol.Required(CONF_REPEAT): vol.All(
            cv.ensure_list,
            [vol.Coerce(float)],
            # Minimum delay is 1 second = 0.016 minutes
            [vol.Range(min=0.016)],
        ),
        vol.Optional(CONF_CAN_ACK, default=DEFAULT_CAN_ACK): cv.boolean,
        vol.Optional(CONF_SKIP_FIRST, default=DEFAULT_SKIP_FIRST): cv.boolean,
        vol.Optional(CONF_ALERT_MESSAGE): cv.template,
        vol.Optional(CONF_DONE_MESSAGE): cv.template,
        vol.Optional(CONF_TITLE): cv.template,
        vol.Optional(CONF_DATA): dict,
        vol.Optional(CONF_NOTIFIERS, default=list): vol.All(
            cv.ensure_list, [cv.string]
        ),
    }
)

CONFIG_SCHEMA = vol.Schema(
    {DOMAIN: cv.schema_with_slug_keys(ALERT_SCHEMA)}, extra=vol.ALLOW_EXTRA
)


# https://developers.home-assistant.io/docs/config_entries_index/#setting-up-an-entry
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Alert from a config entry."""

    # Validate and cast the data using ALERT_SCHEMA
    try:
        # Retrieve configuration data from the entry
        cfg = dict(entry.data)

        # This will validate and coerce the data into the correct format
        cfg = ALERT_SCHEMA(cfg)
    except vol.Invalid as err:
        # Handle validation errors here, such as logging the error
        LOGGER.error(f"Error validating data: {err}")
        return False

    name = cfg[CONF_NAME]
    watched_entity_id = cfg[CONF_ENTITY_ID]
    alert_state = cfg[CONF_STATE]
    repeat = cfg[CONF_REPEAT]
    skip_first = cfg[CONF_SKIP_FIRST]
    message_template = cfg.get(CONF_ALERT_MESSAGE)
    done_message_template = cfg.get(CONF_DONE_MESSAGE)
    notifiers = cfg[CONF_NOTIFIERS]
    can_ack = cfg[CONF_CAN_ACK]
    title_template = cfg.get(CONF_TITLE)
    data = cfg.get(CONF_DATA)

    # Log all the keys in cfg
    LOGGER.warning("****************cfg*****************")
    for k, v in cfg.items():
        LOGGER.warning(f"{k}:{v}")
    LOGGER.warning("*********************************")
    # Create the AlertEntity instance
    alert_entity = AlertEntity(
        hass,
        slugify(name),
        name,
        watched_entity_id,
        alert_state,
        repeat,
        skip_first,
        message_template,
        done_message_template,
        notifiers,
        can_ack,
        title_template,
        data,
    )

    # Create the EntityComponent and add the entity to it
    component = EntityComponent[AlertEntity](LOGGER, DOMAIN, hass)
    await component.async_add_entities([alert_entity])

    return True


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Alert component."""
    component = EntityComponent[AlertEntity](LOGGER, DOMAIN, hass)

    entities: list[AlertEntity] = []

    for object_id, cfg in config[DOMAIN].items():
        if not cfg:
            cfg = {}

        name = cfg[CONF_NAME]
        watched_entity_id = cfg[CONF_ENTITY_ID]
        alert_state = cfg[CONF_STATE]
        repeat = cfg[CONF_REPEAT]
        skip_first = cfg[CONF_SKIP_FIRST]
        message_template = cfg.get(CONF_ALERT_MESSAGE)
        done_message_template = cfg.get(CONF_DONE_MESSAGE)
        notifiers = cfg[CONF_NOTIFIERS]
        can_ack = cfg[CONF_CAN_ACK]
        title_template = cfg.get(CONF_TITLE)
        data = cfg.get(CONF_DATA)

        entities.append(
            AlertEntity(
                hass,
                object_id,
                name,
                watched_entity_id,
                alert_state,
                repeat,
                skip_first,
                message_template,
                done_message_template,
                notifiers,
                can_ack,
                title_template,
                data,
            )
        )

    if not entities:
        return False

    component.async_register_entity_service(SERVICE_TURN_OFF, None, "async_turn_off")
    component.async_register_entity_service(SERVICE_TURN_ON, None, "async_turn_on")
    component.async_register_entity_service(SERVICE_TOGGLE, None, "async_toggle")

    await component.async_add_entities(entities)

    return True
