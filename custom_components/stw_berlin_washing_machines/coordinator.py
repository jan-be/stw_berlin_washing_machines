from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api_parser import WashingMachine, fetch_washing_machine_data
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class WashingMachineCoordinator(DataUpdateCoordinator[list[WashingMachine]]):
    def __init__(self, hass: HomeAssistant, dorm: str, urls: list[str]) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=1),
        )
        self.dorm = dorm
        self.urls = urls

    async def _async_update_data(self) -> dict[str, WashingMachine]:
        """Fetch data from the washing machine API."""
        try:
            session = async_get_clientsession(self.hass)

            machines = {}
            for url in self.urls:
                machines.update(await fetch_washing_machine_data(session, url))

            return machines
        except Exception as err:
            raise UpdateFailed(f"Failed to fetch washing machine data: {err}") from err
