"""Generate a sample planning output artifact."""

from __future__ import annotations

import json
from pathlib import Path

from app.api.planner import build_financial_plan
from app.sample_data import sample_planning_payload


def main() -> None:
    project_root = Path(__file__).resolve().parents[2]
    payload = sample_planning_payload()
    plan = build_financial_plan(payload)

    backend_output_dir = project_root / "backend" / "output"
    frontend_fixture_dir = project_root / "frontend" / "src" / "lib" / "fixtures"
    backend_output_dir.mkdir(parents=True, exist_ok=True)
    frontend_fixture_dir.mkdir(parents=True, exist_ok=True)

    backend_plan_path = backend_output_dir / "sample_plan.json"
    backend_profile_path = backend_output_dir / "sample_profile.json"
    frontend_plan_path = frontend_fixture_dir / "sample-plan.json"
    frontend_profile_path = frontend_fixture_dir / "sample-profile.json"

    backend_plan_path.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
    backend_profile_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    frontend_plan_path.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
    frontend_profile_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    print(backend_plan_path)
    print(frontend_plan_path)


if __name__ == "__main__":
    main()
