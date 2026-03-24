import unittest

from app.core.finance import money
from app.models.financial import Account, Expense, IncomeSource, PlanningRequest, Preferences
from app.services.intake.agent import IntakeFinancialProfileAgent
from app.services.savings_investing.agent import SavingsInvestmentAgent


class SavingsInvestmentAgentTests(unittest.TestCase):
    def test_emergency_fund_target_and_gap_are_based_on_essential_expenses(self) -> None:
        request = PlanningRequest(
            objective="Build reserves",
            incomes=[IncomeSource(name="Salary", net_amount=money(4000), frequency="monthly", pay_day=1)],
            expenses=[
                Expense(name="Rent", amount=money(1500), frequency="monthly", category="housing", is_essential=True),
                Expense(name="Groceries", amount=money(500), frequency="monthly", category="food", is_essential=True),
                Expense(name="Streaming", amount=money(50), frequency="monthly", category="fun", is_essential=False),
            ],
            debts=[],
            accounts=[Account(name="Savings", account_type="savings", balance=money(600), is_liquid=True)],
            goals=[],
            preferences=Preferences(target_emergency_months=money("3.00")),
        )

        snapshot = IntakeFinancialProfileAgent().process(request)
        plan = SavingsInvestmentAgent().build(
            snapshot,
            {
                "emergency_fund_weight": money("0.50"),
                "goal_weight": money("0.20"),
                "retirement_weight": money("0.20"),
                "brokerage_weight": money("0.10"),
            },
            money(1000),
        )

        self.assertEqual(plan.emergency_fund_target, money(6000))
        self.assertEqual(plan.emergency_fund_gap, money(5400))
        self.assertEqual(plan.emergency_fund_monthly_recommendation, money(500))

    def test_emergency_contribution_is_capped_by_remaining_gap(self) -> None:
        request = PlanningRequest(
            objective="Finish emergency fund",
            incomes=[IncomeSource(name="Salary", net_amount=money(3000), frequency="monthly", pay_day=1)],
            expenses=[Expense(name="Rent", amount=money(1000), frequency="monthly", category="housing", is_essential=True)],
            debts=[],
            accounts=[Account(name="Savings", account_type="savings", balance=money(2900), is_liquid=True)],
            goals=[],
            preferences=Preferences(target_emergency_months=money("3.00")),
        )

        snapshot = IntakeFinancialProfileAgent().process(request)
        plan = SavingsInvestmentAgent().build(
            snapshot,
            {
                "emergency_fund_weight": money("1.00"),
                "goal_weight": money("0.00"),
                "retirement_weight": money("0.00"),
                "brokerage_weight": money("0.00"),
            },
            money(500),
        )

        self.assertEqual(plan.emergency_fund_target, money(3000))
        self.assertEqual(plan.emergency_fund_gap, money(100))
        self.assertEqual(plan.emergency_fund_monthly_recommendation, money(100))

    def test_brokerage_is_disabled_when_preference_disables_it(self) -> None:
        request = PlanningRequest(
            objective="Prioritize liquidity",
            incomes=[IncomeSource(name="Salary", net_amount=money(3000), frequency="monthly", pay_day=1)],
            expenses=[Expense(name="Rent", amount=money(1000), frequency="monthly", category="housing", is_essential=True)],
            debts=[],
            accounts=[Account(name="Savings", account_type="savings", balance=money(0), is_liquid=True)],
            goals=[],
            preferences=Preferences(brokerage_enabled=False),
        )

        snapshot = IntakeFinancialProfileAgent().process(request)
        plan = SavingsInvestmentAgent().build(
            snapshot,
            {
                "emergency_fund_weight": money("0.40"),
                "goal_weight": money("0.20"),
                "retirement_weight": money("0.20"),
                "brokerage_weight": money("0.20"),
            },
            money(1000),
        )

        self.assertEqual(plan.brokerage_recommendation, money(0))


if __name__ == "__main__":
    unittest.main()
