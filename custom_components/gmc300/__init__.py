DOMAIN = "gmc300"

async def async_setup(hass, config):
    hass.states.async_set("gmc300.world", "Сенсор")

    # Return boolean to indicate that initialization was successful.
    return True