# Page: Content & Website Management (CMS)

> **Route:** `/admin/cms` · **PRD Module:** 14 · **App:** `admin-portal/` → `pages/CMS/`
> Part of [Doc 17 — Admin Spec](README.md). Read [`README.md` §4](README.md#4-cross-cutting-rules-for-every-admin-page) first.
> Public consumer side: [`16-customer-spec/12-static-cms-pages.md`](../16-customer-spec/12-static-cms-pages.md)

---

## 1. Purpose & Traceability

Lets a tenant edit their own site copy — About, Terms, Privacy, Careers, blog posts, homepage banners — **without a developer**. That's the entire acceptance criterion, and it's a good one: if a tenant has to email support to fix a typo on their About page, this module has failed.

| Requirement | Source |
|---|---|
| FR14.1 Edit homepage banners, blog posts, static pages (About, Careers, Terms) | `01-prd.md` §15 |
| FR14.2 SEO metadata (title, meta description, slug) per page/listing | `01-prd.md` §15 |
| Acceptance: **a non-technical admin can publish a content change without developer involvement** | `01-prd.md` §15 |

---

## 2. Entry & Exit Points

**Entry:** sidebar → CMS; the new-tenant onboarding checklist ("write your About page").

**Exit:** "View live →" opens the public page. As with property approvals, **previewing what the visitor actually sees is the single most important control here.**

---

## 3. Layout & Regions

```
┌──────────┬────────────────────────────────────────────────────────────┐
│ SIDEBAR  │  Content                                    [ + New page ] │
│          │                                                            │
│          │  ┌──────────────────────────────────────────────────────┐  │
│          │  │ Title        │ Slug        │ Status      │ Updated  │  │
│          │  ├──────────────────────────────────────────────────────┤  │
│          │  │ About us     │ /about      │ [Published] │ 2d ago   │  │
│          │  │ Terms        │ /terms      │ [Published] │ 30d ago  │  │
│          │  │ Privacy      │ /privacy    │ [Published] │ 30d ago  │  │
│          │  │ Careers      │ /careers    │ [Draft]     │ 1h ago   │  │
│          │  └──────────────────────────────────────────────────────┘  │
│          │                                                            │
│          │  ── Editing: About us ──────────────────────────────────   │
│          │                                                            │
│          │  Title    [ About us                              ]        │
│          │  Slug     [ /about                                ]        │
│          │                                                            │
│          │  ┌────────────────────────────────────────────────────┐    │
│          │  │ [B] [I] [H2] [•] [🔗] [🖼]                         │    │
│          │  ├────────────────────────────────────────────────────┤    │
│          │  │                                                    │    │
│          │  │  Sharma Estates has served Bangalore's East since │    │
│          │  │  1998. We specialise in…                          │    │
│          │  │                                                    │    │
│          │  └────────────────────────────────────────────────────┘    │
│          │                                                            │
│          │  ┌─ SEO ───────────────────────────────────────────────┐   │
│          │  │ Page title   [ About Sharma Estates | Bangalore ]   │   │
│          │  │              52/60 characters ✓                     │   │
│          │  │ Description  [ Bangalore real estate since 1998…]   │   │
│          │  │              138/160 ✓                              │   │
│          │  │                                                     │   │
│          │  │ Google preview:                                     │   │
│          │  │ ┌─────────────────────────────────────────────┐    │   │
│          │  │ │ About Sharma Estates | Bangalore            │    │   │
│          │  │ │ sharmaestates.com › about                   │    │   │
│          │  │ │ Bangalore real estate since 1998…           │    │   │
│          │  │ └─────────────────────────────────────────────┘    │   │
│          │  └─────────────────────────────────────────────────────┘   │
│          │                                                            │
│          │  [ Save draft ]  [ Preview ]  [ Publish ]                  │
└──────────┴────────────────────────────────────────────────────────────┘
```

| Region | Maps to |
|---|---|
| Page list | `cms_pages` (title, slug, `published`, `updated_at`) |
| Rich-text editor | `cms_pages.content` — **a sanitized allowlist editor, not a raw HTML box** (§9) |
| SEO panel | `seo_title`, `seo_description` + a live Google preview (FR14.2) |
| Publish | `published = true` |

**The Google preview is worth building.** It turns an abstract field ("meta description") into something a non-technical admin immediately understands, which is exactly the acceptance criterion.

---

## 4. Workflow

```
Admin opens CMS
   │
   ▼
GET /admin/cms/pages → the tenant's pages
   │
   ├─→ [ + New page ] → editor with an empty slug
   │
   └─→ Clicks a page → editor, pre-filled
            │
            ▼
        Edits content + SEO
            │
            ├─→ [ Save draft ] → published = false (not public)
            │
            ├─→ [ Preview ]    → renders the public page from unsaved
            │                    content. ⚠ no endpoint (§6)
            │
            └─→ [ Publish ]    → PUT /admin/cms/pages/{id}, published = true
                     │
                     ▼
                Live on the public site immediately —
                no deploy, no developer                  [FR14.1 acceptance]
                     │
                     ▼
                ⚠ …if a public read endpoint exists.
                  It does not. (Customer Gap G5.)
                  The admin can publish into a void: the page is
                  marked published and the public site has no way
                  to fetch it. THE WHOLE MODULE IS INERT until
                  GET /cms/pages/{slug} is added to 04-api-spec.md.
```

---

## 5. States

| State | Behavior |
|---|---|
| Loading | Skeleton |
| **Empty (new tenant)** | Not a blank list. **Seed a starter set** — About, Terms, Privacy, Contact — as drafts with placeholder copy. A tenant whose site links to a Terms page that 404s looks broken, and the tenant won't notice until a customer does |
| Draft | Not public; "View live" is disabled |
| Published | "View live →" enabled |
| Unsaved changes | Dirty indicator; confirm on navigate |
| Slug conflict | Inline error ("/about is already used by another page") |
| Reserved slug | Inline error ("/search is reserved") — see §9 |

---

## 6. API Calls

| Trigger | Call | Notes |
|---|---|---|
| Mount | `GET /admin/cms/pages` | `04-api-spec.md` §13 |
| Create | `POST /admin/cms/pages` | |
| Save / publish | `PUT /admin/cms/pages/{id}` | |
| Delete | `DELETE /admin/cms/pages/{id}` | ⚠ hard or soft? `cms_pages` has **no `deleted_at`** — the schema's soft-delete convention (`.claude/rules/database.md`) covers "user-facing entities (properties, leads, users)" and doesn't mention CMS pages. So a delete here is destructive and unrecoverable |
| **Preview** | *(none)* | |
| **Public read** | *(none)* | **Customer Gap G5 — the module doesn't function without it** |

---

## 7. Data Touched

| Table | Access |
|---|---|
| `cms_pages` | Read / Write / Delete (`tenant_id`, `slug`, `title`, `content`, `seo_title`, `seo_description`, `published`) |
| *`audit_log`* | Should record content changes — **doesn't exist (A1)** |

---

## 8. Roles & Permissions

| Action | `agent` | `admin` | `super_admin` |
|---|---|---|---|
| View / edit / publish | ❌ | ✅ | ✅ |

Admin-only, tenant-scoped. **Two tenants both having an `/about` page is normal and correct** — the key is `(tenant_id, slug)`, never `slug` alone ([customer 12](../16-customer-spec/12-static-cms-pages.md) §8).

---

## 9. Validation & Edge Cases

- **⚠ The content field is a stored-XSS surface, and it is the most dangerous one in the product.** A tenant admin authors HTML that renders on the **public site**, in every visitor's browser. Two defenses, **both required**:
  1. **Sanitize on write** — a strict allowlist (headings, paragraphs, lists, links, images, basic formatting). No `<script>`, no `on*` attributes, no `javascript:` URLs, no `<iframe>`.
  2. **Sanitize on render** — never `dangerouslySetInnerHTML` on raw DB content.

  A tenant admin is *not* a trusted author in a multi-tenant SaaS, and a compromised tenant admin account must not become script execution on that tenant's customers. **Use a well-tested sanitizer; do not write your own.**
- **Reserved slugs:** `search`, `property`, `portal`, `login`, `register`, `contact`, `requirement-analysis`, `admin`, `api`. A tenant who creates a page at `/search` breaks their own property search — and `/:slug` being a catch-all means the router will happily let them ([customer 12](../16-customer-spec/12-static-cms-pages.md) §4).
- **Slug format:** lowercase, hyphens, no spaces, no leading/trailing slash. Auto-generate from the title, allow an override.
- **Changing a published page's slug** breaks every existing inbound link and kills its SEO. **Warn, and offer to keep a redirect** — there's nowhere to store a redirect today, which is itself a gap.
- **Deleting a page that the footer links to** leaves a dead link. Warn.
- **SEO field lengths:** title ~60 chars, description ~160. Show counters (as drawn) rather than silently truncating in the `<head>`.
- **Images in content:** where are they uploaded? Supabase Storage, presumably — but no media endpoint exists for CMS (only `POST /admin/properties/{id}/media`, which is property-scoped).

---

## 10. Acceptance Criteria

| ID | Case | Source |
|---|---|---|
| — | A non-technical admin edits and publishes a page with **no developer involvement** (FR14.1 acceptance) | `01-prd.md` §15 |
| — | SEO title/description/slug appear in the public page's `<head>` (FR14.2) | `01-prd.md` §15 |
| — | A published page is publicly reachable; a draft 404s | [Customer 12](../16-customer-spec/12-static-cms-pages.md) §5 |
| TC-TENANT-01 | Tenant A's `/about` and tenant B's `/about` are independent | Sprint 1 |
| — | **A `<script>` tag pasted into the editor does not execute on the public site** | Security test |
| TC-ROLE-01 | An agent cannot access CMS endpoints (403) | Sprint 8 |

---

## 11. Open Questions

- [ ] **Customer Gap G5 — no public CMS read endpoint.** Until `GET /cms/pages/{slug}` exists, this entire module publishes into a void. **The highest-priority fix for this page**, and it's a small one.
- [ ] **Homepage banners (FR14.1) don't fit `cms_pages`.** A banner is an image + headline + CTA link + sort order — not a slug and a content blob. Either add a `banners` table or model the homepage as structured content. **Currently unbuildable as specified.**
- [ ] **Blog posts (FR14.1) don't fit either.** No `type`, `author`, `published_at`, or `excerpt` columns — so a blog index can't be listed or ordered. If blogging is really in scope, the schema needs those.
- [ ] **`cms_pages.slug` uniqueness** — must be `UNIQUE (tenant_id, slug)`; the schema doesn't say.
- [ ] **Delete is hard, not soft** — no `deleted_at` on `cms_pages`. Intentional?
- [ ] **No image upload path for CMS content**, and no preview endpoint.
- [ ] **SPA vs. SEO:** these pages exist for search visibility, and the public site is a Vite SPA with no SSR ([customer 12](../16-customer-spec/12-static-cms-pages.md) §11). Unaddressed anywhere in the doc set, and it partly defeats the purpose of FR14.2.
