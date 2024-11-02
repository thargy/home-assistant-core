"""Config flow for area_network integration."""

from __future__ import annotations

from collections.abc import Callable, Coroutine, Mapping
import logging
from typing import Any, cast

import voluptuous as vol

from homeassistant.const import CONF_ICON, CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import selector
from homeassistant.helpers.schema_config_entry_flow import (
    SchemaCommonFlowHandler,
    SchemaConfigFlowHandler,
    SchemaFlowFormStep,
    SchemaFlowMenuStep,
    SchemaOptionsFlowHandler,
    entity_selector_without_own_entities,
)

from .const import CONF_AREA, CONF_CHILDREN, CONF_FLOOR, CONF_NETWORK_TYPE, DOMAIN

AREA_NETWORK_TYPES = [
    "independent",
    "area",
    "floor",
]

_LOGGER = logging.getLogger(__name__)


async def options_schema(
    handler: SchemaCommonFlowHandler | None,
) -> vol.Schema:
    """Generate options schema."""
    entity_selector: selector.Selector[Any]

    if handler is not None and isinstance(
        handler.parent_handler, SchemaOptionsFlowHandler
    ):
        optionsFlowHandler: SchemaOptionsFlowHandler = handler.parent_handler
        entity_selector = entity_selector_without_own_entities(
            optionsFlowHandler,
            selector.EntitySelectorConfig(
                domain="sensor", multiple=True, integration=DOMAIN
            ),
        )
    else:
        entity_selector = selector.selector(
            {"entity": {"domain": "sensor", "multiple": True, "integration": DOMAIN}}
        )

    return vol.Schema({vol.Optional(CONF_CHILDREN): entity_selector})


INDEPENDENT_CONFIG_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): selector.TextSelector(),
        vol.Optional(
            CONF_ICON, default="mdi:pine-network-variant-outline"
        ): selector.IconSelector(),
    }
)

AREA_CONFIG_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_AREA): selector.AreaSelector(),
    }
)

FLOOR_CONFIG_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_FLOOR): selector.FloorSelector(),
    }
)


async def _choose_options_step(options: dict[str, Any]) -> str:
    """Return next step_id for options flow according to network_type."""
    return cast(str, options[CONF_NETWORK_TYPE])


def _validate_user_input(
    network_type: str,
) -> Callable[
    [SchemaCommonFlowHandler, dict[str, Any]], Coroutine[Any, Any, dict[str, Any]]
]:
    """Set network type."""

    async def _set_network_type(
        handler: SchemaCommonFlowHandler, user_input: dict[str, Any]
    ) -> dict[str, Any]:
        """Set network type if missing."""
        if CONF_NETWORK_TYPE not in user_input:
            user_input[CONF_NETWORK_TYPE] = network_type
        return user_input

    return _set_network_type


CONFIG_FLOW = {
    "user": SchemaFlowMenuStep(AREA_NETWORK_TYPES),
    "area": SchemaFlowFormStep(
        AREA_CONFIG_SCHEMA,
        validate_user_input=_validate_user_input("area"),
        next_step="options",
    ),
    "floor": SchemaFlowFormStep(
        FLOOR_CONFIG_SCHEMA,
        validate_user_input=_validate_user_input("floor"),
        next_step="options",
    ),
    "independent": SchemaFlowFormStep(
        INDEPENDENT_CONFIG_SCHEMA,
        validate_user_input=_validate_user_input("independent"),
        next_step="options",
    ),
    "options": SchemaFlowFormStep(options_schema),
}


OPTIONS_FLOW = {
    "init": SchemaFlowFormStep(options_schema),
}


class AreaNetworkConfigFlowHandler(SchemaConfigFlowHandler, domain=DOMAIN):
    """Handle a config or options flow for area network."""

    config_flow = CONFIG_FLOW
    options_flow = OPTIONS_FLOW

    @callback
    def async_config_entry_title(self, options: Mapping[str, Any]) -> str:
        """Return config entry title.

        The options parameter contains config entry options, which is the union of user
        input from the config flow steps.
        """
        return cast(str, options[CONF_NAME]) if CONF_NAME in options else ""

    @callback
    def async_config_flow_finished(self, options: Mapping[str, Any]) -> None:
        """TODO Complete setup."""
        _LOGGER.info("Config Flow Finished!")

    @callback
    @staticmethod
    def async_options_flow_finished(
        hass: HomeAssistant, options: Mapping[str, Any]
    ) -> None:
        """TODO Complete setup."""
        _LOGGER.info("Options Flow Finished!")
