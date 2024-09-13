"""The NRJHub SkyConnect integration."""

from __future__ import annotations

from homeassistant.components import usb
from homeassistant.components.homeassistant_hardware.silabs_multiprotocol_addon import (
    check_multi_pan_addon,
    get_zigbee_socket,
    multi_pan_addon_using_device,
)
from homeassistant.config_entries import SOURCE_HARDWARE, ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import ConfigEntryNotReady, HomeAssistantError
from homeassistant.helpers import discovery_flow

from .const import DOMAIN
from .util import get_hardware_variant, get_usb_service_info


async def _async_usb_scan_done(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Finish NRJHub SkyConnect config entry setup."""
    matcher = usb.USBCallbackMatcher(
        domain=DOMAIN,
        vid=entry.data["vid"].upper(),
        pid=entry.data["pid"].upper(),
        serial_number=entry.data["serial_number"].lower(),
        manufacturer=entry.data["manufacturer"].lower(),
        description=entry.data["description"].lower(),
    )

    if not usb.async_is_plugged_in(hass, matcher):
        # The USB dongle is not plugged in, remove the config entry
        hass.async_create_task(
            hass.config_entries.async_remove(entry.entry_id), eager_start=True
        )
        return

    usb_dev = entry.data["device"]
    # The call to get_serial_by_id can be removed in HA Core 2024.1
    dev_path = await hass.async_add_executor_job(usb.get_serial_by_id, usb_dev)

    if not await multi_pan_addon_using_device(hass, dev_path):
        usb_info = get_usb_service_info(entry)
        await hass.config_entries.flow.async_init(
            "zha",
            context={"source": "usb"},
            data=usb_info,
        )
        return

    hw_variant = get_hardware_variant(entry)
    hw_discovery_data = {
        "name": f"{hw_variant.short_name} Multiprotocol",
        "port": {
            "path": get_zigbee_socket(),
        },
        "radio_type": "ezsp",
    }
    discovery_flow.async_create_flow(
        hass,
        "zha",
        context={"source": SOURCE_HARDWARE},
        data=hw_discovery_data,
    )


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up a NRJHub SkyConnect config entry."""

    try:
        await check_multi_pan_addon(hass)
    except HomeAssistantError as err:
        raise ConfigEntryNotReady from err

    @callback
    def async_usb_scan_done() -> None:
        """Handle usb discovery started."""
        hass.async_create_task(_async_usb_scan_done(hass, entry), eager_start=True)

    unsub_usb = usb.async_register_initial_scan_callback(hass, async_usb_scan_done)
    entry.async_on_unload(unsub_usb)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return True
