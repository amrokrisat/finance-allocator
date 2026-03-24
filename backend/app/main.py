"""Minimal executable entrypoint for local backend experimentation."""

from __future__ import annotations

import json

from app.api.planner import build_financial_plan
from app.sample_data import sample_planning_payload


def main() -> None:
    print(json.dumps(build_financial_plan(sample_planning_payload()), indent=2))


if __name__ == "__main__":
    main()
