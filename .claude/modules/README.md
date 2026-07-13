# Module Playbooks

One playbook per backend domain. Before building a module: read its playbook here, then the PRD and spec sections it points to. Every module also obeys the cross-cutting files in `.claude/rules/`.

The PRD (`docs/01-prd.md`) defines **16** feature modules across the two surfaces. They map onto the backend domains below (per `docs/02-architecture.md` §1).

| Backend domain | Playbook | PRD modules covered | Primary specs |
|---|---|---|---|
| Auth / Tenant / Roles | [auth-tenant.md](auth-tenant.md) | 11 User & Role, 16 Tenant & Branding | `docs/08` |
| Property | [property.md](property.md) | 4 Listing, 5 Details, 9 Property Management | `docs/03`, `docs/04` §8 |
| Lead / CRM | [lead-crm.md](lead-crm.md) | 6 Lead Capture, 10 CRM Pipeline, 12 Agents | `docs/04` |
| AI Chatbot | [ai-chatbot.md](ai-chatbot.md) | 1 AI Chatbot | `docs/05` |
| AI Search | [ai-search.md](ai-search.md) | 2 AI Search | `docs/06` |
| AI Recommendation | [ai-recommendation.md](ai-recommendation.md) | 3 Requirement Analysis | `docs/07` |

## Modules without a dedicated playbook yet
These follow the same patterns (`.claude/rules/*` + the referenced PRD/spec section). Build them the same way; add a playbook here if a module grows complex enough to warrant one.

- **7 Customer Portal** — PRD §8. Auth'd view over public-site data; strictly user+tenant scoped.
- **8 Admin Dashboard & Analytics** — PRD §9. Tenant-scoped KPIs reconciling with CRM data.
- **13 AI Configuration** — PRD §14. Per-tenant chatbot/search/recommendation config; changes take effect without deploy. Feeds `ai-chatbot`/`ai-search`/`ai-recommendation`.
- **14 CMS** — PRD §15. Homepage/blog/static pages + SEO metadata; `cms_pages` table.
- **15 Reports & Notifications** — PRD §16. Report export + `notification_rules`.
