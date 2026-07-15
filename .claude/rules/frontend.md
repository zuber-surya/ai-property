# Rule: Frontend (React / TypeScript)

Applies to: `frontend/`. Source: `docs/02-architecture.md` §5, `docs/09-coding-standards.md` §3, ADR-0020.

## One app, route-based
- **One `frontend/` app** (Vite + React + TypeScript), decided 2026-07-15 (ADR-0020, superseding the two-app split).
- `/` and the customer routes = the public surface (public site + customer portal, anonymous-first). `/admin/*` = the CRM.
- ⚠️ **`/admin/*` MUST be lazy-loaded** (`React.lazy` + `Suspense`) so admin code is a separate chunk a public visitor never downloads. The day someone eager-imports an admin route, that mitigation is silently gone (ADR-0020). This is a bundle/exposure measure — **the security boundary is server-side** (`require_role`, RLS), never the frontend hiding a screen.
- **Not tenant-branded in the MVP** (2026-07-13). One fixed palette from `docs/DESIGN.md`, no theming layer. Post-MVP, only the public routes take a tenant's `primary`; `tertiary` stays platform-owned.
- Structure: `src/routes/public/` + `src/routes/admin/` + shared `components/` `hooks/` `api/` `context/` `styles/`.

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
