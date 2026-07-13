# Deployment & DevOps — PropVista CRM

> **Doc 10 of the PropVista CRM documentation set — final document.** Environments, hosting, CI/CD, and operational concerns for the FastAPI + React + Supabase + Amazon Bedrock stack.
>
> **Status:** Draft v1.0 · **Last updated:** July 2026
> Depends on: `02-architecture.md` (Section 8), `04-api-spec.md`, `09-coding-standards.md`

---

## 1. Hosting Target

**AWS-native**, primarily because Amazon Bedrock is the LLM provider — keeping compute in the same region as Bedrock minimizes latency and avoids cross-cloud data transfer for every AI call.

| Component | Suggested AWS Service | Notes |
|---|---|---|
| FastAPI backend | AWS App Runner or ECS (Fargate) | App Runner for simplicity at MVP scale; ECS if more infra control is needed later |
| React apps (public site + admin portal) | S3 + CloudFront (static build) | Both are client-rendered SPAs; served as static assets |
| Background jobs | FastAPI `BackgroundTasks` initially → AWS SQS + a worker (ECS task or Lambda) if promoted to Celery/RQ (per `02-architecture.md` Section 4.3) | |
| Database | Supabase-hosted Postgres | Supabase is a managed service, not self-hosted on AWS — cross-provider by design, acceptable since DB traffic isn't the latency-sensitive leg (Bedrock calls are) |
| File storage | Supabase Storage | Property images/docs — already covered by Supabase, no separate S3 bucket needed unless a specific need arises |
| Secrets | AWS Secrets Manager (or SSM Parameter Store) | Supabase service key, Bedrock IAM credentials |
| DNS / custom tenant domains | Route 53 (or existing DNS provider) + CloudFront | Needed for tenant custom-domain branding (PRD Module 16) |

This is a starting recommendation, not a locked decision — confirm actual AWS account/region setup before provisioning.

---

## 2. Environments

| Environment | Purpose | Notes |
|---|---|---|
| **Local** | Individual development | Local FastAPI (`uvicorn --reload`) + local Vite dev servers for both React apps + a local or shared dev Supabase project |
| **Staging** | Pre-production validation, tenant pilot onboarding | Mirrors production infra at smaller scale; separate Supabase project from production to avoid any risk to pilot-tenant data during testing |
| **Production** | Live multi-tenant environment | |

Environment-specific config is driven entirely by environment variables (per `09-coding-standards.md` Section 7) — the same Docker image/build artifact should be deployable to any environment by changing config, not by changing code.

---

## 3. CI/CD Pipeline (Suggested)

```
On PR:
  → lint (ruff/black for backend, eslint/prettier for frontend)
  → unit tests (pytest, Vitest)
  → type checks (mypy or pyright optional, tsc for frontend)

On merge to main:
  → build (Docker image for backend, static builds for both React apps)
  → run Alembic migrations against staging DB
  → deploy to staging
  → (manual approval gate)
  → run Alembic migrations against production DB
  → deploy to production
```

- Tool: GitHub Actions (or equivalent) — exact provider TBD based on where the repo is hosted.
- Migrations are **always applied via CI**, never manually against staging/production, to keep `03-database-schema.md` and the live schema from drifting (same principle as `09-coding-standards.md` Section 2.6).
- The AI evaluation suites (golden test sets from `05`/`06`/`07`) run **separately from the fast CI pipeline** — as a periodic or pre-release job, since they involve real Bedrock calls and are slower/costlier than unit tests.

---

## 4. Containerization

- Backend: single `Dockerfile` for the FastAPI app, based on a slim Python image.
- Frontend: no runtime container needed — both React apps build to static assets served via S3/CloudFront (or equivalent static hosting), not a Node server in production.

---

## 5. Monitoring & Logging

