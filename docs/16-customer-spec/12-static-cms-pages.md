# Pages: Static / CMS Pages

> **Routes:** `/:slug` (About, Terms, Privacy, Careers, blog posts) · **PRD Module:** 14 (consumer side) · **App:** `public-site/` → `pages/StaticPage/`
> Part of [Doc 16 — Customer Spec](README.md). Read [`README.md` §4](README.md#4-cross-cutting-rules-for-every-customer-page) first.
> The admin authoring side is [`17-admin-spec/17-cms.md`](../17-admin-spec/17-cms.md).

---

## 1. Purpose & Traceability

Tenant-authored content rendered on the public site: About, Terms, Privacy, Careers, and blog posts. One generic template that renders any `cms_pages` row — not a hand-built page per topic.

Two things depend on this that are easy to miss: the **legal links in the registration form** ([06](06-auth-register-login.md)) and the **footer links** on every page. If CMS pages can't be served, those links go nowhere.

| Requirement | Source |
|---|---|
| FR14.1 Edit homepage banners, blog posts, static pages (About, Careers, Terms) | `01-prd.md` §15 |
| FR14.2 SEO metadata (title, meta description, slug) per page | `01-prd.md` §15 |
| Acceptance: a non-technical admin can publish without a developer | `01-prd.md` §15 |

---

## 2. Entry & Exit Points

**Entry:** the footer (the main path); the header nav for About/Contact; the Terms/Privacy links in the registration modal; a search engine (these pages exist largely for SEO); a blog link shared externally.

**Exit:** back into the site — every content page should end with a way back to the product (a "Browse properties" CTA), not a dead end.

---

## 3. Layout & Regions

```
┌──────────────────────────────────────────────────────────────┐
│ HEADER                                                       │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│      About Sharma Estates                                    │
│      ──────────────────────────────                          │
│                                                              │
│      Rendered rich-text content from cms_pages.content.       │
│      Constrained to a readable measure (~65–75ch), not        │
│      full-bleed — this is the one place on the site           │
│      where the content IS the page.                           │
│                                                              │
│      · headings                                              │
│      · paragraphs, lists, links                              │
│      · images                                                │
│                                                              │
│      ┌────────────────────────────────────────────────┐      │
│      │  Looking for a home?   [ Browse properties → ] │      │
│      └────────────────────────────────────────────────┘      │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│ FOOTER                                                       │
└──────────────────────────────────────────────────────────────┘
```

| Region | Contents |
|---|---|
| Title | `cms_pages.title` |
| Body | `cms_pages.content` (rich text / HTML) — see §9 on sanitization |
| CTA band | A standard "back into the funnel" block appended to every content page |
| `<head>` | `seo_title`, `seo_description` (FR14.2), canonical URL, Open Graph tags |

---

## 4. Workflow

```
Visitor hits /:slug  (or a search engine crawls it)
   │
   ▼
Fetch the CMS page for (tenant, slug) where published = true
   │
   ├─ not found or unpublished → 404 page (with a link back to /)
   │
   ▼
Render title + sanitized content
   │
   ▼
Set <title>, <meta description>, canonical, OG tags from the row   [FR14.2]
   │
   ▼
Visitor reads → clicks the CTA → back into /search
```

**Routing caution:** `/:slug` is a catch-all and will happily swallow `/search`, `/contact`, `/login`, and `/portal` if it's registered before them. It must be the **last** route in the table, and slugs must be validated against a reserved-word list at authoring time (see [`17-admin-spec/17-cms.md`](../17-admin-spec/17-cms.md)).

---

## 5. States

| State | Behavior |
|---|---|
| Loading | Skeleton title + paragraph lines |
| Published | Normal render |
| Unpublished (`published = false`) | **404 to the public.** Never render a draft, and never reveal that the slug exists |
| Not found | 404 page with a link home and a search box — a content 404 is a common SEO landing and should recover the visitor |
| Slug collides with a system route | The system route wins (see §4) |
| Empty content | Render the title and the CTA. Don't crash on an empty body |

---

## 6. API Calls

| Trigger | Call | Notes |
|---|---|---|
| Page load | *(none exists)* | **Gap G5.** `04-api-spec.md` §13 defines only `/admin/cms/pages` (admin CRUD). **There is no public read endpoint**, so the public site literally cannot fetch its own content |

**Proposed** (add to `04-api-spec.md` §13 before building):

| Method | Path | Purpose | Auth |
|---|---|---|---|
| GET | `/cms/pages/{slug}` | Fetch a published CMS page for the domain's tenant | None |
| GET | `/cms/pages` | List published pages (for footer nav / blog index) | None |

Both must return **only** `published = true` rows for the domain-resolved tenant.

---

## 7. Data Touched

| Table | Access |
|---|---|
| `cms_pages` | Read (`tenant_id` = domain tenant, `published = true`) |
| `tenants` | Read (branding for header/footer) |

---

## 8. Permissions & Tenancy

- **Auth:** none. These pages are public and intentionally crawlable.
- **Tenancy:** two tenants can both have a page with slug `about` — that's expected and correct. The lookup key is **`(tenant_id, slug)`**, never `slug` alone. A unique constraint on `slug` alone would be a multi-tenancy bug; `03-database-schema.md` doesn't currently state which it is (see §11).
- The public endpoint must **never** expose unpublished rows — that's the tenant's unreleased content.

---

## 9. Validation & Edge Cases

- **`cms_pages.content` is rich text/HTML, authored by a tenant admin, and rendered on the public site. This is a stored-XSS surface.** Two defenses, both needed:
  1. **Sanitize on write** (admin side) with a strict allowlist of tags/attributes — no `<script>`, no `on*` handlers, no `javascript:` URLs.
  2. **Sanitize on render** (public site) as well. Never `dangerouslySetInnerHTML` on raw DB content.

  A tenant admin is not a trusted author in a multi-tenant SaaS — and even if they were, a compromised admin account shouldn't turn into script execution on every visitor's browser.
- **Reserved slugs:** `search`, `property`, `portal`, `login`, `register`, `contact`, `requirement-analysis`, `admin`, `api`. Block them at authoring time.
- **Slug format:** lowercase, hyphens, no leading/trailing slash, no unicode surprises.
- **Missing SEO fields:** fall back to `title` for `seo_title` and a truncated content excerpt for `seo_description`. Never emit an empty `<title>`.
- **Homepage banners (FR14.1)** are listed under CMS, but the homepage isn't a `cms_pages` row — so where do banners live? See §11.

---

## 10. Acceptance Criteria

| ID | Case | Source |
|---|---|---|
| — | A non-technical admin publishes a page and it appears on the public site with no deploy | FR14.1 acceptance |
| — | SEO title/description/slug render into `<head>` | FR14.2 |
| — | Tenant A's `about` page and Tenant B's `about` page are independent and never cross | `TC-TENANT-01` |
| — | An unpublished page 404s publicly | §5 |
| — | A `<script>` tag pasted into the CMS editor does not execute on the public site | Security test |

---

## 11. Open Questions

- [ ] **Gap G5 — no public CMS read endpoint.** Blocking: the public site cannot render About/Terms/blog at all. Add `GET /cms/pages/{slug}` and `GET /cms/pages` to `04-api-spec.md`.
- [ ] **Is `cms_pages.slug` unique per tenant or globally?** `03-database-schema.md` §3.15 doesn't say. It must be `UNIQUE (tenant_id, slug)`.
- [ ] **Homepage banners (FR14.1) have no home.** `cms_pages` is slug+content — it can't represent a banner (image + headline + link + order). Either add a `banners` table or model the homepage as a structured CMS page. Needs a decision in `01-prd.md`/`03-database-schema.md`.
- [ ] **Blog vs. page** — `cms_pages` has no `type`, `author`, `published_at`, or `excerpt`, so a blog index ("latest posts") can't be built or ordered. If blogging is really in scope (FR14.1 says "blog posts"), the schema needs those columns.
- [ ] Whether these pages need server-side rendering for SEO. The app is a Vite SPA (`02-architecture.md`), which **does not SSR** — and these are precisely the pages whose entire purpose is search visibility. This is a real architectural tension and it's unaddressed anywhere in the doc set. Options: prerender at build, add SSR for this route group, or accept weaker indexing.
