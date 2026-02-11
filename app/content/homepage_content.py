from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

CONTENT_PATH = Path(__file__).resolve().parent / "homepage_content.json"

DEFAULT_HOMEPAGE_CONTENT: dict[str, Any] = {
    "hero": {
        "title": "Orbit AI",
        "subtitle": "The astrologer that sees the big picture and the fine details.",
        "cta_text": "Get Your Daily Prediction",
    },
    "intro": {
        "paragraph_1": (
            "You've read your horoscope. It said something about 'new beginnings' and "
            "'trusting the process.' Cool. So did everyone else's."
        ),
        "paragraph_2": (
            "Most astrology apps give you recycled paragraphs based on your sun sign alone. "
            "That's like diagnosing someone by looking at their shoes."
        ),
        "punch_line": "Orbit actually uses all of it.",
    },
    "how_it_works": {
        "label": "HOW IT WORKS",
        "cards": [
            {
                "step": "01",
                "title": "Tell us when and where you were born.",
                "body": (
                    "Date. Time. Location. That's all we need to generate your complete natal chart "
                    "with precise planetary positions, house placements, and aspects."
                ),
            },
            {
                "step": "02",
                "title": "Get readings that are actually yours.",
                "body": (
                    "Every horoscope, every insight, every forecast is generated from your unique chart. "
                    "Not your sun sign. Your entire sky."
                ),
            },
            {
                "step": "03",
                "title": "Ask anything.",
                "body": (
                    "Open a conversation with Orbit and treat it like your personal astrologer. "
                    "Career decisions. Relationship confusion. That weird feeling you can't shake. "
                    "Orbit connects your question to what's happening in your chart right now."
                ),
            },
        ],
    },
    "daily_feature": {
        "label": "DAILY HOROSCOPE",
        "title": "Daily Personalized Horoscope",
        "paragraph_1": (
            "Every morning you wake up to a reading built from your natal chart crossed with the day's "
            "real-time transits. Mercury square your natal Mars today? You'll know before you send that risky text."
        ),
        "tagline": "No two users get the same horoscope. Ever.",
    },
    "birth_chart_feature": {
        "label": "BIRTH CHART",
        "title": "Birth Chart Analysis",
        "paragraph_1": (
            "Your full natal chart, decoded in plain language. Sun, Moon, Rising, Mercury, Venus, Mars "
            "- all the way through Pluto. House placements. Major aspects. Pattern recognition."
        ),
        "paragraph_2": (
            "Orbit doesn't just list your placements. It tells you what they mean together. Why your Scorpio "
            "Moon and Gemini rising make you feel like two different people. Why you keep attracting the same type. "
            "Where your blind spots are."
        ),
        "tagline": "This is the reading most people pay hundreds of dollars for.",
    },
    "compatibility_feature": {
        "label": "COMPATIBILITY",
        "title": "Compatibility Matching",
        "paragraph_1": (
            "Enter someone else's birth details and Orbit runs a full synastry analysis. It compares both charts "
            "planet by planet and shows you where the chemistry lives, where the friction builds, and what the long game actually looks like."
        ),
        "paragraph_2": (
            "Works for romantic partners, friends, business relationships, even that coworker you can't figure out."
        ),
        "tagline": "No sugarcoating. Just the real dynamic between two charts.",
    },
    "chatbot_feature": {
        "label": "AI ASTROLOGER",
        "title": "The Chatbot Astrologer",
        "intro": (
            "Orbit isn't a static report. It's a conversation. Ask it real questions and get real answers rooted in your chart and current transits."
        ),
        "messages": [
            {
                "role": "user",
                "text": "I got offered a new job but something feels off. Should I take it?",
            },
            {
                "role": "assistant",
                "text": (
                    "Your 10th house ruler is currently being squared by transiting Saturn, which often creates doubt around career moves; "
                    "but it's productive doubt. Saturn wants you to negotiate harder, not walk away. Your natal Jupiter in the 6th suggests "
                    "you thrive in roles with daily variety. Does this job offer that?"
                ),
            },
            {
                "role": "user",
                "text": "Not really. It's pretty rigid.",
            },
            {
                "role": "assistant",
                "text": (
                    "That's likely where the hesitation lives. With your chart, structure is fine but monotony kills your momentum. "
                    "I'd counter-offer with flexible terms or keep looking. Mars enters your 10th house in six weeks - a better offer may surface."
                ),
            },
        ],
        "closing_line": (
            "That's not a magic trick. That's astrology applied to your actual life by an AI that never forgets your chart."
        ),
    },
    "yearly_feature": {
        "label": "YEARLY FORECAST",
        "title": "Yearly Forecast",
        "paragraph_1": (
            "A month-by-month breakdown of your year ahead. Major transits hitting your chart, eclipse seasons that activate your houses, "
            "Saturn and Jupiter shifts that reshape your trajectory."
        ),
        "paragraph_2": "Know when to push. Know when to pause. Know when the chaos has a purpose.",
        "tagline": "Updated in real time as planetary positions evolve.",
    },
    "social_proof": {
        "title": "What People Are Saying",
        "line": "We just launched. You're early. But your readings are still accurate.",
        "placeholder_text": "Testimonials coming soon",
    },
    "closing": {
        "title": "Your chart already has the answers.",
        "subtitle": "You just haven't had the right conversation yet.",
        "cta_text": "Meet Your Astrologer",
    },
}


def _merge_defaults(base: dict[str, Any], current: dict[str, Any]) -> dict[str, Any]:
    merged = deepcopy(base)
    for key, value in current.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            nested = deepcopy(merged[key])
            nested.update(value)
            merged[key] = nested
        else:
            merged[key] = value
    return merged


def load_homepage_content() -> dict[str, Any]:
    if not CONTENT_PATH.exists():
        return deepcopy(DEFAULT_HOMEPAGE_CONTENT)
    try:
        parsed = json.loads(CONTENT_PATH.read_text(encoding="utf-8"))
    except Exception:
        return deepcopy(DEFAULT_HOMEPAGE_CONTENT)
    if not isinstance(parsed, dict):
        return deepcopy(DEFAULT_HOMEPAGE_CONTENT)
    return _merge_defaults(DEFAULT_HOMEPAGE_CONTENT, parsed)


def save_homepage_content(content: dict[str, Any]) -> None:
    CONTENT_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONTENT_PATH.write_text(
        json.dumps(content, ensure_ascii=True, indent=2),
        encoding="utf-8",
    )
