import { demoPayload } from "@/lib/demo-payload";
import type { PlannerPayload } from "@/lib/types";

export type IntakeFormState = {
  userName: string;
  objective: string;
  primaryIncome: string;
  sideIncome: string;
  rent: string;
  utilities: string;
  groceries: string;
  insurance: string;
  phone: string;
  transport: string;
  lifestyle: string;
  creditCardBalance: string;
  creditCardApr: string;
  creditCardMinimum: string;
  studentLoanBalance: string;
  studentLoanApr: string;
  studentLoanMinimum: string;
  checkingBalance: string;
  savingsBalance: string;
  retirementBalance: string;
  sinkingFundName: string;
  sinkingFundTarget: string;
  sinkingFundCurrent: string;
  shortTermGoalName: string;
  shortTermGoalTarget: string;
  shortTermGoalCurrent: string;
  strategyPreference: "conservative" | "balanced" | "aggressive";
  debtFocus: "avalanche" | "snowball";
  emergencyMonths: string;
  brokerageEnabled: boolean;
  wantsEmployerMatch: boolean;
  employerMatchRate: string;
  employerMatchCapPercent: string;
};

export function createDemoFormState(): IntakeFormState {
  const incomeByName = Object.fromEntries(
    demoPayload.incomes.map((income) => [String(income.name), String(income.net_amount)])
  );
  const expenseByName = Object.fromEntries(
    demoPayload.expenses.map((expense) => [String(expense.name), String(expense.amount)])
  );
  const debtByName = Object.fromEntries(
    demoPayload.debts.map((debt) => [String(debt.name), debt])
  );
  const accountByName = Object.fromEntries(
    demoPayload.accounts.map((account) => [String(account.name), account])
  );
  const goalsByType = Object.fromEntries(
    demoPayload.goals.map((goal) => [String(goal.goal_type), goal])
  );
  const preferences = demoPayload.preferences ?? {};

  return {
    userName: String(demoPayload.user_name),
    objective: String(demoPayload.objective),
    primaryIncome: incomeByName["Primary Salary"] ?? "0",
    sideIncome: incomeByName["Freelance"] ?? "0",
    rent: expenseByName["Rent"] ?? "0",
    utilities: expenseByName["Utilities"] ?? "0",
    groceries: expenseByName["Groceries"] ?? "0",
    insurance: expenseByName["Insurance"] ?? "0",
    phone: expenseByName["Phone"] ?? "0",
    transport: expenseByName["Transit"] ?? "0",
    lifestyle: expenseByName["Gym"] ?? "0",
    creditCardBalance: String(debtByName["Credit Card"]?.current_balance ?? 0),
    creditCardApr: String(debtByName["Credit Card"]?.interest_rate ?? 0),
    creditCardMinimum: String(debtByName["Credit Card"]?.minimum_payment ?? 0),
    studentLoanBalance: String(debtByName["Student Loan"]?.current_balance ?? 0),
    studentLoanApr: String(debtByName["Student Loan"]?.interest_rate ?? 0),
    studentLoanMinimum: String(debtByName["Student Loan"]?.minimum_payment ?? 0),
    checkingBalance: String(accountByName["Checking"]?.balance ?? 0),
    savingsBalance: String(accountByName["Savings"]?.balance ?? 0),
    retirementBalance: String(accountByName["401k"]?.balance ?? 0),
    sinkingFundName: String(goalsByType["sinking_fund"]?.name ?? "Sinking Fund"),
    sinkingFundTarget: String(goalsByType["sinking_fund"]?.target_amount ?? 0),
    sinkingFundCurrent: String(goalsByType["sinking_fund"]?.current_amount ?? 0),
    shortTermGoalName: String(goalsByType["short_term"]?.name ?? "Short-Term Goal"),
    shortTermGoalTarget: String(goalsByType["short_term"]?.target_amount ?? 0),
    shortTermGoalCurrent: String(goalsByType["short_term"]?.current_amount ?? 0),
    strategyPreference: (preferences.strategy_preference as IntakeFormState["strategyPreference"]) ?? "balanced",
    debtFocus: (preferences.debt_focus as IntakeFormState["debtFocus"]) ?? "avalanche",
    emergencyMonths: String(preferences.target_emergency_months ?? 3),
    brokerageEnabled: Boolean(preferences.brokerage_enabled ?? true),
    wantsEmployerMatch: Boolean(preferences.wants_employer_match ?? false),
    employerMatchRate: String(preferences.employer_match_rate ?? 0),
    employerMatchCapPercent: String(preferences.employer_match_cap_percent ?? 0)
  };
}

