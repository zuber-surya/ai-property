# Rule: Frontend (React / TypeScript)

Applies to: `public-site/` and `admin-portal/`. Source: `docs/02-architecture.md` §5, `docs/09-coding-standards.md` §3.

## Two separate apps
- `public-site/` — public site + customer portal (shared auth context; the portal is an authenticated view of the public site). Tenant-branded.
- `admin-portal/` — admin/agent/super-admin CRM. Not tenant-branded.
- Both use Vite + React + TypeScript and share the same folder shape (`pages/` + `components/` + `hooks/` + `api/` + `context/`).

## Style & tooling
- Format with `prettier`; lint with `eslint` (TS + React rules).
- **TypeScript strict mode on. No `any`** without an inline comment justifying it.
- Function components with hooks only — no class components.

## Naming
- Component files: `PascalCase.tsx` matching the component (`PropertyCard.tsx`).
- Hooks: `useSomething.ts`.
- API client functions: `camelCase`, grouped by domain in `api/` (e.g. `api/properties.ts` exports `getProperties()`, `getPropertyById()`).

## Structure
- Page components own data-fetching/orchestration; `components/` stay presentational and reusable where possible.
- The three USP widgets get self-contained subfolders — `components/chat/`, `components/search/`, `components/recommendation/` (or `RequirementAnalysis`). Keep their logic in one place; these are the most iterated-on parts of the product.

## State
- Default to `useState` / `useReducer`. Only genuinely cross-cutting state (auth/tenant) goes in React Context (`context/`). Don't reach for a heavier state library unless a concrete need emerges.

## API contract sync
- Generate request/response types from the FastAPI OpenAPI schema where practical rather than hand-duplicating — reduces drift from backend Pydantic schemas.
