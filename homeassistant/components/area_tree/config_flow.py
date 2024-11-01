"""Config flow for area_tree integration."""

from __future__ import annotations

from collections.abc import Callable, Coroutine, Mapping
from typing import Any, cast

import voluptuous as vol

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

from . import _LOGGER
from .const import (
    CONF_AREA_ID,
    CONF_CHILDREN,
    CONF_FLOOR_ID,
    CONF_ICON,
    CONF_NAME,
    CONF_TREE_TYPE,
    DOMAIN,
)

AREA_TREE_TYPES = [
    "independent",
    "area",
    "floor",
]


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
            CONF_ICON, default="mdi:pine-tree-variant-outline"
        ): selector.IconSelector(),
    }
)

AREA_CONFIG_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_AREA_ID): selector.AreaSelector(),
    }
)

FLOOR_CONFIG_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_FLOOR_ID): selector.FloorSelector(),
    }
)


# async def _suggested_values(handler: SchemaCommonFlowHandler) -> dict[str, Any]:
#     """Suggest values based on area/floor."""
#     tree_type = handler.options.get(CONF_TREE_TYPE)
#     suggestions = {}
#     if tree_type == "area":
#         area_id = handler.options.get(CONF_AREA_ID)
#         if area_id is not None:
#             area_reg = ar.async_get(handler.parent_handler.hass)
#             area = area_reg.async_get_area(area_id)
#             if area is not None:
#                 if not handler.options.get(CONF_NAME):
#                     suggestions = {CONF_NAME: area.name, **suggestions}
#                 if not handler.options.get(CONF_ICON):
#                     suggestions = {CONF_ICON: area.icon, **suggestions}
#
#     elif tree_type == "floor":
#         floor_id = handler.options.get(CONF_FLOOR_ID)
#         if floor_id is not None:
#             floor_reg = fr.async_get(handler.parent_handler.hass)
#             floor = floor_reg.async_get_floor(floor_id)
#             if floor is not None:
#                 if not handler.options.get(CONF_NAME):
#                     suggestions = {CONF_NAME: floor.name, **suggestions}
#                 if not handler.options.get(CONF_ICON):
#                     suggestions = {CONF_ICON: floor.icon, **suggestions}
#
#     return suggestions


async def _choose_options_step(options: dict[str, Any]) -> str:
    """Return next step_id for options flow according to tree_type."""
    return cast(str, options[CONF_TREE_TYPE])


def _validate_user_input(
    tree_type: str,
) -> Callable[
    [SchemaCommonFlowHandler, dict[str, Any]], Coroutine[Any, Any, dict[str, Any]]
]:
    """Set group type."""

    async def _set_tree_type(
        handler: SchemaCommonFlowHandler, user_input: dict[str, Any]
    ) -> dict[str, Any]:
        """Set tree type if missing."""
        if CONF_TREE_TYPE not in user_input:
            user_input[CONF_TREE_TYPE] = tree_type
        return user_input

    return _set_tree_type


CONFIG_FLOW = {
    "user": SchemaFlowMenuStep(AREA_TREE_TYPES),
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


class AreaTreeConfigFlowHandler(SchemaConfigFlowHandler, domain=DOMAIN):
    """Handle a config or options flow for area tree."""

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
