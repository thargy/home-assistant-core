"""Helpers for listening to events."""
# ruff: noqa: BLE001

from __future__ import annotations

from collections.abc import Callable, Iterable
import logging
from typing import Any

from homeassistant.core import (
    CALLBACK_TYPE,
    Event,
    # Explicit reexport of 'EventStateChangedData' for backwards compatibility
    EventStateChangedData as EventStateChangedData,  # noqa: PLC0414
    HassJob,
    HassJobType,
    HomeAssistant,
    callback,
)
from homeassistant.helpers.area_registry import (
    EVENT_AREA_REGISTRY_UPDATED,
    EventAreaRegistryUpdatedData,
)
from homeassistant.helpers.event import (
    _async_track_event,
    _KeyedEventData,
    _KeyedEventTracker,
)
from homeassistant.helpers.floor_registry import (
    EVENT_FLOOR_REGISTRY_UPDATED,
    EventFloorRegistryUpdatedData,
)
from homeassistant.util.hass_dict import HassKey

_LOGGER = logging.getLogger(__name__)

_TRACK_AREA_REGISTRY_UPDATED_DATA: HassKey[
    _KeyedEventData[EventAreaRegistryUpdatedData]
] = HassKey("track_area_registry_updated_data")

_TRACK_FLOOR_REGISTRY_UPDATED_DATA: HassKey[
    _KeyedEventData[EventFloorRegistryUpdatedData]
] = HassKey("track_floor_registry_updated_data")


@callback
def _async_area_registry_updated_filter(
    hass: HomeAssistant,
    callbacks: dict[str, list[HassJob[[Event[EventAreaRegistryUpdatedData]], Any]]],
    event_data: EventAreaRegistryUpdatedData,
) -> bool:
    """Filter area registry updates by area_id."""
    return event_data["area_id"] in callbacks


@callback
def _async_dispatch_area_id_event(
    hass: HomeAssistant,
    callbacks: dict[str, list[HassJob[[Event[EventAreaRegistryUpdatedData]], Any]]],
    event: Event[EventAreaRegistryUpdatedData],
) -> None:
    """Dispatch to listeners."""
    if not (callbacks_list := callbacks.get(event.data["area_id"])):
        return
    for job in callbacks_list.copy():
        try:
            hass.async_run_hass_job(job, event)
        except Exception:
            _LOGGER.exception(
                "Error while dispatching event for %s to %s",
                event.data["area_id"],
                job,
            )


_KEYED_TRACK_AREA_REGISTRY_UPDATED = _KeyedEventTracker(
    key=_TRACK_AREA_REGISTRY_UPDATED_DATA,
    event_type=EVENT_AREA_REGISTRY_UPDATED,
    dispatcher_callable=_async_dispatch_area_id_event,
    filter_callable=_async_area_registry_updated_filter,
)


@callback
def async_track_area_registry_updated_event(
    hass: HomeAssistant,
    area_ids: str | Iterable[str],
    action: Callable[[Event[EventAreaRegistryUpdatedData]], Any],
    job_type: HassJobType | None = None,
) -> CALLBACK_TYPE:
    """Track specific area registry updated events indexed by area_id.

    Similar to async_track_entity_registry_updated_event.
    """
    return _async_track_event(
        _KEYED_TRACK_AREA_REGISTRY_UPDATED, hass, area_ids, action, job_type
    )


@callback
def _async_floor_registry_updated_filter(
    hass: HomeAssistant,
    callbacks: dict[str, list[HassJob[[Event[EventFloorRegistryUpdatedData]], Any]]],
    event_data: EventFloorRegistryUpdatedData,
) -> bool:
    """Filter floor registry updates by floor_id."""
    return event_data["floor_id"] in callbacks


@callback
def _async_dispatch_floor_id_event(
    hass: HomeAssistant,
    callbacks: dict[str, list[HassJob[[Event[EventFloorRegistryUpdatedData]], Any]]],
    event: Event[EventFloorRegistryUpdatedData],
) -> None:
    """Dispatch to listeners."""
    if not (callbacks_list := callbacks.get(event.data["floor_id"])):
        return
    for job in callbacks_list.copy():
        try:
            hass.async_run_hass_job(job, event)
        except Exception:
            _LOGGER.exception(
                "Error while dispatching event for %s to %s",
                event.data["floor_id"],
                job,
            )


_KEYED_TRACK_FLOOR_REGISTRY_UPDATED = _KeyedEventTracker(
    key=_TRACK_FLOOR_REGISTRY_UPDATED_DATA,
    event_type=EVENT_FLOOR_REGISTRY_UPDATED,
    dispatcher_callable=_async_dispatch_floor_id_event,
    filter_callable=_async_floor_registry_updated_filter,
)


@callback
def async_track_floor_registry_updated_event(
    hass: HomeAssistant,
    floor_ids: str | Iterable[str],
    action: Callable[[Event[EventFloorRegistryUpdatedData]], Any],
    job_type: HassJobType | None = None,
) -> CALLBACK_TYPE:
    """Track specific floor registry updated events indexed by floor_id.

    Similar to async_track_entity_registry_updated_event.
    """
    return _async_track_event(
        _KEYED_TRACK_FLOOR_REGISTRY_UPDATED, hass, floor_ids, action, job_type
    )
