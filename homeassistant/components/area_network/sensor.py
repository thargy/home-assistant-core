"""Sensor platform for area_network integration."""
# pylint: disable=fixme

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    ATTR_AREA_ID,
    ATTR_FLOOR_ID,
    CONF_ICON,
    CONF_NAME,
    CONF_UNIQUE_ID,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import (
    area_registry as ar,
    entity_registry as er,
    floor_registry as fr,
)
from homeassistant.helpers.area_registry import AreaEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.floor_registry import FloorEntry
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .const import ATTR_CHILD_IDS, CONF_AREA, CONF_CHILDREN, CONF_FLOOR
from .entity import AreaNetworkEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the Switch Group platform."""
    async_add_entities(
        [
            AreaNetworkSensorEntity(
                hass,
                config.get(CONF_UNIQUE_ID),
                config[CONF_NAME],
                config.get(CONF_ICON),
                config.get(CONF_CHILDREN),
                config.get(CONF_AREA),
                config.get(CONF_FLOOR),
            )
        ]
    )


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Initialize area_network config entry."""

    children = config_entry.options.get(CONF_CHILDREN)
    if children:
        registry = er.async_get(hass)
        children = er.async_validate_entity_ids(registry, children)

    async_add_entities(
        [
            AreaNetworkSensorEntity(
                hass,
                config_entry.entry_id,
                config_entry.title,
                config_entry.options.get(CONF_ICON),
                children,
                config_entry.options.get(CONF_AREA),
                config_entry.options.get(CONF_FLOOR),
            )
        ]
    )


class AreaNetworkSensorEntity(AreaNetworkEntity, SensorEntity):
    """area_network Sensor."""

    def __init__(
        self,
        hass: HomeAssistant,
        unique_id: str | None,
        name: str,
        icon: str | None,
        child_ids: list[str] | None,
        area_id: str | None,
        floor_id: str | None,
    ) -> None:
        """Initialize area_network Sensor."""
        super().__init__()
        self.hass = hass
        self._attr_unique_id = unique_id
        self._attr_name = name
        self._attr_icon = icon
        self._child_ids = child_ids
        self._area_id = area_id
        self._floor_id = floor_id
        self._extra_state_attribute: dict[str, Any] = {}
        if area_id:
            area = self._get_area()
            if area is not None:
                # Set name and icon
                self._attr_name = area.name
                self._attr_icon = area.icon
        elif floor_id:
            floor = self._get_floor()
            if floor is not None:
                # Set name and icon
                self._attr_name = floor.name
                self._attr_icon = floor.icon

    @property
    def area_id(self) -> str | None:
        """Return the area ID."""
        return self._area_id

    @property
    def floor_id(self) -> str | None:
        """Return the floor ID."""
        return self._floor_id

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the attributes of the sensor."""
        return self._extra_state_attribute

    def _get_area(self) -> AreaEntry | None:
        """Get the current area entry."""
        if not self._area_id:
            return None

        area_registry = ar.async_get(self.hass)
        area = area_registry.async_get_area(self._area_id)
        if area is None:
            _LOGGER.warning(
                "Could not find '%s' area, treating '%s' area network as independent",
                self._area_id,
                self._attr_name,
            )
        return area

    @callback
    def async_update_area(self) -> None:
        """Update the network based on an area change."""
        area = self._get_area()
        if area is None:
            if ATTR_AREA_ID in self._extra_state_attribute:
                self._extra_state_attribute.pop(ATTR_AREA_ID)
            return

        # Update name and icon
        self._attr_name = area.name
        self._attr_icon = area.icon

        # Update area_id attribute
        self._extra_state_attribute.update({ATTR_AREA_ID: area.id})

    def _get_floor(self) -> FloorEntry | None:
        """Get the current floor entry."""
        if not self._floor_id:
            return None

        floor_registry = fr.async_get(self.hass)
        floor = floor_registry.async_get_floor(self._floor_id)
        if floor is None:
            _LOGGER.warning(
                "Could not find '%s' floor, treating '%s' floor network as independent",
                self._floor_id,
                self._attr_name,
            )
        return floor

    @callback
    def async_update_floor(self) -> None:
        """Update the network based on a floor change."""
        floor = self._get_floor()
        if floor is None:
            if ATTR_FLOOR_ID in self._extra_state_attribute:
                self._extra_state_attribute.pop(ATTR_FLOOR_ID)
            return

        # Update name and icon
        self._attr_name = floor.name
        self._attr_icon = floor.icon

        # Update floor_id attribute
        self._extra_state_attribute.update({ATTR_FLOOR_ID: floor.floor_id})

    @callback
    def async_update_network_state(self) -> None:
        """Update the network based on a child entity change."""

        # Update child_ids attribute
        self._extra_state_attribute.update({ATTR_CHILD_IDS: self._child_ids})
