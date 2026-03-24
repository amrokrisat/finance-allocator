"""Strategy agent for the monthly plan."""

from __future__ import annotations

from decimal import Decimal
from typing import List

from app.core.finance import money
from app.models.financial import PlanningSnapshot, StrategyDecision


class StrategyAgent:
    """Chooses a simple deterministic strategy profile.

    The strategy is intentionally data-driven and conservative in the presence
    of tight cash flow so the allocation engine can retry with small tweaks.
    """

    def decide(self, snapshot: PlanningSnapshot, retry_count: int = 0) -> StrategyDecision:
        preference = snapshot.request.preferences.strategy_preference
        debt_framework = snapshot.request.preferences.debt_focus
        monthly_discretionary = snapshot.monthly_discretionary_pre_strategy

        priority_order: List[str] = [
            "mandatory_expenses",
            "minimum_debt",
            "starter_emergency_fund",
            "retirement_match",
            "high_priority_goals",
            "extra_debt",
            "full_emergency_fund",
            "sinking_funds",
            "retirement_extra",
            "brokerage",
        ]
        savings_balance = {
            "emergency_fund_weight": money("0.30"),
            "debt_weight": money("0.30"),
            "goal_weight": money("0.20"),
            "retirement_weight": money("0.15"),
            "brokerage_weight": money("0.05"),
        }
        notes = [
            "Mandatory costs and debt minimums are funded before optional wealth-building buckets.",
        ]

        if preference == "conservative":
            savings_balance.update(
                {
                    "emergency_fund_weight": money("0.45"),
                    "debt_weight": money("0.30"),
                    "goal_weight": money("0.15"),
                    "retirement_weight": money("0.10"),
                    "brokerage_weight": money("0.00"),
                }
            )
            notes.append("Conservative strategy increases liquidity before long-term investing.")
        elif preference == "aggressive":
            savings_balance.update(
                {
                    "emergency_fund_weight": money("0.20"),
                    "debt_weight": money("0.35"),
                    "goal_weight": money("0.15"),
                    "retirement_weight": money("0.20"),
                    "brokerage_weight": money("0.10"),
                }
            )
            notes.append("Aggressive strategy increases payoff and investing allocations once basics are covered.")

        high_apr_debt_exists = any(debt.interest_rate >= money("12.0") for debt in snapshot.request.debts)
        if high_apr_debt_exists:
            priority_order.insert(priority_order.index("full_emergency_fund"), "high_interest_debt_focus")
            notes.append("High-interest debt is pulled forward in the waterfall because APR exceeds 12%.")
            debt_framework = "avalanche"

        if monthly_discretionary <= Decimal("0.00"):
            savings_balance.update(
                {
                    "emergency_fund_weight": money("0.00"),
                    "debt_weight": money("0.00"),
                    "goal_weight": money("0.00"),
                    "retirement_weight": money("0.00"),
                    "brokerage_weight": money("0.00"),
                }
            )
            notes.append("No discretionary cash available, so optional buckets are suspended.")

        if retry_count > 0:
            savings_balance["brokerage_weight"] = money("0.00")
            notes.append("Retry logic removes brokerage funding until the plan validates cleanly.")
        if retry_count > 1:
            savings_balance["retirement_weight"] = money("0.05")
            notes.append("Later retries reduce extra retirement contributions to preserve liquidity.")

        return StrategyDecision(
            priority_order=priority_order,
            decision_waterfall=priority_order[:],
            debt_framework=debt_framework,
            savings_investing_balance=savings_balance,
            strategic_notes=notes,
            iteration_notes=[],
        )

