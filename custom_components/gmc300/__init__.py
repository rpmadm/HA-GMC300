#async def async_setup(hass, config):
#    hass.states.async_set("gmc300.world", "GMC-300")

    # Return boolean to indicate that initialization was successful.
#    return True
import logging
from .const import *
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import *
import homeassistant.helpers.event as ev
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.entity import DeviceInfo
from datetime import timedelta
from .gmc_connection import GMCConnection
#from .skykettle import SkyKettle

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [
    Platform.SENSOR,
    Platform.NUMBER,
]