- **Application logs:** structured logging (`core/logging.py`, per `02-architecture.md`) shipped to CloudWatch Logs (or equivalent).
- **AI-specific observability:** log every Bedrock call's latency, token usage, and model ID — needed both for cost tracking and for debugging conversation/search/recommendation quality issues (ties to the conversation/query logging already modeled in `chat_messages` and the search-insights endpoint in `04-api-spec.md` Section 12).
- **Error tracking:** a dedicated error-tracking tool (e.g. Sentry) is recommended for both backend and frontend, to catch issues beyond what raw logs surface.
- **Uptime/health checks:** a `/health` endpoint on the backend for App Runner/ECS health checks.

---

## 6. Rate Limiting & Cost Control

Bedrock usage is the primary variable cost driver (unlike flat-rate infra), so this needs explicit control, not just infra-level rate limiting:
- Per-session/IP rate limits on `ai/*` endpoints (referenced as open in `04-api-spec.md` Section 17) — exact thresholds to be set based on expected usage patterns and monitored/adjusted post-launch rather than guessed permanently upfront.
- Per-tenant usage visibility (even without a billing model yet, per the business plan's decision to exclude pricing) — track Bedrock token usage per tenant internally, so cost drivers are understood before any future pricing model is designed.
- Consider a daily/monthly soft cap per tenant on AI-endpoint calls during the pilot phase, with graceful degradation (e.g. fallback to non-AI search) rather than hard failure if a cap is hit.

---

## 7. Backup & Disaster Recovery

- Supabase provides managed Postgres backups — confirm backup frequency/retention on the chosen Supabase plan and document the recovery process (restore steps) once confirmed.
- `property_embeddings` can, worst-case, be regenerated from `properties` data (Section 4.2 of `06-ai-search-spec.md`) — so this table is not a single point of unrecoverable failure, which is worth knowing when prioritizing backup strictness.
- Infrastructure-as-code (e.g. Terraform) is recommended once the AWS setup stabilizes, so environments are reproducible rather than manually configured — not required for the very first MVP deploy, but flagged early since retrofitting IaC later is more work than starting with it.

---

## 8. Custom Domains for Tenant Branding

Supports PRD Module 16 (tenant branding, custom domain):
- New tenant custom domain → CNAME/A record pointed at the platform's CloudFront distribution (or load balancer) → backend resolves `tenant_id` from the incoming `Host` header (per `02-architecture.md` Section 7).
- SSL: automated certificate provisioning (e.g. ACM) per custom domain, not manual per-tenant certificate handling.

---

## 9. Open Questions / Assumptions to Confirm

- [ ] Confirm AWS account/region setup and whether App Runner or ECS is the actual choice (App Runner recommended for MVP simplicity).
- [ ] CI provider (GitHub Actions assumed).
- [ ] Exact rate-limit thresholds per AI endpoint (deferred from `04-api-spec.md`) — to be set from real usage data during pilot.
- [ ] Error-tracking tool selection (Sentry suggested, not confirmed).
- [ ] Supabase plan/tier and its backup retention terms.
- [ ] Whether Terraform (or similar IaC) is introduced before or after the first production deploy.

---

## 10. Documentation Set — Complete

This closes the initial PropVista CRM documentation set:

| # | Document | Status |
|---|---|---|
| 00 | `00-project-overview.md` | ✅ |
| 01 | `01-prd.md` | ✅ |
| 02 | `02-architecture.md` | ✅ |
| 03 | `03-database-schema.md` | ✅ |
| 04 | `04-api-spec.md` | ✅ |
| 05 | `05-ai-chatbot-spec.md` | ✅ |
| 06 | `06-ai-search-spec.md` | ✅ |
| 07 | `07-ai-recommendation-spec.md` | ✅ |
| 08 | `08-auth-roles-spec.md` | ✅ |
| 09 | `09-coding-standards.md` | ✅ |
| 10 | `10-deployment-devops.md` | ✅ |

Each document carries its own "Open Questions" section — worth a final pass to resolve the remaining ones (model IDs, exact weights/thresholds, provider selections) as implementation with Claude Code begins, since several are best answered empirically rather than speculatively.
