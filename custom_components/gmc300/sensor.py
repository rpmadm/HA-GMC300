from __future__ import annotations

import logging

import aiohttp
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.components.sensor import PLATFORM_SCHEMA

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

import serial

CONF_NAME = 'name'
#CONF_START = 'start'
#CONF_DESTINATION = 'destination'

ICON = 'mdi:Radioactive'

CONF_USB = 'usb_port'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_USB): cv.string,
})

_LOGGER = logging.getLogger(__name__)

async def async_setup_platform(
        hass, config, async_add_entities, discovery_info=None):  # pylint: disable=unused-argument
    """Setup sensor platform."""
    name = config['name']
    usb_port: config['usb_port']

    async_add_entities(
        [RadiationSensor(hass, name, usb_port)], True)


class RadiationSensor(Entity):
    """GMC-300 Sensor class"""

    def __init__(self, hass, name, usb_port):
        self.hass = hass
        self._state = None
        self._name = name
        self._usb_port = usb_port
        self.attr = {}
        _LOGGER.debug('Initialized sensor %s with %s, %s', self._name, self._start, self._destination)

    async def async_update(self):
        """Update sensor."""
        _LOGGER.debug('%s - Running update', self._name)

        try:
            rdn_device = serial.Serial( "/dev/ttyUSB-geiger", 57600 )

            _LOGGER.debug('Requesting url %s', url)

        except Exception as error:  # pylint: disable=broad-except
            _LOGGER.debug('%s - Could not update - %s', self._name, error)

#    @classmethod
#    def is_coord(cls, data: str) -> bool:
#        return bool(coords_re.fullmatch(data))

    @property
    def usb_port(self):
        return self._usb_port

#    @property
#    def destination(self):
#        return self.point_to_coords(self._destination)

#    def point_to_coords(self, point: str) -> str:
#        if YandexMapsSensor.is_coord(point):
#            return point

#        state = self.hass.states.get(point)
#        if state:
#            latitude = state.attributes.get('latitude')
#            longitude = state.attributes.get('longitude')
#            if latitude and longitude:
#                return "{},{}".format(longitude, latitude)
#            else:
#                raise AttributeError

    @property
    def name(self):
        """Name."""
        return self._name

    @property
    def state(self):
        """State."""
        return self._state

    @property
    def icon(self):
        """Icon."""
        return ICON

    @property
    def unit_of_measurement(self):
        """unit_of_measurement."""
        return 'мин'

    @property
    def extra_state_attributes(self):
        """Attributes."""
        return self.attr