"""Constants for Bravia TV integration."""

from __future__ import annotations

from enum import StrEnum
from typing import Final

ATTR_CID: Final = "cid"
ATTR_MAC: Final = "macAddr"
ATTR_MANUFACTURER: Final = "Sony"
ATTR_MODEL: Final = "model"

CONF_NICKNAME: Final = "nickname"
CONF_USE_PSK: Final = "use_psk"

DOMAIN: Final = "braviatv"
LEGACY_CLIENT_ID: Final = "HomeAssistant"
NICKNAME_PREFIX: Final = "NRJHub"


class SourceType(StrEnum):
    """Source type for Sony TV Integration."""

    APP = "app"
    CHANNEL = "channel"
    INPUT = "input"