function numberValue(value: string): number {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : 0;
}

export function formStateToPayload(state: IntakeFormState): PlannerPayload {
  return {
    user_name: state.userName,
    objective: state.objective,
    incomes: [
      {
        name: "Primary Salary",
        net_amount: numberValue(state.primaryIncome),
        frequency: "semimonthly",
        pay_day: 1
      },
      {
        name: "Freelance",
        net_amount: numberValue(state.sideIncome),
        frequency: "monthly",
        pay_day: 20
      }
    ].filter((income) => income.net_amount > 0),
    expenses: [
      { name: "Rent", amount: numberValue(state.rent), frequency: "monthly", category: "housing", is_essential: true, due_day: 1 },
      { name: "Utilities", amount: numberValue(state.utilities), frequency: "monthly", category: "housing", is_essential: true, due_day: 12 },
      { name: "Groceries", amount: numberValue(state.groceries), frequency: "monthly", category: "food", is_essential: true, due_day: 16 },
      { name: "Insurance", amount: numberValue(state.insurance), frequency: "monthly", category: "insurance", is_essential: true, due_day: 18 },
      { name: "Phone", amount: numberValue(state.phone), frequency: "monthly", category: "utilities", is_essential: true, due_day: 24 },
      { name: "Transport", amount: numberValue(state.transport), frequency: "monthly", category: "transportation", is_essential: true, due_day: 25 },
      { name: "Lifestyle", amount: numberValue(state.lifestyle), frequency: "monthly", category: "lifestyle", is_essential: false, due_day: 26 }
    ].filter((expense) => expense.amount > 0),
    debts: [
      {
        name: "Credit Card",
        current_balance: numberValue(state.creditCardBalance),
        interest_rate: numberValue(state.creditCardApr),
        minimum_payment: numberValue(state.creditCardMinimum),
        due_day: 20
      },
      {
        name: "Student Loan",
        current_balance: numberValue(state.studentLoanBalance),
        interest_rate: numberValue(state.studentLoanApr),
        minimum_payment: numberValue(state.studentLoanMinimum),
        due_day: 28
      }
    ].filter((debt) => debt.current_balance > 0),
    accounts: [
      { name: "Checking", account_type: "checking", balance: numberValue(state.checkingBalance), is_liquid: true },
      { name: "Savings", account_type: "savings", balance: numberValue(state.savingsBalance), is_liquid: true },
      { name: "401k", account_type: "retirement", balance: numberValue(state.retirementBalance), is_liquid: false, is_tax_advantaged: true }
    ],
    goals: [
      {
        name: state.sinkingFundName,
        goal_type: "sinking_fund",
        target_amount: numberValue(state.sinkingFundTarget),
        current_amount: numberValue(state.sinkingFundCurrent),
        priority: 2
      },
      {
        name: state.shortTermGoalName,
        goal_type: "short_term",
        target_amount: numberValue(state.shortTermGoalTarget),
        current_amount: numberValue(state.shortTermGoalCurrent),
        priority: 3
      }
    ].filter((goal) => goal.name.trim() && goal.target_amount > 0),
    preferences: {
      strategy_preference: state.strategyPreference,
      debt_focus: state.debtFocus,
      target_emergency_months: numberValue(state.emergencyMonths),
      brokerage_enabled: state.brokerageEnabled,
      wants_employer_match: state.wantsEmployerMatch,
      employer_match_rate: numberValue(state.employerMatchRate),
      employer_match_cap_percent: numberValue(state.employerMatchCapPercent)
    }
  };
}
