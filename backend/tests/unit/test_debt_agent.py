import unittest

from app.core.finance import money
from app.models.financial import Debt, PlanningRequest, Preferences
from app.services.debt.agent import DebtOptimizationAgent
from app.services.intake.agent import IntakeFinancialProfileAgent


class DebtOptimizationAgentTests(unittest.TestCase):
    def test_avalanche_recommended_for_high_interest_debt(self) -> None:
        request = PlanningRequest(
            objective="Pay off debt efficiently",
            incomes=[],
            expenses=[],
            debts=[
                Debt(name="Card A", current_balance=money(5000), interest_rate=money(24.9), minimum_payment=money(150)),
                Debt(name="Card B", current_balance=money(2500), interest_rate=money(9.9), minimum_payment=money(85)),
            ],
            accounts=[],
            goals=[],
        )
        snapshot = IntakeFinancialProfileAgent().process(request)
        plan = DebtOptimizationAgent().analyze(snapshot, money(300))
        self.assertEqual(plan.recommended_framework, "avalanche")
        self.assertGreaterEqual(plan.interest_saved_vs_alternative, money(0))

    def test_snowball_can_be_recommended_when_cost_is_close_and_behavioral_benefit_is_high(self) -> None:
        request = PlanningRequest(
            objective="Build momentum while paying off debt",
            incomes=[],
            expenses=[],
            debts=[
                Debt(name="Card A", current_balance=money(700), interest_rate=money(22.0), minimum_payment=money(40)),
                Debt(name="Card B", current_balance=money(650), interest_rate=money(18.0), minimum_payment=money(35)),
                Debt(name="Card C", current_balance=money(2400), interest_rate=money(23.0), minimum_payment=money(90)),
            ],
            accounts=[],
            goals=[],
            preferences=Preferences(debt_focus="snowball"),
        )
        snapshot = IntakeFinancialProfileAgent().process(request)
        plan = DebtOptimizationAgent().analyze(snapshot, money(250))

        self.assertEqual(plan.recommended_framework, "snowball")
        self.assertEqual(plan.payoff_order[0], "Card B")

    def test_unsustainable_debt_load_is_flagged(self) -> None:
        request = PlanningRequest(
            objective="Get debt under control",
            incomes=[],
            expenses=[],
            debts=[
                Debt(name="Loan A", current_balance=money(60000), interest_rate=money(9.0), minimum_payment=money(900)),
                Debt(name="Loan B", current_balance=money(30000), interest_rate=money(12.0), minimum_payment=money(450)),
            ],
            accounts=[],
            goals=[],
        )
        snapshot = IntakeFinancialProfileAgent().process(request)
        snapshot.monthly_income_total = money(2500)
        snapshot.monthly_minimum_debt_total = money(1350)
        snapshot.liabilities_total = money(90000)

        plan = DebtOptimizationAgent().analyze(snapshot, money(100))

        self.assertTrue(plan.unsustainable_debt_load)


if __name__ == "__main__":
    unittest.main()
