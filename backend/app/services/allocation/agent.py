"""Allocation engine agent."""

from __future__ import annotations

from decimal import Decimal
from typing import Dict, List, Optional

from app.core.finance import clamp_non_negative, money, to_monthly
from app.models.financial import (
    AllocationLine,
    AllocationPlan,
    DebtPlan,
    PaycheckAllocation,
    PlanningSnapshot,
    SavingsInvestmentPlan,
    StrategyDecision,
)


class AllocationEngineAgent:
    """Turns strategy into monthly and per-paycheck allocations."""

    def build_plan(
        self,
        snapshot: PlanningSnapshot,
        strategy: StrategyDecision,
        debt_plan: DebtPlan,
        savings_plan: SavingsInvestmentPlan,
    ) -> AllocationPlan:
        allocations: List[AllocationLine] = []

        for expense in snapshot.request.expenses:
            allocations.append(
                AllocationLine(
                    bucket="mandatory_expense" if expense.is_essential else "flexible_expense",
                    name=expense.name,
                    amount=to_monthly(expense.amount, expense.frequency),
                    reason="Mandatory living expense" if expense.is_essential else "Flexible living expense",
                    due_day=expense.due_day,
                )
            )

        for debt in snapshot.request.debts:
            allocations.append(
                AllocationLine(
                    bucket="debt_minimum",
                    name=debt.name,
                    amount=debt.minimum_payment,
                    reason="Required debt minimum payment",
                    due_day=debt.due_day,
                )
            )

        monthly_income = snapshot.monthly_income_total
        used_cash = sum(line.amount for line in allocations)
        discretionary = clamp_non_negative(monthly_income - used_cash)

        extra_debt_budget = min(
            discretionary,
            money(discretionary * strategy.savings_investing_balance.get("debt_weight", Decimal("0.00"))),
        )
        if extra_debt_budget > Decimal("0.00") and debt_plan.payoff_order:
            allocations.append(
                AllocationLine(
                    bucket="debt_extra",
                    name=debt_plan.payoff_order[0],
                    amount=extra_debt_budget,
                    reason=f"Extra debt payment using {debt_plan.recommended_framework}",
                )
            )

        optional_after_debt = clamp_non_negative(discretionary - extra_debt_budget)
        if savings_plan.emergency_fund_monthly_recommendation > Decimal("0.00"):
            allocations.append(
                AllocationLine(
                    bucket="emergency_fund",
                    name="Emergency Fund",
                    amount=savings_plan.emergency_fund_monthly_recommendation,
                    reason="Liquidity reserve contribution",
                )
            )
        if savings_plan.retirement_recommendation > Decimal("0.00"):
            allocations.append(
                AllocationLine(
                    bucket="retirement",
                    name="Retirement",
                    amount=min(
                        savings_plan.retirement_recommendation,
                        clamp_non_negative(optional_after_debt - savings_plan.emergency_fund_monthly_recommendation),
                    ),
                    reason="Retirement contribution based on strategy and employer match",
                )
            )
        for goal in savings_plan.short_term_goal_recommendations:
            if goal["recommended_monthly"] > Decimal("0.00"):
                allocations.append(
                    AllocationLine(
                        bucket="short_term_goal",
                        name=goal["name"],
                        amount=goal["recommended_monthly"],
                        reason="Short-term goal contribution",
                    )
                )
        for goal in savings_plan.sinking_funds:
            if goal["recommended_monthly"] > Decimal("0.00"):
                allocations.append(
                    AllocationLine(
                        bucket="sinking_fund",
                        name=goal["name"],
                        amount=goal["recommended_monthly"],
                        reason="Sinking fund contribution",
                    )
                )
        remaining_before_brokerage = clamp_non_negative(monthly_income - sum(line.amount for line in allocations))
        brokerage_amount = min(savings_plan.brokerage_recommendation, remaining_before_brokerage)
        if brokerage_amount > Decimal("0.00"):
            allocations.append(
                AllocationLine(
                    bucket="brokerage",
                    name="Brokerage",
                    amount=brokerage_amount,
                    reason="Taxable investing after nearer-term obligations",
                )
            )

        monthly_allocated = money(sum(line.amount for line in allocations))
        unallocated = clamp_non_negative(monthly_income - monthly_allocated)
        if unallocated > Decimal("0.00"):
            allocations.append(
                AllocationLine(
                    bucket="buffer",
                    name="Cash Buffer",
                    amount=unallocated,
                    reason="Preserved as slack to reduce overdraft risk",
                )
            )
            monthly_allocated = money(sum(line.amount for line in allocations))
            unallocated = clamp_non_negative(monthly_income - monthly_allocated)

        paychecks = self._allocate_per_paycheck(snapshot, allocations)
        adjustments = []
        if any(paycheck.remaining_cash < Decimal("0.00") for paycheck in paychecks):
            adjustments.append("Paycheck-level cash timing remains tight; retry may reduce late-month optional funding.")

        return AllocationPlan(
            monthly_allocations=allocations,
            per_paycheck_allocations=paychecks,
            monthly_income_total=monthly_income,
            monthly_allocated_total=monthly_allocated,
            monthly_unallocated_cash=unallocated,
            iteration_adjustments=adjustments,
        )

    def _allocate_per_paycheck(
        self,
        snapshot: PlanningSnapshot,
        monthly_allocations: List[AllocationLine],
    ) -> List[PaycheckAllocation]:
        paycheck_schedule = self._paycheck_schedule(snapshot)
        paychecks = [
            PaycheckAllocation(
                paycheck_index=index + 1,
                expected_income=income,
                allocations=[],
                remaining_cash=income,
            )
            for index, (_, income) in enumerate(paycheck_schedule)
        ]

        for line in sorted(monthly_allocations, key=lambda item: item.due_day or 28):
            if line.bucket == "buffer":
                # A buffer is intentionally unassigned cash. Scheduling it like a bill
                # would create a fake timing failure in the paycheck view.
                continue
            target = self._target_paycheck_index(line.due_day, len(paychecks))
            assigned = self._assign_to_paycheck(paychecks, target, line)
            if not assigned and paychecks:
                paychecks[-1].allocations.append(line)
                paychecks[-1].remaining_cash = money(paychecks[-1].remaining_cash - line.amount)

        return paychecks

    def _paycheck_schedule(self, snapshot: PlanningSnapshot) -> List[tuple]:
        schedule: List[tuple] = []
        for income in snapshot.request.incomes:
            if income.frequency == "monthly":
                schedule.append((income.pay_day or 1, income.net_amount))
            elif income.frequency in {"semimonthly", "biweekly"}:
                half = money(income.net_amount)
                schedule.append((income.pay_day or 1, half))
                schedule.append((15 if (income.pay_day or 1) < 15 else 28, half))
            elif income.frequency == "weekly":
                quarter = money(income.net_amount)
                schedule.extend([(1, quarter), (8, quarter), (15, quarter), (22, quarter)])
            else:
                monthly_total = to_monthly(income.net_amount, income.frequency)
                schedule.append((1, monthly_total))
        schedule.sort(key=lambda item: item[0])
        if not schedule:
            schedule = [(1, Decimal("0.00"))]
        return schedule

    def _target_paycheck_index(self, due_day: Optional[int], count: int) -> int:
        if count <= 1:
            return 0
        due_day = due_day or 28
        if due_day <= 10:
            return 0
        if due_day <= 20:
            return min(1, count - 1)
        return count - 1

    def _assign_to_paycheck(
        self,
        paychecks: List[PaycheckAllocation],
        preferred_index: int,
        line: AllocationLine,
    ) -> bool:
        for index in range(preferred_index + 1):
            paycheck = paychecks[index]
            if paycheck.remaining_cash >= line.amount:
                paycheck.allocations.append(line)
                paycheck.remaining_cash = money(paycheck.remaining_cash - line.amount)
                return True
        return False
