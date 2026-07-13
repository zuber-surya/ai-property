# Feature: Favorites & Anonymous Session Migration

> **Appears on:** [Homepage](01-homepage.md), [Property Listing](02-property-listing.md), [Property Details](03-property-details.md), [Portal Favorites](08-portal-favorites.md) · **PRD Modules:** 4, 7 · **Component:** `public-site/src/components/property/FavoriteButton.tsx` + `context/SessionContext.tsx`
> Part of [Doc 16 — Customer Spec](README.md).

---

## 1. Purpose & Traceability

Two things, tightly coupled:

1. **Favoriting** — a one-tap save that works **without an account** (FR4.4).
2. **Session migration** — the machinery that makes (1) safe to promise: when the visitor eventually registers, everything they did anonymously follows them.

The second is invisible when it works and catastrophic when it doesn't. A visitor who favorites five properties, registers *because we asked them to*, and then finds an empty portal has been actively lied to. **This is the single highest-trust-stakes flow in the customer surface.**

| Requirement | Source |
|---|---|
| FR4.4 Favorite without login (session-based); prompt to register to persist | `01-prd.md` §5 |
| Anonymous session data migrates to the account on registration/login | `08-auth-roles-spec.md` §4 |
| Favoriting never blocks on login — the prompt comes *after* the action | `13-ui-ux-flows.md` §2.1 |
| FR7.1 Saved properties shown in the portal | `01-prd.md` §8 |

---

## 2. The Session Identity

```
First visit
   │
   ▼
No session_id in localStorage?  → generate a UUID v4
   │
   ▼
Persist to localStorage: propvista.session_id
   │
   ▼
Send on EVERY request: X-Session-Id: <uuid>
   (04-api-spec.md §1)
```

This one identifier ties together **three** tables' worth of anonymous activity:

| Table | Anonymous key | Post-registration key |
|---|---|---|
| `favorites` | `session_id` | `user_id` |
| `requirement_profiles` | `session_id` | `user_id` |
| `chat_conversations` | `session_id` | `user_id` |
| `leads` | ⚠ **neither — no `session_id` column exists** | ⚠ **no `user_id` column exists** |

That last row is the problem. See §5.

---

## 3. The Favorite Button

```
Anonymous visitor                    Logged-in customer
─────────────────                    ──────────────────
   ♡  (outline)                         ♡  (outline)
      │ tap                                │ tap
      ▼                                    ▼
   ♥  (filled) ← optimistic             ♥  (filled) ← optimistic
      │                                    │
      ▼                                    ▼
   POST /properties/{id}/favorite       POST /properties/{id}/favorite
   X-Session-Id: <uuid>                 Authorization: Bearer <jwt>
      │                                    │
      ▼                                    ▼
   row: session_id = X                  row: user_id = me
        user_id = NULL                        session_id = NULL
      │
      ▼
   ── after the 2nd favorite ──
   Inline prompt (NOT a modal, NOT blocking):
   ┌──────────────────────────────────────────┐
   │ Saved. Create an account to keep these   │
   │ when you come back.        [ Sign up ]   │
   └──────────────────────────────────────────┘
```

**Prompt timing is the whole design.** After the action, never before. And not on the *first* favorite — let them feel it working before asking for anything. Two favorites means intent; one might be a mis-tap.

**Optimistic UI:** the heart fills instantly. If the request fails, revert it and say so. Never make a visitor wait on a network round-trip to see a heart fill — but never lie about the server state either.

---

## 4. The Migration

Runs on **both** registration and login (a returning user may have accumulated anonymous activity on this device since last time).

```
POST /auth/register   (or a successful login)
   │  body/header carries the current session_id
   ▼
Backend, in ONE transaction:
   │
   ├─ favorites            SET user_id = :new_user, session_id = NULL
   │                       WHERE session_id = :sid AND tenant_id = :tenant
   │
   ├─ requirement_profiles SET user_id = :new_user
   │                       WHERE session_id = :sid AND tenant_id = :tenant
   │
   ├─ chat_conversations   SET user_id = :new_user
   │                       WHERE session_id = :sid AND tenant_id = :tenant
   │
   └─ leads                ⚠ CANNOT MIGRATE — no session_id column (§5)
   │
   ▼
Commit. All-or-nothing.
   │
   ▼
Client clears/rotates the session_id (the identity is now the JWT)
   │
   ▼
Portal shows a one-time confirmation:
   "Your 3 saved properties are now in your account."
   ← closes the loop on the promise that got them to register
```

### 4.1 Merge Conflicts (login, not registration)

A **returning** user logs in on a device that has anonymous favorites. Their account already has favorites. What happens?

| Data | Recommended rule | Why |
|---|---|---|
| `favorites` | **Union**, deduplicated on `property_id` | Never destroy a save. Duplicates are ugly; losing a shortlist is a bug the user will notice and resent |
| `requirement_profiles` | **Keep both** — the account's existing profile *and* the new anonymous one | Silently overwriting someone's saved requirements is worse than showing them two |
| `chat_conversations` | **Attach** the anonymous conversation to the user; don't merge transcripts | Two conversations are coherent; a spliced one isn't |

`08-auth-roles-spec.md` §6 flags this as open. **The rules above are a recommendation, not a decision** — but the *principle* should be non-negotiable: **on any ambiguity, keep more, not less.**

---

## 5. ⚠ Leads Cannot Migrate

`leads` (`03-database-schema.md` §3.7) has **no `session_id` and no `user_id`**. It stores `customer_name`, `customer_phone`, `customer_email` — free-text fields typed by an anonymous visitor.

