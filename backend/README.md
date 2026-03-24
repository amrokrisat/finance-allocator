# Backend

This directory contains the Python planning engine for the MVP.

Current responsibilities:

- parse and validate financial intake payloads
- normalize monthly cash flow and balance-sheet inputs
- choose strategy, debt, and savings/investing recommendations
- generate monthly and per-paycheck allocation plans
- validate and evaluate the generated plan
- expose a simple programmatic entrypoint for the frontend or local scripts

Key files:

- `app/api/planner.py` for the public planning entrypoint
- `app/services/` for the modular agent-style planning layers
- `app/sample_data.py` for a representative demo payload
- `scripts/generate_sample_plan.py` for generating a sample output artifact
- `tests/` for unit and integration coverage
