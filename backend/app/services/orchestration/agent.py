"""Orchestrator agent for the planning system."""

from __future__ import annotations

from dataclasses import asdict
from decimal import Decimal
from typing import Dict, List

from app.core.finance import clamp_non_negative, money
from app.models.financial import (
    AllocationPlan,
    PlanningRequest,
    PlanningSummary,
    StageStatus,
)
from app.services.allocation.agent import AllocationEngineAgent
from app.services.debt.agent import DebtOptimizationAgent
from app.services.evaluation.agent import EvaluationAgent
from app.services.intake.agent import IntakeFinancialProfileAgent
from app.services.savings_investing.agent import SavingsInvestmentAgent
from app.services.strategy.agent import StrategyAgent
from app.services.testing.agent import TestingAgent


class OrchestratorAgent:
    """Coordinates planning stages, retries, and structured observability."""

    def __init__(self) -> None:
        self.intake_agent = IntakeFinancialProfileAgent()
        self.strategy_agent = StrategyAgent()
        self.debt_agent = DebtOptimizationAgent()
        self.savings_agent = SavingsInvestmentAgent()
        self.allocation_agent = AllocationEngineAgent()
        self.testing_agent = TestingAgent()
        self.evaluation_agent = EvaluationAgent()

    def build_plan(self, request: PlanningRequest) -> PlanningSummary:
        logs: List[Dict[str, object]] = []
        stages: List[StageStatus] = []
        iterations: List[Dict[str, object]] = []

        snapshot = self.intake_agent.process(request)
        stages.append(self._stage("intake", "completed", "Normalized profile and identified constraints."))
        logs.append(self._log("intake", "completed", snapshot.constraints or ["No critical constraints detected."]))

        if snapshot.missing_requirements:
            stages.append(self._stage("planning", "incomplete", "Missing required financial inputs."))
            logs.append(self._log("planning", "incomplete", snapshot.missing_requirements))

        max_iterations = 3
        final_plan: AllocationPlan | None = None
        final_debt_plan = None
        final_savings_plan = None
        final_validation = None
        final_evaluation = None

        for retry_count in range(max_iterations):
            strategy = self.strategy_agent.decide(snapshot, retry_count=retry_count)
            stages.append(self._stage("strategy", "completed", f"Selected {strategy.debt_framework} strategy."))
            logs.append(self._log("strategy", "completed", strategy.strategic_notes))

            discretionary = clamp_non_negative(
                snapshot.monthly_income_total
                - snapshot.monthly_expense_total
                - snapshot.monthly_minimum_debt_total
            )
            extra_debt_budget = money(
                discretionary * strategy.savings_investing_balance.get("debt_weight", Decimal("0.00"))
            )
            debt_plan = self.debt_agent.analyze(snapshot, extra_debt_budget)
            savings_plan = self.savings_agent.build(
                snapshot,
                strategy.savings_investing_balance,
                clamp_non_negative(discretionary - extra_debt_budget),
            )
            plan = self.allocation_agent.build_plan(snapshot, strategy, debt_plan, savings_plan)
            validation = self.testing_agent.validate(snapshot, plan)

            iteration_record = {
                "iteration": retry_count + 1,
                "strategy": strategy.priority_order,
                "debt_framework": debt_plan.recommended_framework,
                "validation_passed": validation.passed,
                "failures": [asdict(failure) for failure in validation.failures],
                "warnings": validation.warnings,
            }
            iterations.append(iteration_record)
            logs.append(self._log("testing", "completed", validation.warnings or ["Validation executed."]))

            if validation.passed:
                final_plan = plan
                final_debt_plan = debt_plan
                final_savings_plan = savings_plan
                final_validation = validation
                stages.append(self._stage("testing", "completed", f"Validation passed on iteration {retry_count + 1}."))
                break

            reroute_note = self._route_failure(validation.failures)
            logs.append(self._log("orchestration", "retrying", [reroute_note]))
            stages.append(self._stage("testing", "retrying", reroute_note))

            if retry_count == max_iterations - 1:
                final_plan = plan
                final_debt_plan = debt_plan
                final_savings_plan = savings_plan
                final_validation = validation

        assert final_plan is not None
        assert final_debt_plan is not None
        assert final_savings_plan is not None
        assert final_validation is not None

        final_evaluation = self.evaluation_agent.evaluate(snapshot, final_plan, final_debt_plan, final_savings_plan)
        stages.append(self._stage("evaluation", "completed", "Generated quality and stability assessment."))
        logs.append(self._log("evaluation", "completed", final_evaluation.refinement_opportunities))

        why_this_plan = self._why_this_plan(strategy.strategic_notes, final_debt_plan.notes, final_savings_plan.notes)
        first_30_days = self._first_30_days(final_plan)
        scenario_levers = self._scenario_levers(snapshot, final_plan, final_savings_plan)
        plan_overview = {
            "monthly_income": snapshot.monthly_income_total,
            "essential_expenses": snapshot.monthly_essential_expense_total,
            "total_expenses": snapshot.monthly_expense_total,
            "minimum_debt_payments": snapshot.monthly_minimum_debt_total,
            "monthly_allocated": final_plan.monthly_allocated_total,
            "cash_buffer": next(
                (item["amount"] for item in [
                    {
                        "bucket": line.bucket,
                        "amount": line.amount,
                    } for line in final_plan.monthly_allocations
                ] if item["bucket"] == "buffer"),
                Decimal("0.00"),
            ),
            "plan_quality_score": final_evaluation.plan_quality_score,
            "maintainability_score": final_evaluation.maintainability_score,
            "stability_score": final_evaluation.stability_score,
            "resilience_summary": final_evaluation.resilience_summary,
        }

        risk_assessment = {
            "validation_failures": [asdict(item) for item in final_validation.failures],
            "validation_warnings": final_validation.warnings,
            "fragility_risks": final_evaluation.fragility_risks,
            "behavioral_risks": final_evaluation.behavioral_risks,
            "behavior_guardrails": final_evaluation.behavior_guardrails,
            "opportunity_areas": final_evaluation.opportunity_areas,
        }

        return PlanningSummary(
            objective=request.objective,
            stages=stages,
            iterations=iterations,
            final_monthly_plan=[
                {
                    "bucket": line.bucket,
                    "name": line.name,
                    "amount": line.amount,
                    "reason": line.reason,
                    "due_day": line.due_day,
                }
                for line in final_plan.monthly_allocations
            ],
            per_paycheck_plan=[
                {
                    "paycheck_index": check.paycheck_index,
                    "expected_income": check.expected_income,
                    "remaining_cash": check.remaining_cash,
                    "allocations": [
                        {
                            "bucket": line.bucket,
                            "name": line.name,
                            "amount": line.amount,
                            "reason": line.reason,
                            "due_day": line.due_day,
                        }
                        for line in check.allocations
                    ],
                }
                for check in final_plan.per_paycheck_allocations
            ],
            debt_payoff_summary={
                "recommended_framework": final_debt_plan.recommended_framework,
                "payoff_order": final_debt_plan.payoff_order,
                "estimated_payoff_months": final_debt_plan.estimated_payoff_months,
                "estimated_interest_cost": final_debt_plan.estimated_interest_cost,
                "interest_saved_vs_alternative": final_debt_plan.interest_saved_vs_alternative,
                "comparison": {
                    name: {
                        "framework": item.framework,
                        "estimated_months": item.estimated_months,
                        "total_interest": item.total_interest,
                        "payoff_order": item.payoff_order,
                    }
                    for name, item in final_debt_plan.comparison.items()
                },
                "unsustainable_debt_load": final_debt_plan.unsustainable_debt_load,
                "notes": final_debt_plan.notes,
            },
            savings_investing_summary={
                "emergency_fund_target": final_savings_plan.emergency_fund_target,
                "emergency_fund_gap": final_savings_plan.emergency_fund_gap,
                "emergency_fund_monthly_recommendation": final_savings_plan.emergency_fund_monthly_recommendation,
                "sinking_funds": final_savings_plan.sinking_funds,
                "retirement_recommendation": final_savings_plan.retirement_recommendation,
                "brokerage_recommendation": final_savings_plan.brokerage_recommendation,
                "short_term_goals": final_savings_plan.short_term_goal_recommendations,
                "notes": final_savings_plan.notes,
            },
            financial_profile_summary=snapshot.financial_profile,
            cash_flow_summary={
                **snapshot.cash_flow_summary,
                "monthly_allocated_total": final_plan.monthly_allocated_total,
                "monthly_buffer_total": plan_overview["cash_buffer"],
            },
            goals_summary=snapshot.goals_summary,
            assumptions=snapshot.assumptions,
            constraints=snapshot.constraints,
            plan_overview=plan_overview,
            why_this_plan=why_this_plan,
            first_30_days=first_30_days,
            scenario_levers=scenario_levers,
            risk_assessment=risk_assessment,
            financial_stability_report=final_evaluation.financial_stability_report,
            suggested_next_iteration_roadmap=final_evaluation.refinement_opportunities,
            logs=logs,
        )

    def _route_failure(self, failures: List[object]) -> str:
        codes = {failure.code for failure in failures}
        if "CASH_TIMING_FAILURE" in codes:
            return "Validation failed on cash timing, so orchestration returns to the allocation engine."
        if "IMPOSSIBLE_BUDGET" in codes:
            return "Budget is impossible under current inputs, so orchestration returns to planning assumptions."
        if "OVER_ALLOCATED" in codes:
            return "Plan is over-allocated, so orchestration requests a leaner strategy and allocation pass."
        return "Validation failed, so orchestration reruns downstream agents with tighter constraints."

    def _log(self, stage: str, status: str, messages: List[str]) -> Dict[str, object]:
        return {"stage": stage, "status": status, "messages": messages}

    def _stage(self, stage: str, status: str, details: str) -> StageStatus:
        return StageStatus(stage=stage, status=status, details=details)

    def _why_this_plan(
        self,
        strategy_notes: List[str],
        debt_notes: List[str],
        savings_notes: List[str],
    ) -> List[str]:
        merged = strategy_notes[:2] + debt_notes[:1] + savings_notes[:1]
        return merged[:4]

    def _first_30_days(self, plan: AllocationPlan) -> List[str]:
        actions: List[str] = []
        for item in plan.monthly_allocations:
            if item.bucket in {"mandatory_expense", "debt_minimum", "debt_extra", "emergency_fund"}:
                actions.append(f"{item.name}: set aside {item.amount} this month.")
            if len(actions) == 5:
                break
        return actions

    def _scenario_levers(
        self,
        snapshot: object,
        plan: AllocationPlan,
        savings_plan: object,
    ) -> List[Dict[str, object]]:
        levers: List[Dict[str, object]] = []
        flexible_expenses = [
            line for line in plan.monthly_allocations if line.bucket == "flexible_expense"
        ]
        if flexible_expenses:
            biggest = max(flexible_expenses, key=lambda item: item.amount)
            levers.append(
                {
                    "title": "Trim flexible spending",
                    "impact": biggest.amount,
                    "description": f"Reducing {biggest.name} would immediately free up cash for debt or savings.",
                }
            )
        brokerage = next((line for line in plan.monthly_allocations if line.bucket == "brokerage"), None)
        if brokerage:
            levers.append(
                {
                    "title": "Pause brokerage temporarily",
                    "impact": brokerage.amount,
                    "description": "Temporarily redirecting taxable investing could increase short-term stability.",
                }
            )
        debt_extra = next((line for line in plan.monthly_allocations if line.bucket == "debt_extra"), None)
        if debt_extra:
            levers.append(
                {
                    "title": "Accelerate debt payoff",
                    "impact": debt_extra.amount,
                    "description": "If extra income appears, adding it to the top debt would shorten the payoff timeline.",
                }
            )
        return levers[:3]
