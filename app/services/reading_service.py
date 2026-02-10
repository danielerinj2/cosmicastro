from __future__ import annotations

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
            mode=generated.mode,
            profection_age=age,
        )
        if existing and not force_regenerate:
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
        if cached:
            return cached

        fallback = {
            "headline": f"{sign} daily theme",
            "general": "Keep decisions simple today. Act on what is clear and defer what is noisy.",
            "love": "Name one need directly instead of hinting.",
            "career": "Prioritize one high-impact task and close it.",
            "wellness": "Reduce cognitive overload with one structured reset block.",
        }
        facts = f"sign={sign}, date={day.isoformat()}, tone=psychological direct non-predictive"
        llm_text = self._voice("Daily Horoscope", facts, fallback["general"])
        content = {**fallback, "general": llm_text}
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
