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
        refinement: List[str] = []

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
        if any(item.bucket == "brokerage" for item in plan.monthly_allocations) and savings_plan.emergency_fund_gap > Decimal("0.00"):
            behavioral_risks.append("Brokerage funding may feel premature before full emergency reserves are built.")
        if len(snapshot.request.goals) > 4:
            behavioral_risks.append("Too many simultaneous goals may reduce follow-through.")
            refinement.append("Reduce active goals to one or two headline priorities.")

        plan_quality = 82
        maintainability = 78
        if fragility_risks:
            plan_quality -= 10
            maintainability -= 8
        if savings_plan.emergency_fund_monthly_recommendation == Decimal("0.00") and savings_plan.emergency_fund_gap > Decimal("0.00"):
            plan_quality -= 8
            fragility_risks.append("Emergency gap remains unfunded this month.")

        financial_stability_report = {
            "liquidity_months": round(float(emergency_coverage), 2),
            "net_worth": snapshot.net_worth,
            "debt_to_income_warning": debt_plan.unsustainable_debt_load,
            "buffer_present": any(item.bucket == "buffer" for item in plan.monthly_allocations),
        }

        if not refinement:
            refinement.append("Maintain the plan for one full month and compare actual cash timing against the forecast.")

        return EvaluationReport(
            plan_quality_score=max(0, min(100, plan_quality)),
            maintainability_score=max(0, min(100, maintainability)),
            fragility_risks=fragility_risks,
            behavioral_risks=behavioral_risks,
            refinement_opportunities=refinement,
            financial_stability_report=financial_stability_report,
        )

