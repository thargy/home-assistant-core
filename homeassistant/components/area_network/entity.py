"""Provide entity classes for area_network entities."""

from __future__ import annotations

from abc import abstractmethod
import logging

from homeassistant.core import Event, EventStateChangedData, HomeAssistant, callback
from homeassistant.helpers import start
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.event import async_track_state_change_event

from .const import ATTR_CHILD_IDS, DOMAIN
from .event import (
    EventAreaRegistryUpdatedData,
    EventFloorRegistryUpdatedData,
    async_track_area_registry_updated_event,
    async_track_floor_registry_updated_event,
)

ENTITY_ID_FORMAT = DOMAIN + ".{}"

_PACKAGE_LOGGER = logging.getLogger(__package__)

_LOGGER = logging.getLogger(__name__)


class AreaNetworkEntity(Entity):
    """Representation of a network of areas."""

    _unrecorded_attributes = frozenset({ATTR_CHILD_IDS})

    _attr_should_poll = False
    _child_ids: list[str] | None
    _area_id: str | None
    _floor_id: str | None

    async def async_added_to_hass(self) -> None:
        """Register listeners."""
        if self._area_id:
            # Register area listener
            @callback
            def async_area_changed_listener(
                event: Event[EventAreaRegistryUpdatedData],
            ) -> None:
                """Handle area updates."""
                self.async_set_context(event.context)
                self.async_update_area()
                self.async_write_ha_state()

            self.async_on_remove(
                async_track_area_registry_updated_event(
                    self.hass, [self._area_id], async_area_changed_listener
                )
            )
        elif self._floor_id:
            # Register floor listener
            @callback
            def async_floor_changed_listener(
                event: Event[EventFloorRegistryUpdatedData],
            ) -> None:
                """Handle floor updates."""
                self.async_set_context(event.context)
                self.async_update_floor()
                self.async_write_ha_state()

            self.async_on_remove(
                async_track_floor_registry_updated_event(
                    self.hass, [self._floor_id], async_floor_changed_listener
                )
            )

        if self._child_ids:
            # Register listeners for children
            @callback
            def async_state_changed_listener(
                event: Event[EventStateChangedData],
            ) -> None:
                """Handle child updates."""
                self.async_set_context(event.context)
                self.async_update_network_state()
                self.async_write_ha_state()

            self.async_on_remove(
                async_track_state_change_event(
                    self.hass, self._child_ids, async_state_changed_listener
                )
            )

        self.async_on_remove(start.async_at_start(self.hass, self._update_at_start))

    @callback
    def _update_at_start(self, _: HomeAssistant) -> None:
        """Update the state at start."""
        updated = False
        if self._area_id:
            self.async_update_area()
            updated = True
        if self._floor_id:
            self.async_update_floor()
            updated = True
        if self._child_ids:
            self.async_update_network_state()
            updated = True
        if updated:
            self.async_write_ha_state()

    @abstractmethod
    @callback
    def async_update_area(self) -> None:
        """Abstract method to update the network based on an area."""

    @abstractmethod
    @callback
    def async_update_floor(self) -> None:
        """Abstract method to update the network based on a floor."""

    @abstractmethod
    @callback
    def async_update_network_state(self) -> None:
        """Abstract method to update the network."""
