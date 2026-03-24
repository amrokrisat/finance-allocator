# Finance Allocator MVP

Personal finance allocation system for deciding how to allocate income across monthly expenses, emergency savings, sinking funds, debt payoff, retirement contributions, taxable brokerage investing, and short-term goals.

This repo contains an implemented Python planning engine, backend test coverage, sample planning artifacts, and a minimal Next.js frontend.

## MVP Goals

- keep the first version simple and local-first
- prioritize explainable financial logic over UI polish
- avoid bank integrations
- keep the business logic modular
- test core financial calculations before expanding product scope

## Setup

### Backend

Requirements:

- Python 3.9+

Start the local planner API:

```bash
PYTHONPATH=backend python3 backend/app/server.py
```

The API serves:

- `POST /api/planner`
- `GET /health`

Run the backend demo:

```bash
PYTHONPATH=backend python3 backend/app/main.py
```

Generate the sample planning artifact:

```bash
PYTHONPATH=backend python3 backend/scripts/generate_sample_plan.py
```

This writes shared demo fixtures to:

- [sample_profile.json](/Users/amroalkrisat/Documents/cd%20finance-allocator/backend/output/sample_profile.json)
- [sample_plan.json](/Users/amroalkrisat/Documents/cd%20finance-allocator/backend/output/sample_plan.json)
- [sample-profile.json](/Users/amroalkrisat/Documents/cd%20finance-allocator/frontend/src/lib/fixtures/sample-profile.json)
- [sample-plan.json](/Users/amroalkrisat/Documents/cd%20finance-allocator/frontend/src/lib/fixtures/sample-plan.json)

Run backend tests:

```bash
PYTHONPATH=backend python3 -m unittest discover -s backend/tests -t backend -v
```

### Frontend

Requirements:

- Node.js 20+ recommended
- npm or another compatible package manager

Install and run:

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

Create the frontend environment file at:

- [frontend/.env.local](/Users/amroalkrisat/Documents/cd%20finance-allocator/frontend/.env.local)
- Example file: [frontend/.env.example](/Users/amroalkrisat/Documents/cd%20finance-allocator/frontend/.env.example)

Put this exact value in it for local end-to-end development:

```bash
NEXT_PUBLIC_PLANNER_API_URL=http://127.0.0.1:8000/api/planner
```

Notes:

- with no `NEXT_PUBLIC_PLANNER_API_URL` set, the frontend runs in demo mode using backend-generated seeded fixtures
- to use a live planner backend instead, set `NEXT_PUBLIC_PLANNER_API_URL=http://127.0.0.1:8000/api/planner`
- the frontend expects a planner endpoint that accepts the payload shape defined in [types.ts](/Users/amroalkrisat/Documents/cd%20finance-allocator/frontend/src/lib/types.ts)
- if `NEXT_PUBLIC_PLANNER_API_URL` is set and the backend is unavailable, the frontend now shows an error instead of silently falling back to fixture data
- available frontend scripts are `dev`, `build`, `start`, `lint`, and `typecheck`

## Demo Flow

The repo includes one seeded sample user profile for immediate demos:

- realistic salary plus side income
- recurring expenses
- high-interest credit-card debt plus student loans
- emergency fund inputs via liquid balances and a three-month target
- employer retirement match preferences

To refresh the demo data after changing the sample profile:

```bash
PYTHONPATH=backend python3 backend/scripts/generate_sample_plan.py
```

Then start the frontend. The intake form will load the seeded profile and the app will show a visible monthly plan and per-paycheck plan immediately, even without a running backend API.

## Local URLs

