# Rule: Backend (Python / FastAPI)

Applies to: everything in `backend/`. Source: `docs/02-architecture.md` §4, `docs/09-coding-standards.md` §2.

## Layering — never skip a layer
```
Router (api/v1/*.py)  →  Service (services/*.py)  →  Repository (repositories/*.py)  →  DB
```
- **Routers** only: parse request, call one service method, return response. No business logic.
- **Services** hold business logic and orchestrate repositories/AI clients. Services **never** construct raw SQL.
- **Repositories** are the only place raw SQLAlchemy queries live.
- AI modules add a client layer: `Router → AI Service → AI Client (Bedrock) + Repository`. **Never call `app/ai_clients/` from a router.**

Keep to the folder structure in `docs/02-architecture.md` §4.2 exactly — don't add top-level folders or reorganize layers without updating that doc first.

## Style & tooling
- Format with `black`; lint/sort imports with `ruff`.
- **Type hints required on all function signatures.** Correctness leans on Pydantic + type hints, not runtime checks.
- One-line docstrings required on service functions and non-trivial repository methods. Routers rely on FastAPI's OpenAPI description instead.

## Naming
- Files/modules: `snake_case.py`. Classes: `PascalCase` (`PropertyService`, `LeadRepository`). Functions/vars: `snake_case`.
- Pydantic schemas suffixed by purpose: `PropertyCreate`, `PropertyUpdate`, `PropertyOut`. Never reuse one schema for request and response when the shapes differ.

## Async
- All I/O-bound endpoints (DB, Bedrock) are `async def`.
- Bedrock calls use the async boto3 pattern — chat/search/recommend are latency-sensitive and must not block the event loop.

## Error handling
- Raise domain exceptions in the service layer (e.g. `PropertyNotFoundError`).
- A shared FastAPI exception handler maps them to the standard error envelope from `docs/04-api-spec.md` §1: `{"error": {"code": ..., "message": ...}}`.
- **Never let a raw DB or Bedrock exception reach the client.**

## Config & secrets
- All settings load through `app/core/config.py`. Secrets come from env vars only — never hardcoded, never committed. Keep `.env.example` current.
