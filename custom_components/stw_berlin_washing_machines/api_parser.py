from typing import Optional

import aiohttp
from pydantic import BaseModel


class WashingMachine(BaseModel):
    name: str
    is_occupied: bool
    duration_minutes: Optional[int] = None


headers = {"User-Agent": "Test"}

dorms = {
    'WH Bitscherstraße, Garystraße und Clayalle ("Salvador Allende")': 454,
    "WH Coppistraße (Hans und Hilde Coppi)": 434,
    "WH Dauerwaldweg": 435,
    "WH Eichkamp": 437,
    "WH Franz-Mehring-Platz": 386,
    "WH Gelfertstraße": 438,
    "WH Goerzallee": 242,
    "WH Hardenbergstraße": 441,
    "WH Hubertusallee": 443,
    "WH Nollendorfstraße": 446,
    "WH Oberfeldstraße (Victor Jara)": 381,
    "WH Potsdamer Straße": 453,
    "WH Sewanstraße": 383,
    "WH Siegmunds Hof": 455,
}


async def get_washing_machine_urls(
    session: aiohttp.ClientSession, dorm_id: int
) -> list[str]:
    url = f"https://www.stw.berlin/staticfiles/snippets/infomax/checkCBFieldFHDS.php?id={dorm_id}"

    async with session.get(url, headers=headers) as response:
        response.raise_for_status()
        data = await response.text()

    # for some reason, there can be multiple urls for some larger dorms
    return data.split(",")


async def fetch_washing_machine_data(
    session: aiohttp.ClientSession, url
) -> dict[str, WashingMachine]:
    async with session.get(url, headers=headers) as response:
        response.raise_for_status()
        data = await response.json()

    # Build list of WashingMachine instances
    machines = {}
    for name_raw, status_raw in zip(data["HEAD"], data["DATA"], strict=True):
        name = name_raw.strip()
        status_str = status_raw.strip()

        if status_str:
            parts = status_str.split()
            is_occupied = parts[0].lower() == "belegt"
            minutes = None
            if len(parts) > 1 and ":" in parts[1]:
                try:
                    h, m = map(int, parts[1].split(":"))
                    minutes = h * 60 + m
                except ValueError:
                    pass
            machines[name] = WashingMachine(
                name=name, is_occupied=is_occupied, duration_minutes=minutes
            )
        else:
            machines[name] = WashingMachine(name=name, is_occupied=False)

    return machines
