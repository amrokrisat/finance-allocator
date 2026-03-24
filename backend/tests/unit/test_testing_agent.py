import unittest

from app.core.finance import money
from app.models.financial import Expense, IncomeSource, PlanningRequest
from app.services.intake.agent import IntakeFinancialProfileAgent
from app.services.orchestration.agent import OrchestratorAgent


class TestingAgentBehaviorTests(unittest.TestCase):
    def test_impossible_budget_is_flagged(self) -> None:
        request = PlanningRequest(
            objective="Survive the month",
            incomes=[IncomeSource(name="Salary", net_amount=money(1000), frequency="monthly", pay_day=1)],
            expenses=[
                Expense(name="Rent", amount=money(1200), frequency="monthly", category="housing", due_day=1),
                Expense(name="Food", amount=money(200), frequency="monthly", category="food", due_day=12),
            ],
            debts=[],
            accounts=[],
            goals=[],
        )
        summary = OrchestratorAgent().build_plan(request)
        codes = {failure["code"] for failure in summary.risk_assessment["validation_failures"]}
        self.assertIn("IMPOSSIBLE_BUDGET", codes)


if __name__ == "__main__":
    unittest.main()
