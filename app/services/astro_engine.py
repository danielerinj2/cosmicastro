from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any, Protocol

from app.constants import BETWEEN_US_DIMENSIONS, HOUSE_TOPICS, YEARLY_TIMELINE_SEGMENTS, ZODIAC_SIGNS
from app.domain.models import PartnerProfile, User
from app.utils.astro import (
    approximate_ascendant,
    approximate_moon_sign,
    compatibility_label,
    deterministic_planetary_positions,
    major_aspects,
    moon_change_warning,
    profected_house,
    sign_to_lord,
    summarize_sign_elements,
)
from app.utils.time import calculate_age_on, current_profection_window


@dataclass
class EngineResult:
    mode: str
    source_data: dict[str, Any]
    content: dict[str, Any]


class AstroEngine(Protocol):
    def origin_chart(self, user: User) -> EngineResult:
        ...

    def yearly_chart(self, user: User, reference_day: date) -> EngineResult:
        ...

    def between_us(self, user: User, partner: PartnerProfile | None, partner_name: str | None) -> EngineResult:
        ...


class DeterministicAstroEngine:
    @staticmethod
    def _ordinal(value: int) -> str:
        if 10 <= (value % 100) <= 20:
            suffix = "th"
        else:
            suffix = {1: "st", 2: "nd", 3: "rd"}.get(value % 10, "th")
        return f"{value}{suffix}"

    def origin_chart(self, user: User) -> EngineResult:
        full_mode = bool(user.birth_time and user.lat is not None and user.lng is not None and user.timezone)
        mode = "full" if full_mode else "sign_only"

        positions = deterministic_planetary_positions(
            user.dob,
            birth_time=user.birth_time,
            include_houses=full_mode,
        )
        moon_note = "approximate" if not full_mode else "precise"
        rising = approximate_ascendant(user.dob, user.birth_time) if full_mode else None
        aspects = major_aspects(positions) if full_mode else None
        dominant_summary = summarize_sign_elements([str(item["sign"]) for item in positions[:8]])

        summary_headline = (
            f"You lead with {positions[0]['sign']} Sun expression and {positions[1]['sign']} emotional tone."
        )
        summary_paragraphs = [
            "This interpretation is built from your stored birth data and rendered in a direct, non-predictive voice.",
            dominant_summary,
        ]
        if not full_mode:
            summary_paragraphs.append(
                "Add your birth time and place to unlock Rising sign, houses, and precise aspect-level depth."
            )

        content = {
            "summary": {"headline": summary_headline, "paragraphs": summary_paragraphs},
            "meta": {
                "mode_label": "Full chart" if full_mode else "Birth-date-only chart",
            },
            "placements": [
                {
                    "planet": item["planet"],
                    "sign": item["sign"],
                    "degree": item["degree"],
                    "house": item["house"],
                    "llm_text": (
                        f"{item['planet']} in {item['sign']} suggests a recurring pattern you can consciously work with."
                    ),
                }
                for item in positions
            ],
            "aspects": aspects,
            "disclaimers": (
                []
                if full_mode
                else [
                    "This reading is based on birth date only.",
                    "Rising sign and houses require an accurate birth time and location.",
                    "Moon sign may shift within the day for some birth dates.",
                ]
            ),
        }

        source_data = {
            "mode": mode,
            "dob": user.dob.isoformat(),
            "birth_time": user.birth_time.isoformat() if user.birth_time else None,
            "birth_location": user.birth_location,
            "lat": user.lat,
            "lng": user.lng,
            "timezone": user.timezone,
            "moon_precision": moon_note,
            "moon_sign_change_possible": moon_change_warning(user.dob),
            "rising": rising,
            "planets": positions,
            "aspects": aspects,
        }
        return EngineResult(mode=mode, source_data=source_data, content=content)

    def yearly_chart(self, user: User, reference_day: date) -> EngineResult:
        full_mode = bool(user.birth_time and user.lat is not None and user.lng is not None and user.timezone)
        mode = "full_profection" if full_mode else "light_year"
        age = calculate_age_on(reference_day, user.dob)
        year_start, year_end = current_profection_window(reference_day, user.dob)
        house = profected_house(age)
        house_topic = HOUSE_TOPICS[house]

        if full_mode:
            asc_sign = approximate_ascendant(user.dob, user.birth_time)
            house_sign = ZODIAC_SIGNS[(ZODIAC_SIGNS.index(asc_sign) + house - 1) % 12]
            lord = sign_to_lord(house_sign)
            mode_label = "Full profection year"
        else:
            house_sign = None
            lord = None
            mode_label = "Birth-date-only year view"

        timeline = [
            {
                "segment": YEARLY_TIMELINE_SEGMENTS[0],
                "llm_text": (
                    f"Beginning of the year is about setting direction around {house_topic.lower()}. "
                    "You are likely to notice what requires structure, what can be simplified, and what deserves clear priority."
                ),
            },
            {
                "segment": YEARLY_TIMELINE_SEGMENTS[1],
                "llm_text": (
                    f"Middle of the year tests commitment to {house_topic.lower()}. "
                    "This phase often brings tradeoffs, feedback, and practical adjustments that make the path more realistic."
                ),
            },
            {
                "segment": YEARLY_TIMELINE_SEGMENTS[2],
                "llm_text": (
                    f"Closing months focus on integrating lessons in {house_topic.lower()}. "
                    "You consolidate what worked, release what drained energy, and carry clearer momentum into the next cycle."
                ),
            },
        ]

        content = {
            "summary": {
                "headline": f"This is a {self._ordinal(house)}-house year focused on {house_topic.lower()}.",
                "paragraphs": [
                    "A profection year means each birthday activates a different life area in a repeating 12-year cycle.",
                    f"Your current cycle activates the {self._ordinal(house)} house, so decisions tied to {house_topic.lower()} carry extra weight this year.",
                ],
            },
            "meta": {
                "age": age,
                "year_label": f"{self._ordinal(house)} house year",
                "mode_label": mode_label,
                "window": f"{year_start.isoformat()} -> {year_end.isoformat()}",
            },
            "house_focus": {
                "house_number": house,
                "label": house_topic,
                "llm_text": f"In this cycle, your attention is repeatedly pulled toward {house_topic.lower()}.",
            },
            "ruling_planet_section": (
                {
                    "planet": lord,
                    "llm_text": (
                        f"Your profection lord is {lord}, which colors the year with {lord.lower()}-style priorities."
                    ),
                }
                if full_mode
                else None
            ),
            "timeline": timeline,
            "practices_and_prompts": [
                "What pattern am I repeating in this life area?",
                "What boundary or commitment would make this year cleaner?",
                "What would progress look like by the end of this profection year?",
            ],
            "disclaimers": (
                ["This reading uses your birth date only. Add time/place to unlock full profection detail."]
                if not full_mode
                else []
            ),
        }

        source_data = {
            "mode": mode,
            "age": age,
            "year_start": year_start.isoformat(),
            "year_end": year_end.isoformat(),
            "profected_house": house,
            "house_topic": house_topic,
            "profected_house_sign": house_sign,
            "profection_lord": lord,
        }
        return EngineResult(mode=mode, source_data=source_data, content=content)

    def between_us(self, user: User, partner: PartnerProfile | None, partner_name: str | None) -> EngineResult:
        if partner and partner.dob and user.dob:
            user_full = bool(user.birth_time and user.lat is not None and user.lng is not None and user.timezone)
            partner_full = bool(
                partner.birth_time and partner.lat is not None and partner.lng is not None and partner.timezone
            )
            mode = "full_synastry" if user_full and partner_full else "partial_synastry"
            partner_display_name = partner.name
            partner_sign = partner.sun_sign or "Unknown"
        elif partner and (partner.sun_sign or partner.dob):
            mode = "sun_sign_pairing"
            partner_display_name = partner.name
            partner_sign = partner.sun_sign or "Unknown"
        else:
            mode = "name_only_reflection"
            partner_display_name = partner_name or (partner.name if partner else "Partner")
            partner_sign = "Unknown"

        dimensions = []
        for idx, (key, label) in enumerate(BETWEEN_US_DIMENSIONS):
            score = compatibility_label((idx + len(partner_display_name)) * 3)
            if mode == "name_only_reflection":
                basis = None
                text = (
                    f"{label}: reflect on where this relationship feels stable versus effortful, "
                    "and what direct conversation would improve it this week."
                )
            else:
                basis = f"{user.sun_sign or 'Sun'} x {partner_sign} pattern"
                text = (
                    f"{label}: this connection shows a `{score}` dynamic. "
                    "Use boundaries and explicit communication to convert friction into growth."
                )

            dimensions.append(
                {
                    "key": key,
                    "label": label,
                    "score_label": score if mode != "name_only_reflection" else "reflect",
                    "astro_basis": basis,
                    "llm_text": text,
                }
            )

        content = {
            "summary": {
                "headline": f"{user.first_name} and {partner_display_name}: compatibility across six dimensions.",
                "paragraphs": [
                    "This result is designed as practical relational guidance, not fate.",
                    "Higher precision requires more complete birth data for both people.",
                ],
            },
            "meta": {
                "mode_label": mode.replace("_", " ").title(),
                "partner_name": partner_display_name,
                "partner_sign": partner_sign,
            },
            "dimensions": dimensions,
            "reflection_prompts": [
                "Where do we communicate clearly, and where do we assume?",
                "Which conflict pattern keeps repeating, and what boundary would interrupt it?",
            ],
            "disclaimers": (
                ["This is a reflection mode reading. Add partner birth data for astrology-backed synastry."]
                if mode == "name_only_reflection"
                else []
            ),
        }

        source_data = {
            "mode": mode,
            "user": {"id": user.id, "sun_sign": user.sun_sign, "dob": user.dob.isoformat()},
            "partner": (
                {
                    "id": partner.id,
                    "name": partner_display_name,
                    "sun_sign": partner.sun_sign,
                    "dob": partner.dob.isoformat() if partner and partner.dob else None,
                }
                if partner
                else {"name": partner_display_name}
            ),
        }
        return EngineResult(mode=mode, source_data=source_data, content=content)
