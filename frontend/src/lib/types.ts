export type PlannerLineItem = {
  bucket: string;
  name: string;
  amount: number;
  reason: string;
  due_day?: number | null;
};

export type PlannerPayload = {
  user_name: string;
  objective: string;
  incomes: Array<{
    name: string;
    net_amount: number;
    frequency: string;
    pay_day?: number;
  }>;
  expenses: Array<{
    name: string;
    amount: number;
    frequency: string;
    category: string;
    is_essential?: boolean;
    due_day?: number;
  }>;
  debts: Array<{
    name: string;
    current_balance: number;
    interest_rate: number;
    minimum_payment: number;
    due_day?: number;
  }>;
  accounts: Array<{
    name: string;
    account_type: string;
    balance: number;
    is_liquid?: boolean;
    is_tax_advantaged?: boolean;
  }>;
  goals: Array<{
    name: string;
    goal_type: string;
    target_amount: number;
    current_amount?: number;
    priority?: number;
  }>;
  preferences?: {
    strategy_preference?: string;
    debt_focus?: string;
    target_emergency_months?: number;
    brokerage_enabled?: boolean;
    wants_employer_match?: boolean;
    employer_match_rate?: number;
    employer_match_cap_percent?: number;
  };
};

export type PlannerResponse = {
  objective: string;
  stages?: Array<{ stage: string; status: string; details: string }>;
  iterations?: Array<Record<string, unknown>>;
  final_monthly_plan: PlannerLineItem[];
  per_paycheck_plan: Array<{
    paycheck_index: number;
    expected_income: number;
    remaining_cash: number;
    allocations: PlannerLineItem[];
  }>;
  debt_payoff_summary: {
    recommended_framework: string;
    payoff_order: string[];
    estimated_payoff_months: number;
    estimated_interest_cost: number;
    interest_saved_vs_alternative: number;
    unsustainable_debt_load: boolean;
    notes: string[];
    comparison?: Record<string, unknown>;
  };
  savings_investing_summary: {
    emergency_fund_target: number;
    emergency_fund_gap: number;
    emergency_fund_monthly_recommendation: number;
    retirement_recommendation: number;
    brokerage_recommendation: number;
    sinking_funds: Array<Record<string, unknown>>;
    short_term_goals: Array<Record<string, unknown>>;
    notes: string[];
  };
  risk_assessment: {
    validation_failures: Array<{ code: string; message: string; severity?: string; stage?: string }>;
    validation_warnings: string[];
    fragility_risks: string[];
    behavioral_risks: string[];
  };
  financial_stability_report: {
    liquidity_months: number;
    net_worth: number;
    debt_to_income_warning: boolean;
    buffer_present: boolean;
  };
  suggested_next_iteration_roadmap: string[];
  logs?: Array<Record<string, unknown>>;
};
