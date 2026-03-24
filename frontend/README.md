# Frontend

This directory contains the minimal Next.js frontend for the MVP.

Current responsibilities:

- collect a compact financial intake profile
- submit the profile to the planner backend
- render a results dashboard
- show monthly plan, per-paycheck plan, debt summary, and risk summary

Current MVP tradeoff:

- the intake UI is intentionally compact and single-scenario
- validation depth is mostly handled by the backend
- the app expects a planner endpoint via `NEXT_PUBLIC_PLANNER_API_URL`
