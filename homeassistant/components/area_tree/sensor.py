"""Sensor platform for area_tree integration."""
# pylint: disable=fixme

from __future__ import annotations

from typing import Any

from propcache import cached_property

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import area_registry as ar, floor_registry as fr
from homeassistant.helpers.area_registry import AreaEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.floor_registry import FloorEntry

from .const import (
    CONF_AREA_ID,
    CONF_CHILDREN,
    CONF_FLOOR_ID,
    CONF_ICON,
    CONF_NAME,
    CONF_TREE_TYPE,
)
from .event import (
    async_track_area_registry_updated_event,
    async_track_floor_registry_updated_event,
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
        self._tree_type = config_entry.options.get(CONF_TREE_TYPE)
        self._children = config_entry.options.get(CONF_CHILDREN)

        # Initialise attached
        self._attached: AreaEntry | FloorEntry | None = None

        # Initialize custom attributes
        self._custom_attributes: dict[str, Any] = {}

        # if self.parent is not None:
        #    entity_registry = er.async_get(hass)
        #    entity_id = entity_registry.entities.get_entry(self.parent)
        #    if entity_id is None:
        #        self.parent is None

        if CONF_NAME in config_entry.options:
            self._attr_name = config_entry.options.get(CONF_NAME)
        if CONF_ICON in config_entry.options:
            self._attr_icon = config_entry.options.get(CONF_ICON)

        self._area_id = None
        self._floor_id = None

        if self._tree_type == "area":
            self._init_area(hass, config_entry)
        elif self._tree_type == "floor":
            self._init_floor(hass, config_entry)
        else:
            self._tree_type = "integration"

    def _init_area(self, hass: HomeAssistant, config_entry: ConfigEntry):
        """Initialise area based on configuration."""
        area_id = config_entry.options.get(CONF_AREA_ID)
        if area_id is None:
            self._tree_type = "integration"
            return

        area_registry = ar.async_get(hass)
        area = area_registry.async_get_area(area_id)
        if area is None:
            self._tree_type = "integration"
            return

        self._attached = area
        self._load_area()
        async_track_area_registry_updated_event(
            hass, area.id, self.area_change_listener
        )

    @callback
    def area_change_listener(self, event):
        """Handle area state change events."""
        self._load_area()

    def _load_area(self):
        """Reload an area."""
        if not isinstance(self._attached, AreaEntry):
            raise TypeError("Expected attached area")
        area: AreaEntry = self._attached

        # We are attached to an area
        self._attr_name = area.name
        self._attr_icon = area.icon
        self._clear_cache()

    def _init_floor(self, hass: HomeAssistant, config_entry: ConfigEntry):
        """Initialise floor based on configuration."""
        floor_id = config_entry.options.get(CONF_FLOOR_ID)
        if floor_id is None:
            self._tree_type = "integration"
            return
        floor_reg = fr.async_get(hass)
        floor = floor_reg.async_get_floor(floor_id)
        if floor is None:
            self._tree_type = "integration"
            return

        self._attached = floor
        self._load_floor()
        async_track_floor_registry_updated_event(
            hass, floor.floor_id, self.floor_change_listener
        )

    @callback
    def floor_change_listener(self, event):
        """Handle area state change events."""
        self._load_floor()

    def _load_floor(self):
        """Reload a floor."""
        if not isinstance(self._attached, FloorEntry):
            raise TypeError("Expected attached floor")
        floor: FloorEntry = self._attached

        # We are attached to a floor
        self._attr_name = floor.name
        self._attr_icon = floor.icon
        self._clear_cache()

    @cached_property
    def area_id(self) -> str | None:
        """Return the area ID."""
        return self._attached.id if isinstance(self._attached, AreaEntry) else None

    @cached_property
    def floor_id(self) -> str | None:
        """Return the floor ID."""
        return (
            self._attached.floor_id if isinstance(self._attached, FloorEntry) else None
        )

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the attributes of the sensor."""
        extra_attributes = {
            **self._custom_attributes,
            "tree_type": self._tree_type,
            "children": self._children,
        }
        area_id = self.area_id
        if area_id is not None:
            extra_attributes = {
                **extra_attributes,
                "area_id": area_id,
            }
        else:
            floor_id = self.area_id
            if floor_id is not None:
                extra_attributes = {
                    **extra_attributes,
                    "floor_id": floor_id,
                }

        return extra_attributes

    def _clear_cache(self):
        """Clear cached properties after update."""
        if "name" in self.__dict__:
            self.__dict__.pop("name")
        if "icon" in self.__dict__:
            self.__dict__.pop("icon")
