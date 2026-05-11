"""Small request parser for logistics queries.

It extracts easy-to-explain fields that help the search and analysis agents.
"""

import re
from typing import Dict, Optional

KNOWN_CITIES = ["rabat", "casablanca", "tangier", "marrakech", "fez", "fes"]


def _find_city(text: str, keywords: list[str]) -> Optional[str]:
    for city in keywords:
        if city in text:
            return city.title() if city != "fes" else "Fez"
    return None


def parse_request(user_request: str) -> Dict[str, Optional[str]]:
    """Extract weight, origin, destination, and timing clues from the request."""
    text = user_request.lower()
    weight_match = re.search(r"(\d+(?:\.\d+)?)\s*tons?", text)
    time_match = re.search(r"(\d{1,2}:\d{2})", text)

    origin = None
    destination = None
    if "from" in text and "to" in text:
        after_from = text.split("from", 1)[1]
        origin_part = after_from.split("to", 1)[0]
        destination_part = after_from.split("to", 1)[1]
        origin = _find_city(origin_part, KNOWN_CITIES)
        destination = _find_city(destination_part, KNOWN_CITIES)

    return {
        "weight_tons": weight_match.group(1) if weight_match else None,
        "origin": origin or _find_city(text, KNOWN_CITIES),
        "destination": destination,
        "departure_time": time_match.group(1) if time_match else None,
    }
