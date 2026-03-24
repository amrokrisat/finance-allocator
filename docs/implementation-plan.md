# Implementation Plan

## Phase 1: Project Bootstrap

- initialize the Next.js app in `frontend/`
- initialize the Python backend service in `backend/`
- add formatting, linting, and test tooling
- wire local development via environment variables

## Phase 2: Persistence And Auth

- set up Postgres connection and migrations
- implement MVP local auth with hashed passwords and session handling
- create repositories for core financial entities

## Phase 3: Financial Intake

- build input schemas for income, expenses, debts, accounts, and goals
- normalize recurring amounts to monthly values
- persist a planning snapshot that can be reused for plan runs

## Phase 4: Financial Logic

- implement strategy profiles
- implement allocation waterfall
- implement debt prioritization helpers
- implement emergency fund, sinking fund, retirement, brokerage, and short-term goal calculations

## Phase 5: API And UI

- add plan creation and plan retrieval endpoints
- build a minimal multi-step intake flow
- build a simple results page with allocation explanation

## Phase 6: Testing And Hardening

- add unit tests for each core financial module
- add integration tests for one or two full scenarios
- validate explanation output and edge-case handling

## Delivery Notes

- keep comments focused on business-rule assumptions
- keep strategy configuration data-driven where possible
- avoid premature optimization or polished UI work before logic is trusted
