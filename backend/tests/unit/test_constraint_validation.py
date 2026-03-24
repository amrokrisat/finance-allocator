import unittest

from app.core.finance import money
from app.models.financial import Expense, IncomeSource, PlanningRequest, Preferences
from app.services.intake.agent import IntakeFinancialProfileAgent


class ConstraintValidationTests(unittest.TestCase):
    def test_intake_flags_negative_discretionary_constraint(self) -> None:
        request = PlanningRequest(
            objective="Survive the month",
            incomes=[IncomeSource(name="Salary", net_amount=money(1800), frequency="monthly", pay_day=1)],
            expenses=[
                Expense(name="Rent", amount=money(1400), frequency="monthly", category="housing", due_day=1),
                Expense(name="Groceries", amount=money(500), frequency="monthly", category="food", due_day=15),
            ],
            debts=[],
            accounts=[],
            goals=[],
        )

        snapshot = IntakeFinancialProfileAgent().process(request)

        self.assertIn("Core obligations exceed current monthly income.", snapshot.constraints)

    def test_intake_flags_missing_employer_match_inputs(self) -> None:
        request = PlanningRequest(
            objective="Maximize match",
            incomes=[IncomeSource(name="Salary", net_amount=money(4000), frequency="monthly", pay_day=1)],
            expenses=[Expense(name="Rent", amount=money(1500), frequency="monthly", category="housing", due_day=1)],
            debts=[],
            accounts=[],
            goals=[],
            preferences=Preferences(wants_employer_match=True),
        )

        snapshot = IntakeFinancialProfileAgent().process(request)

        self.assertIn(
            "Employer match cap percent is required when employer match is enabled.",
            snapshot.missing_requirements,
        )


if __name__ == "__main__":
    unittest.main()