- Frontend app: [http://127.0.0.1:3000](http://127.0.0.1:3000)
- Backend planner API: [http://127.0.0.1:8000/api/planner](http://127.0.0.1:8000/api/planner)
- Backend health endpoint: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

## Deployment

Recommended hosting:

- frontend: Vercel
- backend: Render

### Render Backend

This repo now includes [render.yaml](/Users/amroalkrisat/Documents/cd%20finance-allocator/render.yaml) for a simple Python web service deployment.

Render setup:

1. Push this repo to GitHub.
2. In Render, choose `New +` then `Blueprint`.
3. Select the GitHub repo and deploy the blueprint.
4. Render will create a web service named `finance-allocator-api`.
5. After deploy, copy the public backend URL.

Expected backend endpoints after deploy:

- `https://<your-render-service>.onrender.com/health`
- `https://<your-render-service>.onrender.com/api/planner`

### Vercel Frontend

The frontend app lives in [frontend](/Users/amroalkrisat/Documents/cd%20finance-allocator/frontend) and includes [vercel.json](/Users/amroalkrisat/Documents/cd%20finance-allocator/frontend/vercel.json).

Vercel setup:

1. Import the same GitHub repo into Vercel.
2. Set the project root directory to `frontend`.
3. Add the environment variable:
   `NEXT_PUBLIC_PLANNER_API_URL=https://<your-render-service>.onrender.com/api/planner`
4. Deploy.
5. Copy the Vercel production URL.

After that, the Vercel URL is the shareable frontend link you can send to someone.

### Shareable Link

The final shareable link will be your Vercel production URL, which looks like:

- `https://<your-vercel-project>.vercel.app`

I cannot generate the actual live Vercel or Render URLs from here because deployment requires access to your hosting accounts, but the repo is prepared for that flow now.

## Architecture Notes

The repo is a small monorepo with:

- `frontend/` for the Next.js intake and dashboard UI
- `backend/` for the planning engine and tests
- `database/` for the proposed Postgres schema
- `docs/` for design notes and module boundaries

### Planning Flow

1. The frontend or any Python caller submits a planning payload.
2. The intake layer validates and normalizes financial inputs into monthly planning models.
3. The strategy layer chooses the recommendation waterfall and debt focus.
4. Debt and savings/investing modules compute category-specific guidance.
5. The allocation engine creates monthly and per-paycheck plans.
6. The testing layer validates constraints and cash timing.
7. The evaluation layer scores plan quality and flags risk.
8. The orchestration layer returns a structured planning summary with logs and iteration history.

### Module Boundaries

- Intake: parse payloads, validate constraints, normalize frequencies, and summarize the financial profile.
- Strategy: select the priority order and weights used by downstream allocation logic.
- Debt: compare avalanche vs snowball, estimate payoff, and detect unsustainable debt load.
- Savings/Investing: compute emergency fund targets, sinking funds, retirement, brokerage, and short-term goal recommendations.
- Allocation: produce monthly allocations and due-date-aware paycheck allocations.
- Testing: verify allocation math, income constraints, impossible budgets, and paycheck timing.
- Evaluation: score plan quality, flag fragility risks, and suggest next-step refinements.
- Orchestration: coordinate the full workflow, track stage status, and retry when validation fails.

### Design Tradeoffs

- The backend owns business logic so the frontend can stay thin.
- The planner operates on monthly-normalized values to reduce complexity in the MVP.
- Recommendations are deterministic and inspectable rather than probabilistic or AI-generated.
- The frontend intake flow is intentionally compact and single-scenario to keep the MVP moving.
- Postgres schema design is included, but persistence wiring is not yet fully implemented.

## Key Files

- Backend planning entrypoint: [planner.py](/Users/amroalkrisat/Documents/cd%20finance-allocator/backend/app/api/planner.py)
- Orchestration layer: [agent.py](/Users/amroalkrisat/Documents/cd%20finance-allocator/backend/app/services/orchestration/agent.py)
- Evaluation layer: [agent.py](/Users/amroalkrisat/Documents/cd%20finance-allocator/backend/app/services/evaluation/agent.py)
- Allocation engine: [agent.py](/Users/amroalkrisat/Documents/cd%20finance-allocator/backend/app/services/allocation/agent.py)
- Sample payload: [sample_data.py](/Users/amroalkrisat/Documents/cd%20finance-allocator/backend/app/sample_data.py)
- Sample output: [sample_plan.json](/Users/amroalkrisat/Documents/cd%20finance-allocator/backend/output/sample_plan.json)
- Frontend demo payload fixture: [sample-profile.json](/Users/amroalkrisat/Documents/cd%20finance-allocator/frontend/src/lib/fixtures/sample-profile.json)
- Frontend demo plan fixture: [sample-plan.json](/Users/amroalkrisat/Documents/cd%20finance-allocator/frontend/src/lib/fixtures/sample-plan.json)
- Frontend intake page: [page.tsx](/Users/amroalkrisat/Documents/cd%20finance-allocator/frontend/src/app/page.tsx)

## Database Summary

The proposed Postgres schema includes:

- `users` for local auth
- `profiles` for planning defaults
- `income_sources`, `expenses`, `debts`, `accounts`, and `goals` for financial inputs
- `allocation_runs` and `allocation_results` for stored plan output
- `strategy_configs` for configurable strategy presets

See [schema.sql](/Users/amroalkrisat/Documents/cd%20finance-allocator/database/schema.sql).

## Testing Status

Backend test suite status in this environment:

- 19 tests passed with `unittest`
- sample seeded demo flow is covered by integration tests
- debt, savings/investing, allocation math, constraint validation, evaluation, and orchestration flow are covered

Frontend contract notes:

- the frontend consumes `objective`, `final_monthly_plan`, `per_paycheck_plan`, `debt_payoff_summary`, `savings_investing_summary`, `risk_assessment`, `financial_stability_report`, and `suggested_next_iteration_roadmap`
- the backend currently returns all of those fields
- the frontend ignores extra response fields like `stages`, `iterations`, and `logs`, which is safe
- no obvious blocking contract mismatch was found in the current response shape audit

## Additional Docs

- [architecture.md](/Users/amroalkrisat/Documents/cd%20finance-allocator/docs/architecture.md)
- [modules.md](/Users/amroalkrisat/Documents/cd%20finance-allocator/docs/modules.md)
- [implementation-plan.md](/Users/amroalkrisat/Documents/cd%20finance-allocator/docs/implementation-plan.md)
