"""Constants for the NRJHub Yellow integration."""

DOMAIN = "homeassistant_yellow"

RADIO_DEVICE = "/dev/ttyAMA1"
ZHA_HW_DISCOVERY_DATA = {
    "name": "Yellow",
    "port": {
        "path": RADIO_DEVICE,
        "baudrate": 115200,
        "flow_control": "hardware",
    },
    "radio_type": "efr32",
}

FIRMWARE = "firmware"
ZHA_DOMAIN = "zha"
