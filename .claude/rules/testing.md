# Rule: Testing

Applies to: all new logic. Source: `docs/09-coding-standards.md` §5, `docs/15-development-plan.md` (per-sprint `TC-*` cases).

## Backend — pytest
- Unit-test services (business logic) with repositories mocked.
- A smaller set of integration tests hits a real **test** Supabase Postgres instance for repository-layer and RLS-policy correctness.
- **Tenant isolation must have explicit tests** — at least one per tenant-owned table proving a Tenant A user cannot read/write Tenant B rows (enforced at the DB layer).

## AI modules
- **Mock the Bedrock client** for standard unit tests (e.g. "does the service call `create_lead` when the model requests that tool"). Do not hit live Bedrock in fast CI.
- The golden test sets in `docs/05`/`06`/`07` are a **separate** evaluation suite — run periodically / pre-release, not in the fast unit-test run, since they use real Bedrock calls.

## Frontend — Vitest + React Testing Library
- Component tests for the key interactive components: chat widget, search bar, requirement wizard, lead Kanban board.

## Acceptance criteria
- Each sprint in `docs/15-development-plan.md` lists concrete `TC-*` cases and a Definition of Done — treat those as the acceptance criteria for the module, and write tests to cover them.
- Write tests **alongside** the implementation, not after.
