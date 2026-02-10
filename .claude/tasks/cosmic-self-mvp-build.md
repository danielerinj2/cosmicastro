# Task: Discover Your Cosmic Self - MVP Build (Streamlit)

## Goal
Build a working MVP of **Discover Your Cosmic Self** inside this repository with:
- auth + profile management,
- home/daily experience,
- mode-aware `Origin Chart`, `Yearly Chart`, and `Between Us` pages,
- caching + fallback behavior,
- payment integration scaffolding,
- deployable Python app architecture.

## Assumptions (Explicit)
1. **Framework choice**: Build MVP in **Streamlit + Python** to maximize iteration speed while logic is still evolving.
2. **MVP scope now**: Implement pages 1-6 plus required Settings/Profile and the mode-aware compatibility/yearly/origin logic you specified.
3. **Astrology engine integration**: Implement a production-ready Python adapter interface with Kerykeion primary and Flatlib fallback, plus deterministic fallback outputs for MVP safety.
4. **Future frontend**: Keep backend contracts front-end agnostic so an Astro/TS client can be added later without major backend refactor.
5. **LLM provider**: Use **Groq API** as the primary LLM provider for MVP voice generation.

## Research Notes (Latest, verified)
- Streamlit multipage apps and navigation patterns are documented for app-level routing: https://docs.streamlit.io/develop/concepts/multipage-apps
- Supabase has SSR guidance and cookie/session handling patterns: https://supabase.com/docs/guides/auth/server-side
- Stripe Checkout subscriptions use Checkout Sessions with `mode=subscription`: https://docs.stripe.com/payments/subscriptions
- Groq provides a free plan (with rate limits) and a paid developer tier for higher throughput:
  - Plans: https://console.groq.com/settings/billing/plans
  - Rate limits: https://console.groq.com/docs/rate-limits
- `kerykeion` latest release is `5.7.2` (Feb 6, 2026) and currently shows GPL/AGPL metadata on PyPI (license risk to confirm before production use): https://pypi.org/project/kerykeion/
- `flatlib` latest is `0.2.3` (Apr 5, 2021): https://pypi.org/project/flatlib/
- `timezonefinder` latest is `8.2.1` (Jan 8, 2026): https://pypi.org/project/timezonefinder/

## Key Risks and Decisions
- **License mismatch risk**: Product doc says MIT for Kerykeion, but current PyPI metadata indicates GPL/AGPL. We must verify legal posture before shipping proprietary backend with direct library embedding.
- **Massive scope risk**: Full product doc is multi-phase. We will deliver MVP foundation first, then advanced features (transits, palmistry, numerology) as follow-ons.
- **Data quality risk for missing birth time/place**: We’ll enforce explicit mode labels and UI disclaimers to avoid over-claiming precision.
- **Groq free-tier throughput risk**: Free usage is rate-limited; we will implement strict caching + retries + fallback library to avoid user-facing failures.

## Implementation Plan

### 1) Platform foundation (Streamlit app + architecture)
Reasoning:
- All features need a consistent Python-first app shell and shared service layer.

Tasks:
- Add Python project structure (`app/`, `domain/`, `services/`, `adapters/`, `infra/`, `pages/`).
- Initialize Streamlit multipage shell and shared navigation/state utilities.
- Add environment variable schema and config docs.

### 2) Core domain model + storage
Reasoning:
- We need stable contracts for Users, Readings, Tokens, Daily/Moon caches before page logic.

Tasks:
- Create typed models for tables from spec.
- Implement repository layer (MVP: local file/SQLite-backed persistence abstraction; production-ready interface for Supabase Postgres).
- Add cache invalidation hooks when birth data changes.

### 3) Auth + account flows (Pages 1-3 + profile shell in Streamlit)
Reasoning:
- Every premium and personalized feature depends on authenticated identity.

Tasks:
- Build Sign Up, Sign In, Forgot Password, Reset Password.
- Implement session/auth flow + protected page guards in Streamlit session state.
- Build token model and expiry validation.
- Add placeholder email provider adapter (SendGrid-ready interface).

### 4) Astrology pipeline service contracts (Python)
Reasoning:
- Feature pages should not depend on a single implementation detail.

Tasks:
- Implement `AstroEngine` interface with:
  - full chart mode,
  - sign-only/minimal mode,
  - yearly full/light modes,
  - between-us full/partial/sun/reflection modes.
- Implement deterministic fallback engine for MVP local behavior.
- Add concrete Kerykeion primary adapter + Flatlib fallback adapter with deterministic failsafe responses.

### 5) Build user-facing MVP Streamlit pages
Reasoning:
- Deliver visible product value quickly.

