from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

CONTENT_PATH = Path(__file__).resolve().parent / "homepage_content.json"

DEFAULT_HOMEPAGE_CONTENT: dict[str, Any] = {
    "hero": {
        "title": "Your birth chart. Your personal astrologer.",
        "subtitle": "Orbit reads your complete natal chart and gives you real, personalized guidance - not generic horoscope fluff.",
        "cta_text": "Get Your Daily Prediction",
    },
    "how_it_works": [
        {
            "step": "01",
            "title": "Enter Your Birth Details",
            "description": "Date, time, and location are enough to build your precise chart.",
        },
        {
            "step": "02",
            "title": "Get Your Full Chart",
            "description": "Planets, houses, and aspects are mapped together in one coherent reading.",
        },
        {
            "step": "03",
            "title": "Ask Anything",
            "description": "Chat with your personal AI astrologer for direct guidance on real decisions.",
        },
    ],
    "features": [
        {
            "label": "Daily",
            "headline": "Daily Personalized Horoscope",
            "body": "Each reading is built from your natal chart and live transits so you get concrete, relevant guidance every day.",
            "visual_title": "Transit-Aware Daily Insight",
            "visual_body": "Designed for fast clarity: one grounded theme, relationship signal, career focus, and wellness recommendation.",
        },
        {
            "label": "Natal",
            "headline": "Birth Chart Analysis",
            "body": "Orbit combines signs, houses, and aspects into one readable narrative so you can understand your core patterns and blind spots.",
            "visual_title": "Whole-Chart Interpretation",
            "visual_body": "No isolated placement blurbs. Your chart is interpreted as one system with meaningful connections.",
        },
        {
            "label": "Synastry",
            "headline": "Compatibility Matching",
            "body": "Compare two charts across emotional flow, communication style, chemistry, long-term stability, and growth dynamics.",
            "visual_title": "Real Dynamic, Not A Score",
            "visual_body": "Get a dimensional read on where the connection is smooth, where it is tense, and what to do about it.",
        },
        {
            "label": "Conversation",
            "headline": "The Chatbot Astrologer",
            "body": "Ask direct questions and get chart-grounded responses instantly. Orbit remembers your context and answers with practical detail.",
            "visual_title": "Context-Aware Guidance",
            "visual_body": "Career move, relationship tension, timing confusion - ask one question and get an actionable next step.",
        },
        {
            "label": "Long-Range",
            "headline": "Yearly Forecast",
            "body": "See the year as a timeline of themes so you know when to push, when to pause, and where your focus will matter most.",
            "visual_title": "Month-by-Month Focus",
            "visual_body": "Track major activation periods and use them intentionally instead of reacting late.",
        },
    ],
    "chat_preview": {
        "messages": [
            {
                "role": "user",
                "text": "I got offered a new job but something feels off. Should I take it?",
            },
            {
                "role": "assistant",
                "text": "Your 10th house ruler is being squared by transiting Saturn, which can create productive doubt around career moves. Saturn is asking for better terms, not automatic rejection.",
            },
            {
                "role": "user",
                "text": "It seems rigid and I am worried I will lose momentum.",
            },
            {
                "role": "assistant",
                "text": "That tracks your chart pattern. Structure helps you, but monotony drains you. Counter-offer for flexibility first. If they cannot move, keep looking while this transit tightens your standards.",
            },
        ]
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
