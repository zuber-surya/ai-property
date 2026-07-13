# Page: Tenant & Branding Settings

> **Route:** `/admin/settings` · **PRD Module:** 16 · **App:** `admin-portal/` → `pages/TenantSettings/`
> Part of [Doc 17 — Admin Spec](README.md). Read [`README.md` §4](README.md#4-cross-cutting-rules-for-every-admin-page) first.

---

## 1. Purpose & Traceability

Where a tenant makes the public site **theirs** — logo, color, domain. This is the visible payoff of multi-tenancy: the buyer browsing `sharmaestates.com` should never see the word "PropVista".

| Requirement | Source |
|---|---|
| FR16.2 Tenant admin: configure branding (logo, colors, custom domain) with live preview | `01-prd.md` §17 |
| Acceptance: **branding changes apply immediately to that tenant's public site only; no leakage to other tenants** | `01-prd.md` §17 |
| The public site is tenant-branded; the admin portal is not | `02-architecture.md` §5.1 |
| The tenant is resolved from the request domain | `04-api-spec.md` §1 |

---

## 2. Entry & Exit Points

**Entry:** sidebar → Settings; the new-tenant onboarding checklist ("upload your logo" is the step that makes the product feel real).

**Exit:** "View your site →" — the public site, freshly branded.

---

## 3. Layout & Regions

```
┌──────────┬────────────────────────────────────────────────────────────┐
│ SIDEBAR  │  Settings   [▪Branding] [Notifications]                    │
│          │                                                            │
│          │  ┌── BRANDING ────────────┐  ┌── LIVE PREVIEW ──────────┐  │
│          │  │                        │  │ ┌──────────────────────┐ │  │
│          │  │  Logo                  │  │ │ [logo]   Buy Rent ▪  │ │  │
│          │  │  ┌──────────────┐      │  │ ├──────────────────────┤ │  │
│          │  │  │  [ logo ]    │      │  │ │                      │ │  │
│          │  │  │  [ Replace ] │      │  │ │  Describe the home   │ │  │
│          │  │  └──────────────┘      │  │ │  you're looking for. │ │  │
│          │  │  PNG/SVG, max 2MB      │  │ │  ┌────────────────┐  │ │  │
│          │  │                        │  │ │  │              →│  │ │  │
│          │  │  Primary color         │  │ │  └────────────────┘  │ │  │
│          │  │  [ #C17F3C ] ███       │  │ │                      │ │  │
│          │  │                        │  │ │  ┌────┐ ┌────┐       │ │  │
│          │  │  ⚠ Contrast on white:  │  │ │  │card│ │card│       │ │  │
│          │  │     3.1:1 — fails AA   │  │ │  └────┘ └────┘       │ │  │
│          │  │     for small text     │  │ └──────────────────────┘ │  │
│          │  │                        │  │      ↑ updates as you    │  │
│          │  └────────────────────────┘  │        type (FR16.2)     │  │
│          │                              └──────────────────────────┘  │
│          │  ┌── DOMAIN ───────────────────────────────────────────┐   │
│          │  │  Your site is at                                    │   │
│          │  │  sharma.propvista.com                    [Copy]     │   │
│          │  │                                                     │   │
│          │  │  Custom domain                                      │   │
│          │  │  [ www.sharmaestates.com          ]  [ Verify ]     │   │
│          │  │                                                     │   │
│          │  │  ⏳ Pending verification                            │   │
│          │  │  Add this CNAME with your DNS provider:             │   │
│          │  │  ┌──────────────────────────────────────────────┐   │   │
│          │  │  │ www  CNAME  tenants.propvista.com            │   │   │
│          │  │  └──────────────────────────────────────────────┘   │   │
│          │  └─────────────────────────────────────────────────────┘   │
│          │                                          [ Save ]          │
└──────────┴────────────────────────────────────────────────────────────┘
```

| Region | Maps to |
|---|---|
| Logo | `tenants.branding_logo_url` (Supabase Storage) |
| Primary color | `tenants.branding_primary_color` |
| **Contrast check** | Not required by any doc — but `13-ui-ux-flows.md` §4.8 mandates 4.5:1 contrast, and a tenant picking a pale gold will silently ship an inaccessible site. **Warn at the point of choice**, not in an audit six months later |
| Live preview | FR16.2's explicit requirement |
| Domain | `tenants.domain` — **the key to the entire multi-tenancy model** (§4.1) |

---

## 4. Workflow

```
Admin opens Settings → Branding
   │
   ▼
GET /auth/me  (or a tenant-settings read)
   │   ⚠ there is no GET endpoint for the tenant's own branding —
   │     only PUT /admin/tenant/branding. See §6.
   ▼
Uploads a logo, picks a color
   │
   ▼
The preview updates live as they type                        [FR16.2]
   │
   ▼
[ Save ] → PUT /admin/tenant/branding
   │
   ▼
Applies IMMEDIATELY to that tenant's public site — no deploy  [FR16.2 acceptance]
   │   · if branding is cached per domain, the cache MUST invalidate here,
   │     or "immediately" is quietly false
   ▼
"View your site →"
```

### 4.1 Custom Domain — the part that's actually hard

```
Admin enters www.sharmaestates.com
   │
   ▼
System shows the CNAME to add
   │
   ▼
Admin adds it at their DNS provider (GoDaddy, Cloudflare, …)
   │
   ▼
[ Verify ] → the system resolves the DNS
   │
   ├─ not yet propagated → "Not visible yet. DNS can take up to 48h.
   │                        We'll keep checking." (Do NOT tell them
   │                        they did it wrong — they probably didn't.)
   │
   └─ verified
        │
        ▼
   ⚠ An SSL certificate must now be issued for that domain.
     Nothing in 10-deployment-devops.md covers per-tenant certificate
     provisioning. Without it the tenant's site serves an SSL warning,
     which is worse than having no custom domain at all.
        │
        ▼
   tenants.domain = www.sharmaestates.com
        │
        ▼
   The tenant resolver (core/tenancy.py) now maps that domain → this
   tenant on every public request. This one column is what makes the
   ENTIRE public-site tenancy model work: no domain, no tenant, no
   properties, no branding, no anything.
```

---

## 5. States

| State | Behavior |
|---|---|
| Loading | Skeleton |
| Default (no branding set) | Platform default colors + the tenant name as a text wordmark. **Never a broken image or an empty header** |
| Uploading a logo | Progress; the preview updates on completion |
| Color picked with poor contrast | Warn inline (§3). Don't block — it's their brand — but don't let them ship it unknowingly |
| Domain unverified | Show the CNAME + a "checking" state. **Poll**, don't make them click Verify repeatedly |
| Domain verified, SSL pending | Say so explicitly. A verified domain serving an SSL warning is a worse experience than the subdomain |
| Domain taken by another tenant | Reject clearly (§9) |
| Saved | "Live on your site" + a link |

---

## 6. API Calls

| Trigger | Call | Notes |
|---|---|---|
| Save branding | `PUT /admin/tenant/branding` | Logo, colors, domain. `04-api-spec.md` §15 |
| **Read own branding** | *(none)* | ⚠ There's a `PUT` and no `GET`. The page has to source the current values from somewhere — presumably `/auth/me`, which isn't specified to return them. **Add `GET /admin/tenant`** |
| Logo upload | *(none)* | No media endpoint exists outside `POST /admin/properties/{id}/media` |
| Verify domain | *(none)* | Not specified |

---

## 7. Data Touched

| Table | Access |
|---|---|
| `tenants` | Read / Write (`branding_logo_url`, `branding_primary_color`, `domain`) |
| Supabase Storage | Write (the logo) |
| *`audit_log`* | Should record branding/domain changes — **doesn't exist (A1)**. A domain change is a *high-risk* action: get it wrong and the tenant's public site goes dark |

**`tenants` is platform-level, not tenant-scoped** (`.claude/rules/database.md`) — it's the table `tenant_id` references. So RLS doesn't protect it the way it protects everything else. **The `tenant_id = caller's own` check on this endpoint is application-level, and it is the only thing standing between a tenant admin and another tenant's row.** That deserves a test.

---

## 8. Roles & Permissions

| Action | `agent` | `admin` | `super_admin` |
|---|---|---|---|
| View / edit **own** branding | ❌ | ✅ | ✅ |
| Edit **another tenant's** branding | ❌ | **❌ — must be impossible** | ✅ (via [21](21-superadmin-tenants.md)) |
| Change plan/status | ❌ | ❌ | ✅ |

**`PUT /admin/tenant/branding` must derive the tenant from the authenticated user — never from a request parameter.** If it accepted a `tenant_id`, any tenant admin could rebrand (or, by changing `domain`, effectively **hijack**) another tenant's site. Since `tenants` sits outside the RLS pattern, this is a hand-written check with no database backstop. Test it explicitly (`TC-TENANT-03`).

---

## 9. Validation & Edge Cases

- **Domain uniqueness is load-bearing.** `tenants.domain` is the tenant resolver's key. Two tenants claiming the same domain would make tenant resolution **ambiguous** — and ambiguous tenant resolution means serving one tenant's data on another's site. It must be `UNIQUE`, enforced at the database level, not just checked in the service.
- **Domain hijacking:** a tenant must not be able to claim a domain they don't control. **Verification (DNS TXT/CNAME) is a security control, not a convenience.** Without it, tenant B could set `domain = sharmaestates.com` and — depending on routing — intercept tenant A's traffic.
- **Reserved domains:** the platform's own (`propvista.com`, `app.propvista.com`, the admin portal's) must be blocked.
- **Removing a custom domain** must fall back cleanly to the subdomain, not leave the tenant with no reachable site.
- **Logo:** type allowlist (PNG/SVG/JPG), size cap, dimension guidance. **An SVG is executable content** — an SVG with an embedded `<script>` served from your domain is a real XSS vector. Either sanitize SVGs properly or don't accept them.
- **Color:** validate the hex. And note that a single `branding_primary_color` cannot express hover/active/disabled states — the frontend must **derive** those (as `13-ui-ux-flows.md` §4.4 does with `color-brass-hover`), or the tenant's buttons will have no hover state.
- **Contrast** (§3) — warn.

