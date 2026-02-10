# Discover Your Cosmic Self (Streamlit MVP)

This repository now runs a Streamlit MVP connected to:
- Supabase (data/auth storage)
- Groq (LLM voice layer)
- SendGrid (transactional email)
- Stripe (subscription checkout scaffold)

## Quick Start

From `/Users/erindaniel/Documents/New project/astroapp`:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env
```

Fill `.env` with real credentials, then run:

```bash
.venv/bin/streamlit run streamlit_app.py
```

## Required Environment Variables

```bash
SUPABASE_URL=https://<project-ref>.supabase.co
SUPABASE_SERVICE_ROLE_KEY=<service-role-key>
SUPABASE_REQUIRED_TABLES=users,readings,tokens,daily_horoscopes_cache,moon_phase_cache,partner_profiles,reading_reactions

LLM_PROVIDER=groq
GROQ_API_KEY=<groq-api-key>
GROQ_MODEL=llama-3.3-70b-versatile

EMAIL_PROVIDER=sendgrid
SENDGRID_API_KEY=<sendgrid-api-key>
SENDGRID_FROM_EMAIL=<verified-sender@yourdomain.com>
SENDGRID_REGION=global

APP_BASE_URL=http://localhost:8501
ENABLE_PREMIUM_GATING=false
STRIPE_SECRET_KEY=<stripe-secret-key>
STRIPE_PUBLISHABLE_KEY=<stripe-publishable-key>
STRIPE_PRICE_MONTHLY=<stripe-monthly-price-id>
STRIPE_PRICE_YEARLY=<stripe-yearly-price-id>
```

If you want to ignore Stripe for now, keep `ENABLE_PREMIUM_GATING=false` (default) and leave Stripe keys empty.

## Streamlit Cloud Secrets (Important)

On Streamlit Cloud, set these in **App Settings -> Secrets** (TOML format):

```toml
SUPABASE_URL = "https://<project-ref>.supabase.co"
SUPABASE_SERVICE_ROLE_KEY = "<service-role-key>"
SUPABASE_REQUIRED_TABLES = "users,readings,tokens,daily_horoscopes_cache,moon_phase_cache,partner_profiles,reading_reactions"

LLM_PROVIDER = "groq"
GROQ_API_KEY = "<groq-api-key>"
GROQ_MODEL = "llama-3.3-70b-versatile"

EMAIL_PROVIDER = "sendgrid"
SENDGRID_API_KEY = "<sendgrid-api-key>"
SENDGRID_FROM_EMAIL = "<verified-sender@yourdomain.com>"
SENDGRID_REGION = "global"

ENABLE_PREMIUM_GATING = "false"
APP_BASE_URL = "https://<your-app-name>.streamlit.app"
```

Notes:
- `SUPABASE_URL` supports either REST URL (`https://...supabase.co`) or Supabase Postgres DSN (`postgresql://...db.<ref>.supabase.co/...`).
- Keep service-role and API keys private; never commit `.env`.

## Verification Commands

Run these after `.env` is configured:

```bash
.venv/bin/python scripts/check_supabase.py
.venv/bin/python scripts/check_groq.py
.venv/bin/python scripts/check_sendgrid.py
.venv/bin/python scripts/check_stripe.py
```

## Streamlit Pages

- `Auth - Sign Up`
- `Auth - Sign In`
- `Auth - Password Reset`
- `Home`
- `Origin Chart`
- `Daily Horoscope`
- `Between Us`
- `Yearly Chart`
- `Settings / Profile`
- `Journal / History`
- `Supabase Connection Check`
- `Groq Connection Check`
- `SendGrid Connection Check`
- `Stripe Connection Check`

## Database Tables (Current Contract)

- `users`
- `readings`
- `tokens`
- `daily_horoscopes_cache`
- `moon_phase_cache`
- `partner_profiles`
- `reading_reactions`

## AstroDoc Knowledge Ingestion

The app can ingest long-form reference PDFs and make them immediately available to the LLM layer.

Current ingested document files:
- `app/knowledge/AstroDOc.extracted.txt`
- `app/knowledge/AstroDOc.cleaned.txt`
- `app/knowledge/AstroDOc.llm.txt`
- `app/knowledge/AstroDOc.assessment.md`

Ingestion script:

```bash
.venv/bin/python scripts/ingest_astrodoc_pdf.py "/Users/erindaniel/Downloads/AstroDOc.pdf"
```

Runtime use:
- Retrieval service: `app/services/knowledge_service.py`
- Prompt integration: `app/services/reading_service.py`