**Consequences:**

1. An anonymous visitor who submits an inquiry, then registers, **cannot be shown their own inquiry** in `/portal/inquiries` — FR7.1's "inquiry history" cannot be implemented correctly.
2. The only alternative — matching leads to accounts by **email** — is a **data-leak vector**: `customer_email` is nullable, unverified, and typed by anyone. Register with someone else's email and you'd be shown their inquiries.

**Required fix** in `03-database-schema.md`:

```
leads
  + user_id     UUID NULL REFERENCES users(id)
  + session_id  text NULL
```

Set on creation (from the JWT or `X-Session-Id`), migrated alongside `favorites`. **This must be decided before Sprint 4** — retrofitting ownership onto leads that already exist in production is materially harder, and the "match on email" shortcut is the kind of thing that ships quietly and becomes a breach.

---

## 6. API Calls

| Trigger | Call | Notes |
|---|---|---|
| Favorite | `POST /properties/{id}/favorite` | Anonymous (`X-Session-Id`) or authenticated. `04-api-spec.md` §4 |
| Unfavorite | `DELETE /properties/{id}/favorite` | Must scope the delete to the **caller's** `user_id`/`session_id` — never by `property_id` alone (that would let anyone delete anyone's favorite) |
| List (portal) | `GET /portal/favorites` | Authenticated |
| Migration | `POST /auth/register` / login | Runs server-side as part of auth. Not a separate endpoint |

---

## 7. Data Touched

| Table | Access |
|---|---|
| `favorites` | Read / Write / Delete / **Update (migration)** |
| `requirement_profiles` | Update (migration) |
| `chat_conversations` | Update (migration) |
| `users` | Read (the migration target) |

---

## 8. Permissions & Tenancy

- `favorites` is tenant-owned → RLS applies. A `session_id` from tenant A's site can only ever create tenant A favorites.
- **Session IDs are client-generated and guessable-ish.** A `session_id` is not a credential — it's a correlation key. Treat it accordingly:
  - It grants access **only** to rows created with that exact ID.
  - It must **never** be accepted as an alternative to a JWT on an authenticated endpoint. `GET /portal/favorites` must reject an `X-Session-Id`-only request — otherwise the session ID becomes a bearer token for the portal.
  - Migration must be **one-way and one-time**: once a `session_id`'s rows are claimed by a user, that session ID must not be able to claim them again or re-associate them elsewhere.
- **Migration must be tenant-scoped.** `WHERE session_id = :sid` alone would migrate rows across tenants if the same browser visited two tenants' sites (which it will — same localStorage, same session ID). **Always `AND tenant_id = :tenant`.** This is a subtle cross-tenant leak that a single-tenant test will never catch.

---

## 9. Edge Cases

| Case | Behavior |
|---|---|
| **Same browser visits two tenants' sites** | Same `session_id`, but rows are tenant-scoped. Registering on tenant A must migrate **only** tenant A's rows. See §8 |
| localStorage cleared mid-session | The old favorites are orphaned (unreachable, harmless). A new session ID is generated. Accept it — this is the honest cost of anonymous saves, and it's exactly the argument for registering |
| Private/incognito browsing | Favorites vanish on window close. Expected |
| Favoriting the same property anonymously and again after login | Needs `UNIQUE (tenant_id, property_id, coalesce(user_id, session_id))` — **not currently in the schema.** Without it, migration creates duplicate rows |
| Migration partially fails | It's one transaction — all or nothing. A partial migration (favorites moved, requirement profile lost) is the worst possible outcome |
| Registration succeeds but migration fails | The user is registered with an empty portal after being promised otherwise. **Migration must be inside the registration transaction**, not a fire-and-forget follow-up |
| Orphaned session rows | Anonymous `favorites`/`requirement_profiles` accumulate forever. A cleanup job (rows with `user_id IS NULL` older than N days) is worth having — but retention isn't defined anywhere (`03-database-schema.md` §6 flags this for `chat_messages` too) |

---

## 10. Acceptance Criteria

| ID | Case | Source |
|---|---|---|
| — | Favorite anonymously → register → the favorite is in the portal (FR4.4) | `13-ui-ux-flows.md` §2.1 |
| — | Favoriting never presents a login wall *before* the action | FR4.4 |
| — | Complete the requirement wizard anonymously → register → the profile is saved | FR3.3 |
| — | A browser that visited two tenants and registers on one migrates **only** that tenant's rows | Cross-tenant test |
| — | Customer A cannot delete Customer B's favorite by property ID | Security test |
| — | `X-Session-Id` alone cannot read `/portal/*` | Security test |

---

## 11. Open Questions

- [ ] **BLOCKING — `leads` has no `user_id`/`session_id`** (§5). Fix `03-database-schema.md` before Sprint 4.
- [ ] **No uniqueness constraint on `favorites`** — migration will create duplicates. Add `UNIQUE (tenant_id, property_id, coalesce(user_id, session_id))`.
- [ ] **Merge rules on login (§4.1)** are open in `08-auth-roles-spec.md` §6. The recommendation is "keep more, not less" — needs product sign-off.
- [ ] **Retention for orphaned anonymous rows** — undefined. Ties to the open retention question in `03-database-schema.md` §6.
- [ ] Whether the session ID should be an HttpOnly cookie rather than localStorage + a header. A cookie is harder to steal via XSS, but the current API spec commits to the `X-Session-Id` header. Not urgent — a session ID is not a credential — but worth a deliberate decision.
