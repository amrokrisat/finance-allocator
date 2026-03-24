"""Public backend entrypoints for the finance planning engine."""

from __future__ import annotations

from typing import Any, Dict

from app.schemas.planning import planning_request_from_dict, planning_summary_to_dict
from app.services.orchestration.agent import OrchestratorAgent


def build_financial_plan(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Create a full planning response from a plain Python payload."""
    request = planning_request_from_dict(payload)
    summary = OrchestratorAgent().build_plan(request)
    return planning_summary_to_dict(summary)

