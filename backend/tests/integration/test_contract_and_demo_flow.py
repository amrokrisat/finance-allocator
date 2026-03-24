import unittest

from app.api.planner import build_financial_plan
from app.sample_data import sample_planning_payload


class ContractAndDemoFlowTests(unittest.TestCase):
    def test_backend_response_contains_frontend_consumed_fields(self) -> None:
        result = build_financial_plan(sample_planning_payload())

        self.assertIn("objective", result)
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
        self.assertIn("short_term_goals", result["savings_investing_summary"])

    def test_seeded_demo_totals_and_funding_priority_are_consistent(self) -> None:
        result = build_financial_plan(sample_planning_payload())

        monthly_total = round(sum(item["amount"] for item in result["final_monthly_plan"]), 2)
        paycheck_total = round(sum(item["expected_income"] for item in result["per_paycheck_plan"]), 2)
        mandatory_and_minimums = [
            item for item in result["final_monthly_plan"] if item["bucket"] in {"mandatory_expense", "debt_minimum"}
        ]

        self.assertEqual(monthly_total, paycheck_total)
        self.assertGreater(len(mandatory_and_minimums), 0)
        first_optional_index = next(
            index
            for index, item in enumerate(result["final_monthly_plan"])
            if item["bucket"] not in {"mandatory_expense", "flexible_expense", "debt_minimum"}
        )
        self.assertTrue(
            all(
                item["bucket"] in {"mandatory_expense", "flexible_expense", "debt_minimum"}
                for item in result["final_monthly_plan"][:first_optional_index]
            )
        )


if __name__ == "__main__":
    unittest.main()
