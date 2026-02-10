# Task: Website Redesign + Reactive Birth-Time Input Fix

## Goal
Upgrade the app from a utility-style interface into a coherent product website/app experience with strong homepage copy and navigation, while fixing reactive input behavior so birth-time fields enable immediately when toggles are clicked.

## Confirmed Issue
The birth-time toggle issue is real.

Root cause:
- On multiple pages, the toggle and dependent fields are inside `st.form`.
- In Streamlit, form widgets do not trigger immediate reruns; updates are applied only on submit.

Affected pages:
- `pages/03_Auth_Sign_Up.py`
- `pages/15_Settings_Profile.py`
- `pages/13_Between_Us.py`

## Product/UI Direction (Phase 1)
- Build a clear public-facing homepage for logged-out users with:
  - value proposition,
  - trust signal,
  - feature summaries,
  - CTA blocks.
- Keep logged-in users in app flow (dashboard-style home), but improve structure and copy for app-like clarity.
- Standardize copy tone across pages: psychologically literate, direct, warm, non-predictive.

## Implementation Plan

### 1) Information Architecture + Navigation Shell
Reasoning:
- Current pages are functional but feel disconnected.
- A shared structure is needed before visual/copy polish.

Tasks:
- Add unified page sections for `Public` vs `App` experience.
- Update top-level entry (`streamlit_app.py`) to show:
  - logged-out homepage content,
  - logged-in app entry links.
- Ensure consistent sidebar and section hierarchy.

### 2) Homepage and Core Marketing Copy
Reasoning:
- User-facing trust and clarity depend on strong first-screen copy.

Tasks:
- Create homepage content blocks:
  - Hero headline + subheadline
  - Trust strip
  - Feature cards (Origin Chart, Between Us, Yearly Chart)
  - “How it works” section
  - CTA section for sign up/sign in
- Align copy to your product positioning doc.

### 3) Reactive Input Fix (Immediate UX Bug)
Reasoning:
- This is a usability regression directly affecting onboarding and partner/profile editing.

Tasks:
- Refactor affected form blocks so toggles rerun immediately:
  - move toggle-driven widgets outside `st.form`, or
  - use session-state + non-form submit flow for dynamic sections.
- Apply to:
  - Sign Up birth-time toggle
  - Settings birth-time toggle
  - Between Us partner DOB/time toggles
- Verify fields enable/disable instantly without save-first behavior.

### 4) Copy/UX Consistency Across Key Pages
Reasoning:
- Once homepage improves, page-level copy should match tone and quality.

Tasks:
- Refine headings and helper text on:
  - Home
  - Origin Chart
  - Between Us
  - Yearly Chart
  - Settings
- Remove placeholder-sounding copy and standardize CTA language.

### 5) QA and Regression Pass
Reasoning:
- Ensure no breakage in auth, reading generation, or integrations after UI refactor.

Tasks:
- Smoke-test app boot and navigation.
- Validate reactive input behavior on all affected pages.
- Validate sign up/sign in and one reading generation path.
- Validate no regressions in Supabase/Groq/SendGrid checks.

## Out of Scope for This Task
- Stripe activation/payment enforcement.
- Major visual theming overhaul beyond practical layout/copy improvements.
- Replacing deterministic astrology engine with full Kerykeion/Flatlib pipeline.

## Progress Tracking
- [ ] Step 1 complete
- [ ] Step 2 complete
- [ ] Step 3 complete
- [ ] Step 4 complete
- [ ] Step 5 complete

## Change Log (to append during implementation)
- Pending approval.
