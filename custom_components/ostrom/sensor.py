from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.core import HomeAssistant

from .const import DOMAIN

async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([OstromPriceSensor(coordinator)])

class OstromPriceSensor(CoordinatorEntity, SensorEntity):
    _attr_name = 'Ostrom Spot Price'
    _attr_icon = 'mdi:lightning-bolt'
    _attr_native_unit_of_measurement = '€/kWh'
    _attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self):
        data = self.coordinator.data or {}
        for key in ('price', 'current_price', 'currentPrice', 'spot_price'):
            if key in data:
                return data[key]
        if isinstance(data, dict):
            for v in data.values():
                if isinstance(v, (int, float)):
                    return v
        return None

    @property
    def extra_state_attributes(self):
        return {'raw': self.coordinator.data or {}}
