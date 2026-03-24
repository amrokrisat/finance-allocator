"""Verification agent for generated plans."""

from __future__ import annotations

from decimal import Decimal
from typing import List

from app.models.financial import AllocationPlan, FailureReport, PlanningSnapshot, ValidationResult


class TestingAgent:
    """Validates the output plan against basic financial safety checks."""

    def validate(self, snapshot: PlanningSnapshot, plan: AllocationPlan) -> ValidationResult:
        failures: List[FailureReport] = []
        warnings: List[str] = []

        if plan.monthly_allocated_total > plan.monthly_income_total:
            failures.append(
                FailureReport(
                    code="OVER_ALLOCATED",
                    severity="high",
                    message="Monthly allocations exceed net income.",
                    stage="allocation",
                )
            )

        mandatory_names = {expense.name for expense in snapshot.request.expenses if expense.is_essential}
        funded_mandatory = {
            allocation.name for allocation in plan.monthly_allocations if allocation.bucket == "mandatory_expense"
        }
        missing_expense_funding = mandatory_names - funded_mandatory
        if missing_expense_funding:
            failures.append(
                FailureReport(
                    code="MANDATORY_NOT_FUNDED",
                    severity="high",
                    message=f"Mandatory expenses missing funding: {sorted(missing_expense_funding)}",
                    stage="allocation",
                )
            )

        if snapshot.monthly_discretionary_pre_strategy < Decimal("0.00"):
            failures.append(
                FailureReport(
                    code="IMPOSSIBLE_BUDGET",
                    severity="high",
                    message="Core obligations exceed income before optional goals are considered.",
                    stage="planning",
                )
            )

        negative_paychecks = [check.paycheck_index for check in plan.per_paycheck_allocations if check.remaining_cash < 0]
        if negative_paychecks:
            failures.append(
                FailureReport(
                    code="CASH_TIMING_FAILURE",
                    severity="medium",
                    message=f"Paycheck timing fails in pay periods: {negative_paychecks}",
                    stage="allocation",
                )
            )

        if plan.monthly_unallocated_cash > Decimal("0.00"):
            warnings.append("Plan leaves some income as a cash buffer instead of fully deploying it.")

        return ValidationResult(
            passed=not failures,
            failures=failures,
            warnings=warnings,
        )
