from __future__ import annotations

import struct
#import serial
from . import const
from . import gmc300

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import TEMP_CELSIUS
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None
) -> None:
    """Set up the sensor platform."""
    add_entities([GMCSensor()])


class GMCSensor(SensorEntity):
    _attr_has_entity_name = True
    _attr_icon = "mdi:radioactive"
    _attr_native_unit_of_measurement = None
    _attr_device_class = None
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_value = 245

    def __init__(self):
        gmc300.open_device()
    #    self._is_on = False
    #    self._attr_device_info = ...  # For automatic device registration
    #    self._attr_unique_id = ...

    @property
    def name(self):
        """Name of the entity."""
        return "GMC300"
    

    def update(self):
        self._attr_native_value = gmc300.get_cpm()

    #
    