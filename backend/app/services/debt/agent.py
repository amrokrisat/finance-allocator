"""Debt optimization agent."""

from __future__ import annotations

from copy import deepcopy
from decimal import Decimal
from typing import Dict, List

from app.core.finance import clamp_non_negative, money, sum_money
from app.models.financial import Debt, DebtComparison, DebtPlan, PlanningSnapshot


class DebtOptimizationAgent:
    """Compares avalanche and snowball, then recommends a payoff order."""

    def analyze(self, snapshot: PlanningSnapshot, extra_payment_budget: Decimal) -> DebtPlan:
        avalanche = self._simulate(snapshot.request.debts, extra_payment_budget, "avalanche")
        snowball = self._simulate(snapshot.request.debts, extra_payment_budget, "snowball")
        preferred_framework = snapshot.request.preferences.debt_focus

        recommended = avalanche
        alternative = snowball
        notes = ["Avalanche is the default because it minimizes interest in most cases."]

        if (
            snowball.estimated_months <= avalanche.estimated_months + 1
            and snowball.total_interest <= avalanche.total_interest + money("100.00")
            and len(snapshot.request.debts) >= 3
        ):
            recommended = snowball
            alternative = avalanche
            notes.append("Snowball is close in cost and may be behaviorally easier to sustain.")
        elif preferred_framework == "snowball" and self._frameworks_are_close(avalanche, snowball):
            # We only honor the user preference when the efficiency tradeoff is
            # modest. This keeps the recommendation explainable and realistic.
            recommended = snowball
            alternative = avalanche
            notes.append("User preference for snowball is honored because the interest tradeoff is modest.")

        minimum_debt_total = snapshot.monthly_minimum_debt_total
        unsustainable = (
            minimum_debt_total > money(snapshot.monthly_income_total * money("0.35"))
            or snapshot.liabilities_total > money(snapshot.monthly_income_total * money("24"))
        )
        if unsustainable:
            notes.append("Debt load appears unsustainable relative to income; restructuring may be needed.")

        return DebtPlan(
            recommended_framework=recommended.framework,
            comparison={
                "avalanche": avalanche,
                "snowball": snowball,
            },
            payoff_order=recommended.payoff_order,
            estimated_payoff_months=recommended.estimated_months,
            estimated_interest_cost=recommended.total_interest,
            interest_saved_vs_alternative=money(alternative.total_interest - recommended.total_interest),
            unsustainable_debt_load=unsustainable,
            notes=notes,
        )

    def _frameworks_are_close(
        self,
        avalanche: DebtComparison,
        snowball: DebtComparison,
    ) -> bool:
        return (
            snowball.estimated_months <= avalanche.estimated_months + 2
            and snowball.total_interest <= avalanche.total_interest + money("150.00")
        )

    def _simulate(self, debts: List[Debt], extra_payment_budget: Decimal, framework: str) -> DebtComparison:
        if not debts:
            return DebtComparison(
                framework=framework,
                estimated_months=0,
                total_interest=money("0"),
                payoff_order=[],
            )

        working = deepcopy(debts)
        total_interest = Decimal("0.00")
        months = 0
        payoff_order: List[str] = []
        carry_extra = money(extra_payment_budget)

        while working and months < 600:
            months += 1
            working = [debt for debt in working if debt.current_balance > Decimal("0.00")]
            if not working:
                break
            if framework == "avalanche":
                working.sort(key=lambda debt: (-debt.interest_rate, debt.current_balance))
            else:
                working.sort(key=lambda debt: (debt.current_balance, -debt.interest_rate))

            month_extra = carry_extra
            for debt in working:
                monthly_rate = debt.interest_rate / Decimal("100") / Decimal("12")
                interest = money(debt.current_balance * monthly_rate)
                debt.current_balance = money(debt.current_balance + interest)
                total_interest += interest

                payment = debt.minimum_payment
                if debt is working[0]:
                    payment = money(payment + month_extra)

                actual_payment = min(payment, debt.current_balance)
                debt.current_balance = money(debt.current_balance - actual_payment)
                if debt.current_balance == Decimal("0.00") and debt.name not in payoff_order:
                    payoff_order.append(debt.name)
                    month_extra = money(month_extra + debt.minimum_payment)

        remaining_balances = sum_money(debt.current_balance for debt in working)
        if remaining_balances > Decimal("0.00"):
            months = 600

        return DebtComparison(
            framework=framework,
            estimated_months=months,
            total_interest=money(total_interest),
            payoff_order=payoff_order or [debt.name for debt in working],
        )
