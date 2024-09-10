"""Assist satellite Websocket API."""

from typing import Any

import voluptuous as vol

from homeassistant.components import websocket_api
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.entity_component import EntityComponent

from .const import DOMAIN
from .entity import AssistSatelliteEntity


@callback
def async_register_websocket_api(hass: HomeAssistant) -> None:
    """Register the websocket API."""
    websocket_api.async_register_command(hass, websocket_intercept_wake_word)


@callback
@websocket_api.websocket_command(
    {
        vol.Required("type"): "assist_satellite/intercept_wake_word",
        vol.Required("entity_id"): cv.entity_domain(DOMAIN),
    }
)
@websocket_api.require_admin
@websocket_api.async_response
async def websocket_intercept_wake_word(
    hass: HomeAssistant,
    connection: websocket_api.connection.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Intercept the next wake word from a satellite."""
    component: EntityComponent[AssistSatelliteEntity] = hass.data[DOMAIN]
    satellite = component.get_entity(msg["entity_id"])
    if satellite is None:
        connection.send_error(
            msg["id"], websocket_api.ERR_NOT_FOUND, "Entity not found"
        )
        return

    async def intercept_wake_word() -> None:
        """Push an intercepted wake word to websocket."""
        try:
            wake_word_phrase = await satellite.async_intercept_wake_word()
            connection.send_message(
                websocket_api.event_message(
                    msg["id"],
                    {"wake_word_phrase": wake_word_phrase},
                )
            )
        except HomeAssistantError as err:
            connection.send_error(msg["id"], "home_assistant_error", str(err))

    task = hass.async_create_background_task(
        intercept_wake_word(), "intercept_wake_word"
    )
    connection.subscriptions[msg["id"]] = task.cancel
    connection.send_message(websocket_api.result_message(msg["id"]))
