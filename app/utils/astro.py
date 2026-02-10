from __future__ import annotations

from datetime import date, time
from typing import Dict, List, Tuple

from app.constants import PLANETS, SIGN_WINDOWS, ZODIAC_SIGNS


def sun_sign_for_date(dob: date) -> str:
    month_day = (dob.month, dob.day)
    for sign, start, end in SIGN_WINDOWS:
        if start <= end:
            if start <= month_day <= end:
                return sign
        else:
            # Wrap window (Capricorn)
            if month_day >= start or month_day <= end:
                return sign
    return "Aries"


def deterministic_sign(index_seed: int) -> str:
    return ZODIAC_SIGNS[index_seed % len(ZODIAC_SIGNS)]


def approximate_moon_sign(dob: date) -> str:
    # Approximation only for missing time/place flow.
    return deterministic_sign((dob.toordinal() * 11) // 2)


def moon_change_warning(dob: date) -> bool:
    # Heuristic to signal possible moon sign boundary days.
    return dob.day in {2, 4, 7, 9, 12, 14, 17, 19, 22, 24, 27, 29}


def deterministic_planetary_positions(
    dob: date,
    birth_time: time | None = None,
    include_houses: bool = False,
) -> List[Dict[str, object]]:
    minute_component = (birth_time.hour * 60 + birth_time.minute) if birth_time else 720
    positions: List[Dict[str, object]] = []

    for idx, planet in enumerate(PLANETS):
        seed = dob.toordinal() + minute_component + (idx * 37)
        sign = deterministic_sign(seed)
        degree = round(((seed % 3000) / 3000) * 30, 2)
        house = (seed % 12) + 1 if include_houses else None
        positions.append(
            {
                "planet": planet,
                "sign": sign,
                "degree": degree,
                "house": house,
            }
        )

    # Force Sun to true tropical sign for consistency.
    positions[0]["sign"] = sun_sign_for_date(dob)
    return positions


def approximate_ascendant(dob: date, birth_time: time | None) -> str:
    minute_component = (birth_time.hour * 60 + birth_time.minute) if birth_time else 720
    return deterministic_sign(dob.toordinal() + minute_component * 3)


def major_aspects(positions: List[Dict[str, object]]) -> List[Dict[str, object]]:
    # Deterministic synthetic aspect list for MVP until full astrology engine wiring.
    aspects: List[Dict[str, object]] = []
    majors = [(0, "conjunction"), (60, "sextile"), (90, "square"), (120, "trine"), (180, "opposition")]
    for i in range(min(len(positions), 6)):
        a = positions[i]
        b = positions[(i + 2) % len(positions)]
        angle, label = majors[(i + int(float(a["degree"]))) % len(majors)]
        aspects.append(
            {
                "a": a["planet"],
                "b": b["planet"],
                "aspect": label,
                "angle": angle,
                "orb": round(abs(float(a["degree"]) - float(b["degree"])) % 8, 2),
            }
        )
    return aspects


def profected_house(age: int) -> int:
    # Age 0 => 1st house
    return (age % 12) + 1


def sign_to_lord(sign: str) -> str:
    rulers: Dict[str, str] = {
        "Aries": "Mars",
        "Taurus": "Venus",
        "Gemini": "Mercury",
        "Cancer": "Moon",
        "Leo": "Sun",
        "Virgo": "Mercury",
        "Libra": "Venus",
        "Scorpio": "Mars",
        "Sagittarius": "Jupiter",
        "Capricorn": "Saturn",
        "Aquarius": "Saturn",
        "Pisces": "Jupiter",
    }
    return rulers.get(sign, "Sun")


def compatibility_label(seed: int) -> str:
    labels = ["strong_flow", "mixed", "growth_edge", "magnetic", "steady", "intense"]
    return labels[seed % len(labels)]


def summarize_sign_elements(signs: List[str]) -> str:
    fire = {"Aries", "Leo", "Sagittarius"}
    earth = {"Taurus", "Virgo", "Capricorn"}
    air = {"Gemini", "Libra", "Aquarius"}
    water = {"Cancer", "Scorpio", "Pisces"}
    counts = {"fire": 0, "earth": 0, "air": 0, "water": 0}
    for sign in signs:
        if sign in fire:
            counts["fire"] += 1
        elif sign in earth:
            counts["earth"] += 1
        elif sign in air:
            counts["air"] += 1
        elif sign in water:
            counts["water"] += 1

    dominant = max(counts, key=counts.get)
    return f"Dominant {dominant} tone ({counts[dominant]} placements)."

