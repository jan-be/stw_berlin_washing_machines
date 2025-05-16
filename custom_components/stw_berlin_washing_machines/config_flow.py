"""Config flow for the STW Berlin Washing Machines integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import selector

from .api_parser import dorms, get_washing_machine_urls
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required("dorm"): selector({"select": {"options": list(dorms.keys())}}),
    }
)


class ConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for STW Berlin Washing Machines."""

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            session = async_get_clientsession(self.hass)

            urls = await get_washing_machine_urls(session, dorms[user_input["dorm"]])

            return self.async_create_entry(
                title=user_input["dorm"],
                data={"dorm": user_input["dorm"], "urls": urls},
            )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )
