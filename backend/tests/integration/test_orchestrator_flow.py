import unittest

from app.api.planner import build_financial_plan


class OrchestratorFlowTests(unittest.TestCase):
    def test_full_pipeline_returns_required_sections(self) -> None:
        payload = {
            "user_name": "Avery",
            "objective": "Create a monthly action plan that improves liquidity and pays off debt.",
            "incomes": [
                {"name": "Salary", "net_amount": 2800, "frequency": "semimonthly", "pay_day": 1},
            ],
            "expenses": [
                {"name": "Rent", "amount": 1400, "frequency": "monthly", "category": "housing", "is_essential": True, "due_day": 1},
                {"name": "Utilities", "amount": 200, "frequency": "monthly", "category": "housing", "is_essential": True, "due_day": 10},
                {"name": "Groceries", "amount": 450, "frequency": "monthly", "category": "food", "is_essential": True, "due_day": 18},
            ],
            "debts": [
                {"name": "Card", "current_balance": 3500, "interest_rate": 21.5, "minimum_payment": 110, "due_day": 22},
            ],
            "accounts": [
                {"name": "Checking", "account_type": "checking", "balance": 800, "is_liquid": True},
                {"name": "Emergency Savings", "account_type": "savings", "balance": 300, "is_liquid": True},
            ],
            "goals": [
                {"name": "Travel", "goal_type": "short_term", "target_amount": 1200, "current_amount": 100, "priority": 3},
            ],
            "preferences": {
                "strategy_preference": "balanced",
                "debt_focus": "avalanche",
                "target_emergency_months": 3,
            },
        }

        result = build_financial_plan(payload)

        self.assertIn("final_monthly_plan", result)
        self.assertIn("per_paycheck_plan", result)
        self.assertIn("debt_payoff_summary", result)
        self.assertIn("savings_investing_summary", result)
        self.assertIn("risk_assessment", result)
        self.assertIn("financial_stability_report", result)
        self.assertIn("suggested_next_iteration_roadmap", result)
        self.assertIn("plan_overview", result)
        self.assertIn("why_this_plan", result)
        self.assertIn("first_30_days", result)
        self.assertIn("scenario_levers", result)
        self.assertTrue(result["why_this_plan"])
        self.assertTrue(result["first_30_days"])


if __name__ == "__main__":
    unittest.main()
