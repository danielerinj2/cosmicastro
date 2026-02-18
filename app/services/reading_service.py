from __future__ import annotations

import json
from datetime import date, timedelta
from typing import Any

from app.constants import LAUNCH_TRUST_MESSAGE, MOON_PHASES
from app.domain.models import PartnerProfile, Reading, User
from app.repos.supabase_repo import SupabaseRepository
from app.services.astro_engine import DeterministicAstroEngine
from app.services.knowledge_service import get_relevant_context
from app.services.llm_service import LLMService
from app.utils.astro import approximate_moon_sign, sun_sign_for_date
from app.utils.time import utc_now


class ReadingService:
    def __init__(self) -> None:
        self.repo = SupabaseRepository()
        self.engine = DeterministicAstroEngine()
        self.llm = LLMService()

    def _voice(self, title: str, facts: str, fallback: str) -> str:
        system = (
            "You are an astrology writing assistant. Be psychologically literate, warm, direct, and non-predictive. "
            "Never invent placements not in the provided facts. "
            "If external knowledge context is provided, treat it as optional reference, not source of chart facts."
        )
        knowledge = get_relevant_context(f"{title} {facts}", max_snippets=2, max_chars=1800)
        user = (
            f"Title: {title}\n"
            f"Facts: {facts}\n"
            f"Knowledge Context (optional): {knowledge if knowledge else 'None'}\n"
            "Write 2-3 concise paragraphs."
        )
        result = self.llm.generate(system_prompt=system, user_prompt=user, fallback_text=fallback)
        return result.text

    def _daily_sections(
        self,
        *,
        sign: str,
        day: date,
        fallback: dict[str, str],
    ) -> dict[str, str]:
        system = (
            "You are an astrology writing assistant. Be psychologically literate, warm, direct, and non-predictive. "
            "Return valid JSON only with keys: general, love, career, wellness. "
            "Each value must be 2-3 sentences and practical, not mystical."
        )
        knowledge = get_relevant_context(f"daily horoscope {sign} {day.isoformat()}", max_snippets=2, max_chars=1500)
        user = (
            f"Sign: {sign}\n"
            f"Date: {day.isoformat()}\n"
            f"Knowledge Context (optional): {knowledge if knowledge else 'None'}\n"
            "Output JSON only."
        )
        fallback_json = json.dumps(
            {
                "general": fallback["general"],
                "love": fallback["love"],
                "career": fallback["career"],
                "wellness": fallback["wellness"],
            }
        )
        raw = self.llm.generate(system_prompt=system, user_prompt=user, fallback_text=fallback_json).text.strip()
        if raw.startswith("```"):
            raw = raw.strip("`")
            if raw.lower().startswith("json"):
                raw = raw[4:].strip()

        try:
            parsed = json.loads(raw)
        except Exception:
            return {
                "general": fallback["general"],
                "love": fallback["love"],
                "career": fallback["career"],
                "wellness": fallback["wellness"],
            }

        sections: dict[str, str] = {}
        for key in ("general", "love", "career", "wellness"):
            value = str(parsed.get(key, "")).strip()
            sections[key] = value if len(value) >= 80 else fallback[key]
        return sections

    @staticmethod
    def _needs_daily_upgrade(content: dict[str, Any]) -> bool:
        legacy_lines = {
            "Name one need directly instead of hinting.",
            "Prioritize one high-impact task and close it.",
            "Reduce cognitive overload with one structured reset block.",
        }
        for key in ("love", "career", "wellness"):
            value = str(content.get(key, "")).strip()
            if not value:
                return True
            if value in legacy_lines:
                return True
            if len(value) < 80:
                return True
        return False

    @staticmethod
    def _needs_yearly_upgrade(content: dict[str, Any]) -> bool:
        meta = content.get("meta", {})
        year_label = str(meta.get("year_label", ""))
        if any(tag in year_label for tag in ("1th", "2th", "3th")):
            return True

        timeline = content.get("timeline", [])
        if len(timeline) < 3:
            return True

        generic_markers = (
            "setting direction around",
            "tests commitment to",
            "focus on integrating lessons",
            "the key focus remains",
        )
        if len(timeline) >= 3:
            texts = [str(item.get("llm_text", "")).strip() for item in timeline]
            if all("the key focus remains" in text.lower() for text in texts):
                return True
            if len(set(texts)) == 1:
                return True
            if any(any(marker in text.lower() for marker in generic_markers) for text in texts):
                return True
            if any(len(text) < 160 for text in texts):
                return True

        return False

    def get_or_create_origin_chart(self, user: User, force_regenerate: bool = False) -> Reading:
        generated = self.engine.origin_chart(user)
        existing = self.repo.get_latest_reading(
            user_id=user.id,
            reading_type="origin_chart",
            mode=generated.mode,
        )
        if existing and not force_regenerate:
            birth_signature = (
                generated.source_data.get("dob"),
                generated.source_data.get("birth_time"),
                generated.source_data.get("lat"),
                generated.source_data.get("lng"),
                generated.source_data.get("timezone"),
            )
            existing_signature = (
                existing.source_data.get("dob"),
                existing.source_data.get("birth_time"),
                existing.source_data.get("lat"),
                existing.source_data.get("lng"),
                existing.source_data.get("timezone"),
            )
            if birth_signature == existing_signature:
                return existing

        fallback_summary = generated.content["summary"]["headline"]
        generated.content["summary"]["llm_voice"] = self._voice(
            title="Origin Chart Summary",
            facts=str(generated.source_data),
            fallback=fallback_summary,
        )
        return self.repo.create_reading(
            user_id=user.id,
            reading_type="origin_chart",
            mode=generated.mode,
            source_data=generated.source_data,
            content=generated.content,
        )

    def get_or_create_yearly_chart(self, user: User, reference_day: date, force_regenerate: bool = False) -> Reading:
        generated = self.engine.yearly_chart(user, reference_day)
        age = int(generated.source_data["age"])
        existing = self.repo.get_latest_reading(
            user_id=user.id,
            reading_type="yearly_chart",
            mode=None,
            profection_age=age,
        )
        if (
            existing
            and not force_regenerate
            and existing.mode == generated.mode
            and not self._needs_yearly_upgrade(existing.content)
        ):
            return existing

        generated.content["summary"]["llm_voice"] = self._voice(
            title="Yearly Chart Summary",
            facts=str(generated.source_data),
            fallback=generated.content["summary"]["headline"],
        )
        return self.repo.create_reading(
            user_id=user.id,
            reading_type="yearly_chart",
            mode=generated.mode,
            source_data=generated.source_data,
            content=generated.content,
            profection_age=age,
        )

    def get_or_create_between_us(
        self,
        user: User,
        partner: PartnerProfile | None,
        partner_name: str | None,
        force_regenerate: bool = False,
    ) -> Reading:
        generated = self.engine.between_us(user, partner, partner_name)
        existing = self.repo.get_latest_reading(
            user_id=user.id,
            reading_type="between_us",
            mode=generated.mode,
            partner_profile_id=partner.id if partner else None,
        )
        if existing and not force_regenerate:
            return existing

        generated.content["summary"]["llm_voice"] = self._voice(
            title="Compatibility Summary",
            facts=str(generated.source_data),
            fallback=generated.content["summary"]["headline"],
        )
        return self.repo.create_reading(
            user_id=user.id,
            reading_type="between_us",
            mode=generated.mode,
            source_data=generated.source_data,
            content=generated.content,
            partner_profile_id=partner.id if partner else None,
        )

    def get_or_create_daily_horoscope(self, user: User, day: date) -> dict[str, Any]:
        sign = user.sun_sign or sun_sign_for_date(user.dob)
        cached = self.repo.get_daily_horoscope(sign, day)
        if cached and not self._needs_daily_upgrade(cached.get("content", {})):
            return cached

        fallback = {
            "headline": f"{sign} daily theme",
            "general": (
                f"As a {sign}, today supports grounded clarity over speed. "
                "Pause before reacting and choose the path that reduces friction instead of creating more of it. "
                "Small intentional decisions will compound into a steadier day."
            ),
            "love": (
                "Speak one emotional need clearly instead of hoping it gets inferred. "
                "Lead with tone, not pressure, and ask a direct question that invites an honest answer. "
                "Clarity today will prevent resentment later."
            ),
            "career": (
                "Pick one meaningful task and move it to done before context-switching. "
                "Set a visible boundary around your focus window and protect it from low-value noise. "
                "Progress will come from completion, not volume."
            ),
            "wellness": (
                "Reset your nervous system with one structured break: step away, hydrate, breathe, and re-enter slowly. "
                "If your mind is crowded, write down the next three actions and ignore the rest for now. "
                "Stability comes from rhythm, not intensity."
            ),
        }
        sections = self._daily_sections(sign=sign, day=day, fallback=fallback)
        content = {**fallback, **sections}
        return self.repo.upsert_daily_horoscope(sign, day, content)

    def get_or_create_moon_phase(self, day: date) -> dict[str, Any]:
        cached = self.repo.get_moon_phase_for_day(day)
        if cached:
            return cached

        cycle_index = ((day.toordinal() // 4) % len(MOON_PHASES))
        phase = MOON_PHASES[cycle_index]
        start_date = day
        end_date = day + timedelta(days=3)
        content = {
            "phase": phase,
            "insight": f"{phase.replace('_', ' ').title()}: simplify your emotional commitments and close one open loop.",
        }
        return self.repo.upsert_moon_phase(phase=phase, start_date=start_date, end_date=end_date, content=content)

    def record_reaction(
        self,
        *,
        user_id: str,
        reaction: str,
        journal_text: str | None = None,
        reading_id: str | None = None,
        daily_horoscope_id: str | None = None,
        moon_phase_id: str | None = None,
    ) -> dict[str, Any]:
        return self.repo.add_reaction(
            user_id=user_id,
            reaction=reaction,
            journal_text=journal_text,
            reading_id=reading_id,
            daily_horoscope_id=daily_horoscope_id,
            moon_phase_id=moon_phase_id,
        )

    def home_context(self, user: User) -> dict[str, Any]:
        today = utc_now().date()
        daily = self.get_or_create_daily_horoscope(user, today)
        moon = self.get_or_create_moon_phase(today)
        return {
            "trust_strip": LAUNCH_TRUST_MESSAGE,
            "daily": daily,
            "moon": moon,
        }