---

## 10. Acceptance Criteria

| ID | Case | Source |
|---|---|---|
| TC-TENANT-03 | A branding change applies to **that tenant's public site only**, with no leakage (FR16.2 acceptance) | Sprint 9 |
| — | A tenant admin cannot modify another tenant's branding or domain | Security test |
| — | Two tenants cannot claim the same domain | Security test |
| — | Branding changes appear immediately, with no deploy (cache invalidation included) | FR16.2 |
| TC-ROLE-01 | An agent cannot access tenant settings (403) | Sprint 8 |

---

## 11. Open Questions

- [ ] **Per-tenant SSL certificate provisioning is unaddressed** in `10-deployment-devops.md`. Custom domains without automated certs (ACM + CloudFront, or Let's Encrypt) means either manual ops per tenant — which doesn't scale — or tenants seeing SSL warnings on their own site. **This is the biggest unsolved piece of the custom-domain feature**, and it's infrastructure, not application code.
- [ ] **No `GET` endpoint for the tenant's own settings** (§6), and no logo-upload endpoint.
- [ ] **No domain-verification endpoint or flow**, though it's a security requirement (§9).
- [ ] **`tenants` has no contact-info columns** (address, phone, email, hours, timezone) — needed by the public [Contact page](../16-customer-spec/05-contact-page.md), and the timezone is needed by every dated report ([02](02-dashboard.md) §9).
- [ ] **One color is not a brand.** Most tenants will want at least a primary and an accent. The schema has one column. Worth widening to a small palette (or a jsonb) before it ships and becomes hard to migrate.
- [ ] Where the **"approval required" tenant flag** lives (FR9.3) — it belongs on this screen and in the `tenants` table ([04](04-property-add-edit.md) §11).
