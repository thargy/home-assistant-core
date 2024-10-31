"""Sensor platform for area_tree integration."""
# pylint: disable=fixme

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import area_registry as ar, floor_registry as fr
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CONF_AREA_ID,
    CONF_FLOOR_ID,
    CONF_ICON,
    CONF_NAME,
    CONF_PARENT,
    CONF_TREE_TYPE,
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Initialize area_tree config entry."""
    async_add_entities([AreaTreeSensorEntity(hass, config_entry)])


class AreaTreeSensorEntity(SensorEntity):
    """area_tree Sensor."""

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        """Initialize area_tree Sensor."""
        super().__init__()
        self._attr_unique_id = config_entry.entry_id
        self.tree_type = config_entry.options.get(CONF_TREE_TYPE)
        self.parent_id = config_entry.options.get(CONF_PARENT)
        # if self.parent is not None:
        #    entity_registry = er.async_get(hass)
        #    entity_id = entity_registry.entities.get_entry(self.parent)
        #    if entity_id is None:
        #        self.parent is None

        if CONF_NAME in config_entry.options:
            self._attr_name = config_entry.options.get(CONF_NAME)
        if CONF_ICON in config_entry.options:
            self._attr_icon = config_entry.options.get(CONF_ICON)

        if self.tree_type == "area":
            area_id = config_entry.options.get(CONF_AREA_ID)
            if area_id is not None:
                area_reg = ar.async_get(hass)
                self.area = area_reg.async_get_area(area_id)
                if self.area:
                    # TODO Specify entity area if not already set
                    if CONF_NAME not in config_entry.options:
                        self._attr_name = self.area.name
                    if CONF_ICON not in config_entry.options:
                        self._attr_icon = self.area.icon
                else:
                    self.tree_type = "integration"

        elif self.tree_type == "floor":
            floor_id = config_entry.options.get(CONF_FLOOR_ID)
            if floor_id is not None:
                floor_reg = fr.async_get(hass)
                self.floor = floor_reg.async_get_floor(floor_id)
                if self.floor:
                    if CONF_NAME not in config_entry.options:
                        self._attr_name = self.floor.name
                    if CONF_ICON not in config_entry.options:
                        self._attr_icon = self.floor.icon
                else:
                    self.tree_type = "integration"

        else:
            self.tree_type = "integration"
