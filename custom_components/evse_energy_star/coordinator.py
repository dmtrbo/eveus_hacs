import logging
import aiohttp
import async_timeout
from datetime import timedelta
from homeassistant.util import slugify
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

class EVSECoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, host: str, entry: ConfigEntry):
        update_rate = entry.options.get("update_rate", 10)
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN} Coordinator",
            update_interval=timedelta(seconds=update_rate),
        )
        self.hass = hass
        self.host = host
        self.entry = entry

        # Store device name from config
        self.device_name = entry.options.get(
            "device_name",
            entry.data.get("device_name", "Eveus Pro")
        )

        # Store slug immediately to avoid code duplication in entities
        self.device_name_slug = slugify(self.device_name)

    async def _async_update_data(self):
        try:
            async with async_timeout.timeout(5):
                async with aiohttp.ClientSession() as session:

                    # Step 1: POST /init
                    init_url = f"http://{self.host}/init"
                    _LOGGER.debug("EVSECoordinator → POST /init: %s", init_url)

                    init_data = {}
                    try:
                        async with session.post(init_url) as resp_init:
                            if resp_init.status == 200 and "application/json" in resp_init.headers.get("Content-Type", ""):
                                init_data = await resp_init.json()
                                _LOGGER.debug("EVSECoordinator → Data from /init:")
                                for key, value in init_data.items():
                                    _LOGGER.debug("  %s → %s (%s)", key, value, type(value).__name__)
                            else:
                                _LOGGER.warning("EVSECoordinator → /init → not JSON (%s)", resp_init.headers.get("Content-Type"))
                    except Exception as err:
                        _LOGGER.error("EVSECoordinator → /init request error: %s", repr(err))

                    # Step 2: POST /main
                    main_url = f"http://{self.host}/main"
                    _LOGGER.debug("EVSECoordinator → POST /main: %s", main_url)

                    main_data = {}
                    try:
                        async with session.post(main_url, json={"getState": True}) as resp_main:
                            if resp_main.status == 200 and "application/json" in resp_main.headers.get("Content-Type", ""):
                                main_data = await resp_main.json()
                                _LOGGER.debug("EVSECoordinator → Data from /main:")
                                for key, value in main_data.items():
                                    _LOGGER.debug("  %s → %s (%s)", key, value, type(value).__name__)
                            else:
                                _LOGGER.warning("EVSECoordinator → /main → not JSON (%s)", resp_main.headers.get("Content-Type"))
                    except Exception as err:
                        _LOGGER.error("EVSECoordinator → /main request error: %s", repr(err))

                    # Merge data from both endpoints
                    combined = {**init_data, **main_data}
                    return combined

        except Exception as err:
            _LOGGER.error("EVSECoordinator → general error: %s", repr(err))
            return {}
