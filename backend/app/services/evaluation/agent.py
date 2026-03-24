"""Evaluation agent for plan quality."""

from __future__ import annotations

from decimal import Decimal
from typing import List

from app.models.financial import AllocationPlan, DebtPlan, EvaluationReport, PlanningSnapshot, SavingsInvestmentPlan


class EvaluationAgent:
    """Scores the plan and flags fragility or behavior risks."""

    def evaluate(
        self,
        snapshot: PlanningSnapshot,
        plan: AllocationPlan,
        debt_plan: DebtPlan,
        savings_plan: SavingsInvestmentPlan,
    ) -> EvaluationReport:
        fragility_risks: List[str] = []
        behavioral_risks: List[str] = []
        behavior_guardrails: List[str] = []
        refinement: List[str] = []
        opportunity_areas: List[str] = []

        emergency_coverage = (
            snapshot.liquid_assets_total / snapshot.monthly_essential_expense_total
            if snapshot.monthly_essential_expense_total > Decimal("0.00")
            else Decimal("0.00")
        )
        if emergency_coverage < Decimal("1.0"):
            fragility_risks.append("Liquid reserves cover less than one month of essential expenses.")
            refinement.append("Increase emergency funding priority until at least one month is covered.")
        if debt_plan.unsustainable_debt_load:
            fragility_risks.append("Debt load appears heavy relative to income.")
            refinement.append("Consider debt restructuring or temporary spending cuts.")
            opportunity_areas.append("Debt reduction strategy needs stronger near-term focus.")
        if any(item.bucket == "brokerage" for item in plan.monthly_allocations) and savings_plan.emergency_fund_gap > Decimal("0.00"):
            behavioral_risks.append("Brokerage funding may feel premature before full emergency reserves are built.")
            behavior_guardrails.append("Keep brokerage contributions modest until emergency reserves cover at least one month.")
        if len(snapshot.request.goals) > 4:
            behavioral_risks.append("Too many simultaneous goals may reduce follow-through.")
            refinement.append("Reduce active goals to one or two headline priorities.")
            opportunity_areas.append("Goal sprawl is making the plan harder to maintain.")

        plan_quality = 82
        maintainability = 78
        stability = 80
        if fragility_risks:
            plan_quality -= 10
            maintainability -= 8
            stability -= 12
        if savings_plan.emergency_fund_monthly_recommendation == Decimal("0.00") and savings_plan.emergency_fund_gap > Decimal("0.00"):
            plan_quality -= 8
            fragility_risks.append("Emergency gap remains unfunded this month.")
            stability -= 8
        if any(item.bucket == "buffer" for item in plan.monthly_allocations):
            behavior_guardrails.append("Preserve the cash buffer rather than spending it immediately.")
        if debt_plan.recommended_framework == "snowball":
            behavior_guardrails.append("Use quick debt wins to stay motivated, but revisit total interest over time.")
        else:
            behavior_guardrails.append("Stay consistent with the avalanche plan to maximize interest savings.")

        if savings_plan.emergency_fund_monthly_recommendation > Decimal("0.00"):
            opportunity_areas.append("Emergency reserves are improving, but still below the target.")
        if not opportunity_areas:
            opportunity_areas.append("Maintain the current plan and compare actual spending against the model.")

        financial_stability_report = {
            "liquidity_months": round(float(emergency_coverage), 2),
            "net_worth": snapshot.net_worth,
            "debt_to_income_warning": debt_plan.unsustainable_debt_load,
            "buffer_present": any(item.bucket == "buffer" for item in plan.monthly_allocations),
        }

        if not refinement:
            refinement.append("Maintain the plan for one full month and compare actual cash timing against the forecast.")

        if stability >= 85:
            resilience_summary = "The plan looks stable for a typical month and has some room for setbacks."
        elif stability >= 70:
            resilience_summary = "The plan is workable, but a surprise expense would still create pressure."
        else:
            resilience_summary = "The plan is fragile and needs tighter focus on cash safety and debt pressure."

        return EvaluationReport(
            plan_quality_score=max(0, min(100, plan_quality)),
            maintainability_score=max(0, min(100, maintainability)),
            stability_score=max(0, min(100, stability)),
            fragility_risks=fragility_risks,
            behavioral_risks=behavioral_risks,
            behavior_guardrails=behavior_guardrails,
            refinement_opportunities=refinement,
            opportunity_areas=opportunity_areas,
            resilience_summary=resilience_summary,
            financial_stability_report=financial_stability_report,
        )