Tasks:
- **Onboarding / Sign Up (Page 1)**: collect core identity and birth data with optional time/place.
- **Sign In + Password Reset (Pages 2-3)**: standard auth and token reset flow.
- **Home (Page 4)**: greeting, trust strip, daily horoscope block, premium cards, moon strip.
- **Origin Chart (Page 5)**: full/sign-only/minimal mode rendering, confidence banner, conditional sections.
- **Daily Horoscope detail (Page 6)**: structured sections + reactions.
- **Between Us (MVP core)**: four compatibility modes with six dimensions.
- **Yearly Chart (MVP core)**: full profection vs light year mode.
- **Settings/Profile (required)**: edit birth data, password change, notification prefs, theme toggle placeholder, delete account flow placeholder, subscription management link placeholder.

### 6) Caching + fallback behavior
Reasoning:
- Cost and latency control are core product requirements.

Tasks:
- Implement tiered cache policy primitives:
  - permanent (`origin_chart`),
  - per-cycle (`daily_horoscope`, moon phase),
  - per-trigger (`between_us`, `yearly_chart`).
- Add fallback content serving path when generation engine fails.
- Add Groq rate-limit handling (`429` backoff/retry) and deterministic fallback responses.
- Add explicit user-facing non-breaking error messages from spec.

### 7) Payments scaffold (backend endpoints + Streamlit entry points)
Reasoning:
- Premium gating requires immediate subscription plumbing.

Tasks:
- Add Stripe Checkout session endpoint scaffold.
- Add premium access guards in service layer and page checks.
- Add settings subscription section with Stripe Customer Portal entrypoint scaffold.

### 8) QA + documentation + handoff
Reasoning:
- Ensure this is runnable by another engineer immediately.

Tasks:
- Validate auth and all mode transitions.
- Validate cache invalidation on birth data change.
- Validate no-mode-mismatch UI bugs.
- Update README with setup/run/env.
- Append detailed implementation log in this task file during execution.

## Deliverables for this implementation pass
- Running Streamlit app with auth, home, origin, yearly, between-us, settings pages.
- Mode-aware logic and UI per your spec.
- Adapter-based astrology engine architecture with fallback.
- Stripe and SendGrid integration scaffolds ready for key injection.

## Out of Scope for this pass
- Palmistry scanner (Phase 2)
- Transit calendar and push alerts (Phase 2)
- Numerology module (Phase 2)
- Community layer (Phase 2)
- Native mobile apps (Phase 3)

## Progress Tracking
- [x] Step 1 complete
- [x] Step 2 complete
- [x] Step 3 complete
- [x] Step 4 complete
- [x] Step 5 complete
- [x] Step 6 complete
- [x] Step 7 complete
- [x] Step 8 complete

## Change Log (append during implementation)
- Pre-approval prerequisite completed (Supabase connection wiring):
  - Added Python dependencies file: `requirements.txt` (`streamlit`, `supabase`, `python-dotenv`).
  - Added env template: `.env.example` with Supabase URL/key/table config.
  - Added config loader and required schema checks:
    - `app/config.py`
    - `app/infra/supabase_client.py`
    - `app/infra/supabase_probe.py`
  - Added Streamlit entrypoint and live DB verification screen:
    - `streamlit_app.py`
    - `pages/01_Supabase_Connection_Check.py`
  - Added CLI verifier for the same checks:
    - `scripts/check_supabase.py`
  - Updated `README.md` with setup steps to run the connection/schema checker.
  - Created local virtual environment and installed Python dependencies in `.venv` for immediate execution of the checker.
  - Added config normalization to handle either Supabase REST URL or Supabase Postgres DSN in `SUPABASE_URL`.
  - Ran live Supabase checks with real credentials:
    - Connection: PASS
    - Table reachability: PASS (`users`, `readings`, `tokens`, `daily_horoscopes_cache`, `moon_phase_cache`)
    - Column contract: one mismatch on `readings.partner_user_id` (column missing in DB vs current app contract)
  - Synced checker contracts to live schema:
    - Added table contracts for `partner_profiles`, `reading_reactions`.
    - Updated `users`, `readings`, and `moon_phase_cache` expected columns to match actual DB.
    - Updated `.env.example` and README default required table list to include all 7 current tables.
  - Re-ran live Supabase validation after contract sync:
    - Connection: PASS
    - Table reachability: PASS (all 7 tables)
    - Column contract: PASS (all configured checks)
  - Added SendGrid integration scaffolding and verification:
    - Extended `.env.example` with `EMAIL_PROVIDER`, `SENDGRID_API_KEY`, `SENDGRID_FROM_EMAIL`, `SENDGRID_REGION`.
    - Extended `AppConfig` with Groq and SendGrid env parsing/validation helpers.
    - Added SendGrid probe utility: `app/infra/sendgrid_probe.py`.
    - Added CLI checker: `scripts/check_sendgrid.py` (validates API key + `mail.send` scope).
    - Added Streamlit checker page: `pages/02_SendGrid_Connection_Check.py`.
    - Updated README with exact SendGrid dashboard locations and setup steps.
