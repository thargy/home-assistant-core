"""Constants for the area_network integration."""

from __future__ import annotations

from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.util.hass_dict import HassKey

DOMAIN = "area_network"

CONF_NETWORK_TYPE = "type"
CONF_CHILDREN = "children"
CONF_AREA = "area"
CONF_FLOOR = "floor"

# For now we shall reuse ATTR_ENTITY_ID to mimic the same behaviour as groups
ATTR_CHILD_IDS = ATTR_ENTITY_ID

AREA_NETWORK_ORDER: HassKey[int] = HassKey("area_network_order")
