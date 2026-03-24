"""Savings and investing agent."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Dict, List

from app.core.finance import clamp_non_negative, money
from app.models.financial import Goal, PlanningSnapshot, SavingsInvestmentPlan


class SavingsInvestmentAgent:
    """Builds emergency, goal, retirement, and brokerage recommendations."""

    def build(
        self,
        snapshot: PlanningSnapshot,
        strategy_weights: Dict[str, Decimal],
        monthly_optional_budget: Decimal,
    ) -> SavingsInvestmentPlan:
        emergency_target = money(
            snapshot.monthly_essential_expense_total * snapshot.request.preferences.target_emergency_months
        )
        emergency_gap = clamp_non_negative(emergency_target - snapshot.liquid_assets_total)
        emergency_monthly = min(
            emergency_gap,
            money(monthly_optional_budget * strategy_weights.get("emergency_fund_weight", Decimal("0.00"))),
        )

        retirement_match = self._retirement_match(snapshot)
        retirement_extra = money(
            monthly_optional_budget * strategy_weights.get("retirement_weight", Decimal("0.00"))
        )
        retirement_total = money(retirement_match + retirement_extra)

        brokerage_total = money(
            monthly_optional_budget * strategy_weights.get("brokerage_weight", Decimal("0.00"))
        )
        if not snapshot.request.preferences.brokerage_enabled:
            brokerage_total = money("0")

        sinking_funds: List[Dict[str, object]] = []
        short_term_goals: List[Dict[str, object]] = []

        goal_weight = strategy_weights.get("goal_weight", Decimal("0.00"))
        remaining_goal_budget = money(monthly_optional_budget * goal_weight)
        sorted_goals = sorted(snapshot.request.goals, key=lambda goal: (goal.priority, goal.name))

        for goal in sorted_goals:
            gap = clamp_non_negative(goal.target_amount - goal.current_amount)
            recommended = min(gap, self._monthly_goal_need(goal))
            recommended = min(recommended, remaining_goal_budget)
            remaining_goal_budget = money(remaining_goal_budget - recommended)
            payload = {
                "name": goal.name,
                "goal_type": goal.goal_type,
                "target_amount": goal.target_amount,
                "current_amount": goal.current_amount,
                "recommended_monthly": recommended,
                "gap": gap,
                "priority": goal.priority,
            }
            if goal.goal_type == "sinking_fund":
                sinking_funds.append(payload)
            else:
                short_term_goals.append(payload)

        notes = [
            "Emergency liquidity is funded before brokerage unless the user has ample cash reserves.",
        ]
        if brokerage_total > Decimal("0.00") and emergency_gap > Decimal("0.00"):
            notes.append("Brokerage is still modest because the emergency fund is not fully built.")

        return SavingsInvestmentPlan(
            emergency_fund_target=emergency_target,
            emergency_fund_gap=emergency_gap,
            emergency_fund_monthly_recommendation=emergency_monthly,
            sinking_funds=sinking_funds,
            retirement_recommendation=retirement_total,
            brokerage_recommendation=brokerage_total,
            short_term_goal_recommendations=short_term_goals,
            notes=notes,
        )

    def _monthly_goal_need(self, goal: Goal) -> Decimal:
        if not goal.target_date:
            return clamp_non_negative(goal.target_amount - goal.current_amount)
        months_remaining = max(1, self._months_until(goal.target_date))
        gap = clamp_non_negative(goal.target_amount - goal.current_amount)
        return money(gap / Decimal(months_remaining))

    def _months_until(self, target_date: date) -> int:
        today = date.today()
        return max(1, (target_date.year - today.year) * 12 + target_date.month - today.month)

    def _retirement_match(self, snapshot: PlanningSnapshot) -> Decimal:
        preferences = snapshot.request.preferences
        if not preferences.wants_employer_match:
            return money("0")
        match_percent = min(preferences.employer_match_rate, preferences.employer_match_cap_percent)
        return money(snapshot.monthly_income_total * (match_percent / Decimal("100")))

