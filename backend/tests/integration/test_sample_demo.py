import unittest

from app.api.planner import build_financial_plan
from app.sample_data import sample_planning_payload


class SampleDemoTests(unittest.TestCase):
    def test_sample_profile_produces_visible_monthly_and_paycheck_plans(self) -> None:
        result = build_financial_plan(sample_planning_payload())

        self.assertGreater(len(result["final_monthly_plan"]), 0)
        self.assertGreater(len(result["per_paycheck_plan"]), 0)
        self.assertTrue(any(item["bucket"] == "mandatory_expense" for item in result["final_monthly_plan"]))
        self.assertIn("debt_payoff_summary", result)
        self.assertIn("savings_investing_summary", result)
        self.assertIn("risk_assessment", result)


if __name__ == "__main__":
    unittest.main()
