-- Proposed Postgres schema for the finance allocation MVP.
-- Assumptions:
-- 1. The planner operates on monthly-normalized values even if the user enters other frequencies.
-- 2. We store user-entered source records and computed allocation runs separately.
-- 3. We keep the schema simple for MVP and avoid full accounting-style ledgers.

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    display_name TEXT,
    monthly_housing_target NUMERIC(12, 2),
    emergency_months_target NUMERIC(4, 2) NOT NULL DEFAULT 3.0,
    strategy_preference TEXT NOT NULL DEFAULT 'balanced',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CHECK (strategy_preference IN ('conservative', 'balanced', 'aggressive'))
);

CREATE TABLE income_sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    gross_amount NUMERIC(12, 2),
    net_amount NUMERIC(12, 2) NOT NULL,
    frequency TEXT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CHECK (frequency IN ('weekly', 'biweekly', 'semimonthly', 'monthly', 'annual'))
);

CREATE TABLE expenses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    amount NUMERIC(12, 2) NOT NULL,
    frequency TEXT NOT NULL,
    category TEXT NOT NULL,
    is_essential BOOLEAN NOT NULL DEFAULT TRUE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CHECK (frequency IN ('weekly', 'biweekly', 'monthly', 'quarterly', 'annual'))
);

CREATE TABLE accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    account_type TEXT NOT NULL,
    balance NUMERIC(12, 2) NOT NULL DEFAULT 0,
    is_tax_advantaged BOOLEAN NOT NULL DEFAULT FALSE,
    is_liquid BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CHECK (account_type IN (
        'checking',
        'savings',
        'emergency_fund',
        'retirement',
        'brokerage',
        'debt',
        'other'
    ))
);

CREATE TABLE debts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    debt_type TEXT NOT NULL,
    current_balance NUMERIC(12, 2) NOT NULL,
    interest_rate NUMERIC(6, 3) NOT NULL,
    minimum_payment NUMERIC(12, 2) NOT NULL,
    due_day_of_month INTEGER,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CHECK (interest_rate >= 0),
    CHECK (due_day_of_month IS NULL OR due_day_of_month BETWEEN 1 AND 31)
);

CREATE TABLE goals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    goal_type TEXT NOT NULL,
    target_amount NUMERIC(12, 2) NOT NULL,
    current_amount NUMERIC(12, 2) NOT NULL DEFAULT 0,
    target_date DATE,
    priority INTEGER NOT NULL DEFAULT 3,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CHECK (goal_type IN (
        'emergency_fund',
        'sinking_fund',
        'short_term',
        'retirement',
        'brokerage'
    )),
    CHECK (priority BETWEEN 1 AND 5)
);

CREATE TABLE strategy_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    config_json JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE allocation_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    strategy_config_id UUID REFERENCES strategy_configs(id) ON DELETE SET NULL,
    monthly_income_total NUMERIC(12, 2) NOT NULL,
    monthly_expense_total NUMERIC(12, 2) NOT NULL,
    monthly_minimum_debt_total NUMERIC(12, 2) NOT NULL,
    monthly_discretionary_total NUMERIC(12, 2) NOT NULL,
    status TEXT NOT NULL DEFAULT 'completed',
    explanation_summary JSONB NOT NULL DEFAULT '{}'::JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CHECK (status IN ('completed', 'incomplete', 'error'))
);

CREATE TABLE allocation_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    allocation_run_id UUID NOT NULL REFERENCES allocation_runs(id) ON DELETE CASCADE,
    bucket_type TEXT NOT NULL,
    bucket_name TEXT NOT NULL,
    recommended_amount NUMERIC(12, 2) NOT NULL,
    rationale_code TEXT NOT NULL,
    metadata_json JSONB NOT NULL DEFAULT '{}'::JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CHECK (bucket_type IN (
        'expense',
        'debt_minimum',
        'debt_extra',
        'emergency_fund',
        'sinking_fund',
        'short_term_goal',
        'retirement',
        'brokerage',
        'leftover_cash'
    ))
);

CREATE INDEX idx_income_sources_user_id ON income_sources(user_id);
CREATE INDEX idx_expenses_user_id ON expenses(user_id);
CREATE INDEX idx_accounts_user_id ON accounts(user_id);
CREATE INDEX idx_debts_user_id ON debts(user_id);
CREATE INDEX idx_goals_user_id ON goals(user_id);
CREATE INDEX idx_allocation_runs_user_id ON allocation_runs(user_id);
CREATE INDEX idx_allocation_results_run_id ON allocation_results(allocation_run_id);
