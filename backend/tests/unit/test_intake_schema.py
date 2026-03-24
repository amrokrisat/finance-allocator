import unittest

from app.schemas.planning import planning_request_from_dict


class PlanningSchemaTests(unittest.TestCase):
    def test_planning_request_parses_valid_payload(self) -> None:
        payload = {
            "objective": "Build a realistic monthly plan",
            "incomes": [{"name": "Salary", "net_amount": 2500, "frequency": "semimonthly", "pay_day": 1}],
            "expenses": [{"name": "Rent", "amount": 1200, "frequency": "monthly", "category": "housing", "due_day": 1}],
            "debts": [{"name": "Card", "current_balance": 500, "interest_rate": 19.9, "minimum_payment": 35, "due_day": 20}],
            "accounts": [{"name": "Checking", "account_type": "checking", "balance": 200, "is_liquid": True}],
            "goals": [{"name": "Trip", "goal_type": "short_term", "target_amount": 600, "current_amount": 100, "priority": 2}],
        }

        request = planning_request_from_dict(payload)

        self.assertEqual(request.objective, payload["objective"])
        self.assertEqual(request.incomes[0].frequency, "semimonthly")
        self.assertEqual(request.expenses[0].due_day, 1)
        self.assertEqual(request.goals[0].priority, 2)

    def test_invalid_frequency_is_rejected(self) -> None:
        payload = {
            "objective": "Build a realistic monthly plan",
            "incomes": [{"name": "Salary", "net_amount": 2500, "frequency": "daily"}],
            "expenses": [],
            "debts": [],
            "accounts": [],
            "goals": [],
        }

        with self.assertRaises(ValueError):
            planning_request_from_dict(payload)

    def test_negative_amount_is_rejected(self) -> None:
        payload = {
            "objective": "Build a realistic monthly plan",
            "incomes": [{"name": "Salary", "net_amount": -2500, "frequency": "monthly"}],
            "expenses": [],
            "debts": [],
            "accounts": [],
            "goals": [],
        }

        with self.assertRaises(ValueError):
            planning_request_from_dict(payload)


if __name__ == "__main__":
    unittest.main()
