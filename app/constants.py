from __future__ import annotations

from datetime import date
from typing import Dict, List, Tuple

ZODIAC_SIGNS: List[str] = [
    "Aries",
    "Taurus",
    "Gemini",
    "Cancer",
    "Leo",
    "Virgo",
    "Libra",
    "Scorpio",
    "Sagittarius",
    "Capricorn",
    "Aquarius",
    "Pisces",
]

# Western tropical sign date windows (month/day).
SIGN_WINDOWS: List[Tuple[str, Tuple[int, int], Tuple[int, int]]] = [
    ("Capricorn", (12, 22), (1, 19)),
    ("Aquarius", (1, 20), (2, 18)),
    ("Pisces", (2, 19), (3, 20)),
    ("Aries", (3, 21), (4, 19)),
    ("Taurus", (4, 20), (5, 20)),
    ("Gemini", (5, 21), (6, 20)),
    ("Cancer", (6, 21), (7, 22)),
    ("Leo", (7, 23), (8, 22)),
    ("Virgo", (8, 23), (9, 22)),
    ("Libra", (9, 23), (10, 22)),
    ("Scorpio", (10, 23), (11, 21)),
    ("Sagittarius", (11, 22), (12, 21)),
]

PLANETS: List[str] = [
    "Sun",
    "Moon",
    "Mercury",
    "Venus",
    "Mars",
    "Jupiter",
    "Saturn",
    "Uranus",
    "Neptune",
    "Pluto",
    "North Node",
    "Chiron",
]

HOUSE_TOPICS: Dict[int, str] = {
    1: "Identity, body, self-definition",
    2: "Money, values, resources",
    3: "Communication, learning, siblings",
    4: "Home, roots, family, emotional foundations",
    5: "Creativity, romance, joy, self-expression",
    6: "Workflows, health, daily systems",
    7: "Partnerships, contracts, commitments",
    8: "Shared resources, intimacy, transformation",
    9: "Beliefs, higher learning, travel",
    10: "Career, reputation, public direction",
    11: "Community, friendship, long-term goals",
    12: "Rest, closure, subconscious patterns",
}

YEARLY_TIMELINE_SEGMENTS: List[str] = [
    "Beginning of the year",
    "Middle of the year",
    "Closing months",
]

BETWEEN_US_DIMENSIONS: List[Tuple[str, str]] = [
    ("emotional", "Emotional Compatibility"),
    ("communication", "Communication Style"),
    ("sexual", "Sexual Chemistry"),
    ("stability", "Long-Term Stability"),
    ("growth", "Growth Potential"),
    ("power", "Power Dynamics"),
]

REACTION_CHOICES: List[str] = ["accurate", "thinking", "missed"]

MOON_PHASES: List[str] = [
    "new_moon",
    "waxing_crescent",
    "first_quarter",
    "waxing_gibbous",
    "full_moon",
    "waning_gibbous",
    "last_quarter",
    "waning_crescent",
]

DEFAULT_DAILY_READING_HOUR = 8
DEFAULT_LANGUAGE = "en"
DEFAULT_THEME = "dark"
DEFAULT_SUBSCRIPTION_TIER = "free"
DEFAULT_COUNTRY_CODE = "US"

LAUNCH_TRUST_MESSAGE = "We just launched. You're early. But your chart is still accurate."

# Rough moon sign change warning: every ~2.3 days, so these boundaries are approximate.
MOON_SIGN_CHANGE_WARN_DAYS: List[int] = [0, 2, 5, 7, 10, 12, 15, 17, 20, 22, 25, 27]

APP_DATE = date.today()
