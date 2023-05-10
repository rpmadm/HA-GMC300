from homeassistant.components.sensor import SensorEntity


class GMCSensor(SensorEntity):
    _attr_has_entity_name = True
    _attr_icon = "mdi:radioactive"

    def __init__(self):
        self._is_on = False
        self._attr_device_info = ...  # For automatic device registration
        self._attr_unique_id = ...

    @property
    def name(self):
        """Name of the entity."""
        return "GMC300"
    
    async def _async_update_data(self):
        self.native_value = 356