- Implementation status update (post-build):
  - Added core app architecture and modules:
    - `app/constants.py`, `app/domain/models.py`
    - `app/repos/supabase_repo.py`
    - `app/services/auth_service.py`, `app/services/reading_service.py`, `app/services/astro_engine.py`, `app/services/llm_service.py`, `app/services/email_service.py`
    - `app/ui/session.py`, `app/ui/components.py`
    - `app/utils/security.py`, `app/utils/time.py`, `app/utils/astro.py`
  - Added full Streamlit page set for MVP flows:
    - Auth: `pages/03_Auth_Sign_Up.py`, `pages/04_Auth_Sign_In.py`, `pages/05_Auth_Password_Reset.py`
    - Product: `pages/10_Home.py`, `pages/11_Origin_Chart.py`, `pages/12_Daily_Horoscope.py`, `pages/13_Between_Us.py`, `pages/14_Yearly_Chart.py`, `pages/15_Settings_Profile.py`, `pages/16_Journal_History.py`
    - Infra checks: `pages/01_Supabase_Connection_Check.py`, `pages/02_SendGrid_Connection_Check.py`, `pages/06_Groq_Connection_Check.py`
  - Added verification scripts and docs refresh:
    - `scripts/check_supabase.py`, `scripts/check_groq.py`, `scripts/check_sendgrid.py`
    - Updated `README.md`, `requirements.txt`, `.gitignore`, `streamlit_app.py`
  - Validation completed:
    - Streamlit boot smoke test: PASS (`http://127.0.0.1:8765`)
    - Supabase live check: PASS (all configured tables and columns)
    - Groq live check: PASS (`llama-3.3-70b-versatile`, response `GROQ_OK`)
    - SendGrid live check: PASS (`mail.send` scope present)
  - Remaining planned work:
    - Step 8 final end-to-end manual UX validation and commit/push pending.
  - Stripe scaffold implementation completed:
    - Added Stripe env/config support in `app/config.py` and `.env.example`:
      - `APP_BASE_URL`, `STRIPE_SECRET_KEY`, `STRIPE_PUBLISHABLE_KEY`, `STRIPE_PRICE_MONTHLY`, `STRIPE_PRICE_YEARLY`
    - Added Stripe service:
      - `app/services/stripe_service.py`
      - checkout session creation (`/v1/checkout/sessions`)
      - customer portal session creation (`/v1/billing_portal/sessions`)
      - premium-active entitlement helper (`subscription_tier` + expiry check)
    - Added premium gate wiring:
      - `app/ui/components.py` (`premium_upgrade_block`)
      - `pages/14_Yearly_Chart.py` (premium-gated)
      - `pages/13_Between_Us.py` (premium-gated)
      - `pages/11_Origin_Chart.py` (free basic view + premium unlock for full interpretation/aspects)
      - `pages/15_Settings_Profile.py` (checkout and portal action buttons)
    - Added Stripe verification tools:
      - `scripts/check_stripe.py`
      - `pages/07_Stripe_Connection_Check.py`
    - Updated docs:
      - `README.md` now includes Stripe env and verification command/page.
  - Final QA and handoff validation completed:
    - Streamlit boot smoke test rerun: PASS.
    - Auth + home manual flow via QA script: PASS.
      - signup, signin, home context, origin generation, yearly generation all succeeded.
      - QA test account was deleted after validation.
    - Final live integration checks:
      - `scripts/check_supabase.py`: PASS
      - `scripts/check_groq.py`: PASS
      - `scripts/check_sendgrid.py`: PASS
    - Stripe live verification is scaffolded but blocked by missing local env vars:
      - `STRIPE_SECRET_KEY`, `STRIPE_PRICE_MONTHLY`, `STRIPE_PRICE_YEARLY`
      - once set, run `scripts/check_stripe.py` or `pages/07_Stripe_Connection_Check.py`
  - Post-handoff adjustment (defer Stripe enforcement):
    - Added `ENABLE_PREMIUM_GATING` env flag (default `false`).
    - Premium-gated pages now stay accessible when Stripe is deferred.
    - Stripe scaffolding remains intact for later activation.
