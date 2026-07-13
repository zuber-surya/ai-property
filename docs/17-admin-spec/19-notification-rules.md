# Page: Notification Rules

> **Route:** `/admin/settings/notifications` · **PRD Module:** 15 · **App:** `admin-portal/` → `pages/Settings/Notifications`
> Part of [Doc 17 — Admin Spec](README.md). Read [`README.md` §4](README.md#4-cross-cutting-rules-for-every-admin-page) first.

---

## 1. Purpose & Traceability

Decides **who gets told what, and how**, when something happens inside the tenant's workspace. A new lead at 9pm is worthless if the agent finds out on Thursday.

Note the distinction from the customer side: this configures notifications to **staff** (`notification_rules`). The **customer's** notification preferences are a separate concern with separate storage ([customer 11](../16-customer-spec/11-portal-notifications.md)) — and both are currently unbuildable for related reasons.

| Requirement | Source |
|---|---|
| FR15.2 Configurable notification rules (event → channel → recipients) for events like new lead or listing expiring | `01-prd.md` §16 |

---

## 2. Entry & Exit Points

**Entry:** sidebar → Settings → Notifications; the new-tenant onboarding checklist (**"tell us where to send new leads" is one of the first things a tenant must configure**, or their leads land silently in a CRM nobody has open).

**Exit:** [Users](11-users-roles.md) (to add a recipient).

---

## 3. Layout & Regions

```
┌──────────┬────────────────────────────────────────────────────────────┐
│ SIDEBAR  │  Settings   [Branding] [▪Notifications]                    │
│          │                                                            │
│          │  Tell the right people when something happens.             │
│          │                                    [ + New rule ]          │
│          │                                                            │
│          │  ┌──────────────────────────────────────────────────────┐  │
│          │  │ When…            │ Send via │ To…          │ On  │⋯ │  │
│          │  ├──────────────────────────────────────────────────────┤  │
│          │  │ A new lead       │ Email    │ Assigned     │ ✅  │⋯ │  │
│          │  │ arrives          │ + In-app │ agent        │     │  │  │
│          │  ├──────────────────────────────────────────────────────┤  │
│          │  │ A chat is        │ Email    │ All agents   │ ✅  │⋯ │  │
│          │  │ escalated 🔴     │ + SMS    │              │     │  │  │
│          │  ├──────────────────────────────────────────────────────┤  │
│          │  │ A lead sits in   │ Email    │ Admins       │ ✅  │⋯ │  │
│          │  │ "New" for 48h    │          │              │     │  │  │
│          │  ├──────────────────────────────────────────────────────┤  │
│          │  │ A listing is     │ In-app   │ Admins       │ ☐   │⋯ │  │
│          │  │ pending approval │          │              │     │  │  │
│          │  └──────────────────────────────────────────────────────┘  │
│          │                                                            │
│          │  ┌─ New rule ─────────────────────────────────────────┐    │
│          │  │  When   [ A new lead arrives          ▾ ]          │    │
│          │  │  Send   ☑ Email   ☐ SMS   ☑ In-app                │    │
│          │  │  To     ( ) The assigned agent                     │    │
│          │  │         (•) Specific people [ Vikram × ][ + ]      │    │
│          │  │         ( ) Everyone with role [ Admin ▾ ]         │    │
│          │  │                            [ Save rule ]           │    │
│          │  └────────────────────────────────────────────────────┘    │
└──────────┴────────────────────────────────────────────────────────────┘
```

| Region | Maps to |
|---|---|
| Rule row | `notification_rules` (`event_type`, `channel`, `recipients` jsonb, `is_active`) |
| Event dropdown | See §4.1 — **the event catalogue is undefined** |
| Channel | Email / SMS / In-app. **Email and SMS need a provider that hasn't been chosen** |
| Recipients | The assigned agent · specific users · a role. `recipients` is a jsonb of "user IDs or role targets" |

---

## 4. Workflow

```
Admin opens Settings → Notifications
   │
   ▼
GET /admin/notification-rules
   │
   ▼
[ + New rule ]  →  event + channels + recipients  →  POST /admin/notification-rules
   │
   ▼
Rule is live
   │
   ▼
Later: a visitor submits an inquiry on the public site
   │
   ▼
Lead is created  (15-feature-lead-capture.md)
   │
   ▼
The lead service evaluates the tenant's active notification_rules
   │
   ├─ event_type = 'new_lead' matches
   │        │
   │        ▼
   │   Resolve the recipients (assigned agent / specific users / role)
   │        │
   │        ▼
   │   Dispatch per channel:
   │        · in-app → write a notification row  ⚠ no table (customer G1)
   │        · email  → queue                     ⚠ no provider chosen
   │        · SMS    → queue                     ⚠ no provider chosen
   │
   ▼
The agent finds out. Which is the entire point — a CRM that captures
leads and tells nobody is a very expensive spreadsheet.
```

### 4.1 The Event Catalogue — undefined

FR15.2 names two examples ("new lead", "listing expiring"). `notification_rules.event_type` is a free-text column. **Nothing enumerates the valid events**, so the dropdown above can't be built without inventing them.

Reasonable set (**needs adding to `01-prd.md`**):

| Event | Fires when | Notes |
|---|---|---|
| `new_lead` | A lead is created | The essential one |
| `lead_escalated` | The chatbot escalates (FR1.7) | **Time-critical** — a person is waiting |
| `lead_stale` | A lead sits in a stage past a threshold | Needs a scheduled job |
| `lead_assigned` | A lead is assigned to an agent | |
| `property_pending_approval` | Submitted for approval (FR9.3) | |
| `listing_expiring` | Named in FR15.2 — but **`properties` has no expiry date**, so this event cannot fire | ⚠ |
| `follow_up_due` | A `lead_notes.follow_up_at` comes due (FR10.3) | **Currently reminders never fire at all** ([08](08-lead-detail.md) §9) |

---

## 5. States

| State | Behavior |
|---|---|
| **Empty (new tenant)** | **The most dangerous empty state in the product.** No rules means leads arrive and nobody is told. **Seed a default rule on tenant creation** — "new lead → email → assigned agent" — rather than leaving it to a tenant who doesn't know they need it |
| Rule with no valid recipients | Flag it. A rule pointing at a deactivated user silently notifies nobody |
| Channel unavailable | If no email/SMS provider is configured, **disable those channels with a reason** rather than letting an admin build a rule that quietly does nothing |
| Rule disabled | `is_active = false`. Keep it — disabling is safer than deleting |

---

## 6. API Calls

| Trigger | Call | Notes |
|---|---|---|
| Mount | `GET /admin/notification-rules` | `04-api-spec.md` §14 |
| Create | `POST /admin/notification-rules` | |
| Update / toggle | `PUT /admin/notification-rules/{id}` | |
| Delete | *(none)* | Not in the spec — but `is_active = false` covers it |
| **Test a rule** | *(none)* | "Send me a test" is the only way an admin can trust this page. Worth adding |

---

## 7. Data Touched

| Table | Access |
|---|---|
| `notification_rules` | Read / Write |
| `users` | Read (recipient picker; role resolution) |
| *`notifications`* | Write on dispatch — **doesn't exist (customer Gap G1)** |
| *email/SMS queue* | **No provider chosen** |

---

## 8. Roles & Permissions

| Action | `agent` | `admin` | `super_admin` |
|---|---|---|---|
| View / create / edit rules | ❌ | ✅ | ✅ |

Admin-only, tenant-scoped. **Recipients must be validated against the tenant's own users** — a rule naming a user ID from another tenant would leak lead data (name, phone, property interest) across a tenant boundary by *email*, which is both the worst kind of leak and the hardest to walk back. `recipients` is a jsonb blob of IDs, so **nothing structurally prevents this** — it must be validated on write *and* on dispatch.

---

## 9. Validation & Edge Cases

- **Recipient in another tenant** — reject on write, re-check on dispatch (§8).
- **Deactivated recipient** — skip them, and flag the rule as needing attention. Don't fail the whole dispatch.
- **A rule with no recipients** — reject. It does nothing.
- **Notification storms:** a [bulk upload](05-property-bulk-upload.md) of 200 properties, each triggering `property_pending_approval`, produces 200 emails to the same admin in one minute. **Batch and rate-limit per recipient per window.** This is the same storm problem as the customer side, and it will absolutely happen in week one of a real onboarding.
- **Dispatch failures must not break the triggering action.** If the email provider is down, the lead still gets created. **Notifications are a side effect and must be dispatched outside the critical transaction** — queued, retried, and failing loudly in logs but silently to the user.
- **Duplicate notifications:** a lead that's created *and* auto-assigned in the same request might match both `new_lead` and `lead_assigned`. Dedupe per recipient per event per entity.
- **SMS costs money per send.** A misconfigured rule ("SMS all agents on every new lead") on a busy tenant is a bill. Default SMS to off, and consider a cap.

---

## 10. Acceptance Criteria

| ID | Case | Source |
|---|---|---|
| — | Creating a `new_lead` rule causes the assigned agent to be notified when a lead arrives (FR15.2) | `01-prd.md` §16 |
| — | A rule cannot name a recipient from another tenant | Security test |
| — | 200 properties imported at once do not produce 200 separate emails | §9 |
| — | An email-provider outage does not prevent lead creation | §9 |
| TC-ROLE-01 | An agent cannot view or edit notification rules (403) | Sprint 8 |

---

## 11. Open Questions

- [ ] **No email/SMS provider is chosen anywhere** (`10-deployment-devops.md` doesn't name one). Without it, only the in-app channel can work — and in-app needs the `notifications` table that doesn't exist either (customer Gap G1). **As specified, this entire module currently notifies nobody through any channel.** That is the single biggest functional hole in the admin portal: leads get captured and nobody is told.
- [ ] **The event catalogue is undefined** (§4.1) — add it to `01-prd.md`.
- [ ] **`listing_expiring` is named in FR15.2, but `properties` has no expiry date.** Either add one or drop the example.
- [ ] **Scheduled/time-based events** (`lead_stale`, `follow_up_due`, `listing_expiring`) need a **job scheduler**. Nothing in `02-architecture.md` or `10-deployment-devops.md` provides one. This also blocks follow-up reminders ([08](08-lead-detail.md)) — a feature agents will assume works.
- [ ] Whether admins can customize the **message template** per rule, or only the routing.
- [ ] A "send me a test notification" action (§6) — small, and the difference between a page an admin trusts and one they don't.
