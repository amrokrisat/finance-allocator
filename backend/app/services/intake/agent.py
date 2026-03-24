"""Intake and planning-layer agent."""

from __future__ import annotations

from typing import List

from app.core.finance import clamp_non_negative, money, sum_money, to_monthly
from app.models.financial import PlanningRequest, PlanningSnapshot


class IntakeFinancialProfileAgent:
    """Normalizes raw financial data into planning summaries.

    The agent favors transparency over deep inference. When data is missing, it
    records the assumption rather than guessing aggressively.
    """

    def process(self, request: PlanningRequest) -> PlanningSnapshot:
        monthly_income_total = sum_money(
            to_monthly(income.net_amount, income.frequency) for income in request.incomes
        )
        monthly_expense_amounts = [to_monthly(expense.amount, expense.frequency) for expense in request.expenses]
        monthly_expense_total = sum_money(monthly_expense_amounts)
        monthly_essential_total = sum_money(
            to_monthly(expense.amount, expense.frequency)
            for expense in request.expenses
            if expense.is_essential
        )
        monthly_minimum_debt_total = sum_money(debt.minimum_payment for debt in request.debts)
        assets_total = sum_money(account.balance for account in request.accounts)
        liquid_assets_total = sum_money(account.balance for account in request.accounts if account.is_liquid)
        liabilities_total = sum_money(debt.current_balance for debt in request.debts)
        net_worth = money(assets_total - liabilities_total)
        monthly_discretionary = money(
            monthly_income_total - monthly_expense_total - monthly_minimum_debt_total
        )

        assumptions: List[str] = []
        constraints: List[str] = []
        missing_requirements: List[str] = []

        if not request.incomes:
            missing_requirements.append("At least one income source is required.")
        if not request.expenses:
            missing_requirements.append("Monthly expenses are required to build a realistic plan.")
        if any(expense.due_day is None for expense in request.expenses):
            assumptions.append("Expenses without a due day are treated as due near month-end.")
        if any(income.pay_day is None for income in request.incomes):
            assumptions.append("Income without a pay day is placed on a standard semi-monthly schedule.")
        if request.preferences.wants_employer_match and request.preferences.employer_match_cap_percent == money(0):
            missing_requirements.append("Employer match cap percent is required when employer match is enabled.")
        if monthly_discretionary < money(0):
            constraints.append("Core obligations exceed current monthly income.")
        if monthly_essential_total > money(monthly_income_total * money("0.8")):
            constraints.append("Essential expenses consume more than 80% of monthly income.")

        goals_summary = {
            "goal_count": len(request.goals),
            "high_priority_goals": [goal.name for goal in request.goals if goal.priority <= 2],
            "total_goal_gap": sum_money(
                clamp_non_negative(goal.target_amount - goal.current_amount) for goal in request.goals
            ),
        }
        financial_profile = {
            "user_name": request.user_name,
            "objective": request.objective,
            "income_sources": [income.name for income in request.incomes],
            "expense_categories": sorted({expense.category for expense in request.expenses}),
            "debt_count": len(request.debts),
            "account_count": len(request.accounts),
        }
        cash_flow_summary = {
            "monthly_income_total": monthly_income_total,
            "monthly_expense_total": monthly_expense_total,
            "monthly_minimum_debt_total": monthly_minimum_debt_total,
            "monthly_discretionary_pre_strategy": monthly_discretionary,
        }
        balance_sheet_snapshot = {
            "assets_total": assets_total,
            "liabilities_total": liabilities_total,
            "liquid_assets_total": liquid_assets_total,
            "net_worth": net_worth,
        }

        return PlanningSnapshot(
            request=request,
            monthly_income_total=monthly_income_total,
            monthly_expense_total=monthly_expense_total,
            monthly_essential_expense_total=monthly_essential_total,
            monthly_minimum_debt_total=monthly_minimum_debt_total,
            liquid_assets_total=liquid_assets_total,
            assets_total=assets_total,
            liabilities_total=liabilities_total,
            net_worth=net_worth,
            monthly_discretionary_pre_strategy=monthly_discretionary,
            financial_profile=financial_profile,
            cash_flow_summary=cash_flow_summary,
            balance_sheet_snapshot=balance_sheet_snapshot,
            goals_summary=goals_summary,
            assumptions=assumptions,
            constraints=constraints,
            missing_requirements=missing_requirements,
        )

