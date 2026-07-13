# Page: Lead Detail Panel

> **Route:** `/admin/leads/:id` — rendered as a **slide-over panel** over the board, not a full page · **PRD Module:** 10
> Part of [Doc 17 — Admin Spec](README.md). Read [`README.md` §4](README.md#4-cross-cutting-rules-for-every-admin-page) first.

---

## 1. Purpose & Traceability

Everything about one person and one deal, in one place: who they are, what they want, what's been said, and what happens next.

**It is a panel, not a page.** The agent opens it, logs a call, sets a reminder, closes it, and drags the card — all without losing the board. A full-page navigation would break the working rhythm of the person who uses this fifty times a day.

| Requirement | Source |
|---|---|
| FR10.3 Notes, call logs, and follow-up reminders per lead | `01-prd.md` §11 |
| FR10.4 Lead source tracking | `01-prd.md` §11 |
| FR1.7 Chatbot escalations reach an agent | `01-prd.md` §2 |
| Acceptance: stage changes are timestamped for reporting | `01-prd.md` §11 |
| Screen workflow | `14-screen-workflows.md` §8 |

---

## 2. Entry & Exit Points

**Entry:** a card on the [Kanban board](07-leads-kanban.md); a row in the [table view](09-leads-table-and-assignment.md); a Dashboard activity item, deep-linked; a "new lead" notification.

**Exit:** close the panel (back to the board, unchanged). Or the property link → [property edit](04-property-add-edit.md).

---

## 3. Layout & Regions

```
                    ┌──────────────────────────────────────────────┐
                    │  Priya Sharma                          [ × ] │
   board            │  ┌────────────────────────────────────────┐  │
   (still           │  │ 📞 +91 98xxx xxxxx      [ Call ]       │  │
    visible,        │  │ ✉  priya@example.com                   │  │
    dimmed)         │  └────────────────────────────────────────┘  │
                    │                                              │
                    │  Stage    [ Contacted        ▾ ]             │
                    │  Owner    [ Anjali           ▾ ]             │
                    │  Source   💬 Chatbot        ← how they came  │
                    │  Property Sunview Residences · ₹78L          │
                    │                                              │
                    │  ┌── WHAT THEY WANT ────────────────────┐    │
                    │  │ From their requirement profile:      │    │
                    │  │ 3BHK · ₹50–80L · Whitefield          │    │
                    │  │ Self-use · within 3 months           │    │
                    │  │ Must-have: parking, gym              │    │
                    │  └──────────────────────────────────────┘    │
                    │       ↑ GOLD. The agent knows what to        │
                    │         pitch before dialling.               │
                    │                                              │
                    │  ┌── TIMELINE ──────────────────────────┐    │
                    │  │ 💬 Chat transcript (12 messages) ▾   │    │
                    │  │    "Is Sunview available for a Nov   │    │
                    │  │     move-in?" …                      │    │
                    │  │ ● 12 Jul  Lead created (chatbot)     │    │
                    │  │ ● 13 Jul  Stage → Contacted (Anjali) │    │
                    │  │ 📝 13 Jul  Called. Wants a weekend   │    │
                    │  │            viewing. Budget is firm.  │    │
                    │  └──────────────────────────────────────┘    │
                    │                                              │
                    │  ┌── ADD A NOTE ────────────────────────┐    │
                    │  │ [                                  ] │    │
                    │  │ Follow up on: [ 16 Jul ▾ ]  [ Save ] │    │
                    │  └──────────────────────────────────────┘    │
                    └──────────────────────────────────────────────┘
```

| Region | Contents |
|---|---|
| Contact header | Name, **phone (the primary action — make it click-to-call)**, email |
| Stage / Owner | Editable inline. Changing the stage here does exactly what dragging does |
| Source | How the lead arrived (FR10.4) — sets the agent's opening line |
| **What they want** | The linked `requirement_profile`, if any. **The highest-value block on the panel** and the clearest payoff of the AI features feeding the CRM: the agent already knows the budget, the area, and the deadline |
| Timeline | A **merged** stream: `lead_activities` (stage changes) + `lead_notes` (agent notes) + the chat transcript if the lead came from the bot |
| Add a note | Note text + an optional follow-up date (FR10.3) |

---

## 4. Workflow

```
Agent clicks a lead card
   │
   ▼
GET /admin/leads/{id}   → lead + notes + activity timeline
   │
   ▼
Panel slides in (the board stays behind it)
   │
   ├─→ Taps the phone number → click-to-call (tel:)
   │        │
   │        ▼
   │   Call happens
   │        │
   │        ▼
   │   Logs a note: "Called. Wants a weekend viewing."     [FR10.3]
   │   Sets a follow-up: 16 Jul
   │        │
   │        ▼
   │   POST /admin/leads/{id}/notes { note_text, follow_up_at }
   │
   ├─→ Changes the stage in the dropdown
   │        → PATCH /admin/leads/{id}/stage
   │        → a lead_activities row is written (timestamped)
   │        → the card moves on the board behind the panel
   │
   ├─→ Reassigns the owner (admin only)
   │        → PATCH /admin/leads/{id}/assign
   │
   └─→ Reads the chat transcript (if source = chatbot)
            · The visitor already told the bot everything. Making the
              agent re-ask is the fastest way to look incompetent.
            │
            ▼
        ⚠ ESCALATED CONVERSATIONS: the visitor is waiting for a human
          reply IN the chat widget. But there is NO endpoint for an
          agent to send a message into that conversation (Gap A2).
          The escalation arrives, and the agent... calls them instead.
          The chat loop never closes. See §11.
```

---

## 5. States

| State | Behavior |
|---|---|
| Loading | Skeleton panel |
| Lead with no property | The property block is hidden (a general contact-form lead) |
| Lead with no requirement profile | The "what they want" block is hidden. Most walk-in and contact-form leads won't have one |
| Lead from the chatbot | The transcript is available, collapsed by default, expandable |
| **Escalated chat** | Flag it hard (`color-coral`). This is the only genuinely real-time item in the CRM — someone is *waiting right now*. It should look different from every other lead |
| Follow-up overdue | Highlight it. An overdue reminder that looks identical to a future one is a reminder that doesn't work |
| Note saving | Optimistic append; revert on failure |
| Agent viewing someone else's lead | Read-only, or 403 — depending on the tenant's policy (see [07](07-leads-kanban.md) §11) |

---

## 6. API Calls

| Trigger | Call | Notes |
|---|---|---|
| Open | `GET /admin/leads/{id}` | Lead + notes + activity timeline. `04-api-spec.md` §9 |
| Add a note / reminder | `POST /admin/leads/{id}/notes` | `{note_text, follow_up_at}` |
| Change stage | `PATCH /admin/leads/{id}/stage` | |
| Reassign | `PATCH /admin/leads/{id}/assign` | Admin only |
| Read the chat transcript | `GET /ai/chat/history/{conversation_id}` | ⚠ a **public** endpoint. An admin reading it needs the conversation ID — and `leads` has no link to `chat_conversations`. See §9 |
| **Reply in an escalated chat** | *(none)* | **Gap A2 — the escalation loop is open** |

---

## 7. Data Touched

| Table | Access |
|---|---|
| `leads` | Read / Update (`stage`, `assigned_agent_id`) |
| `lead_notes` | Read / Write (**internal only — never customer-visible**) |
| `lead_activities` | Read / Write (the stage-change trail) |
| `requirement_profiles` | Read ("what they want") — ⚠ **no FK from `leads` links them** (§9) |
| `chat_conversations`, `chat_messages` | Read (the transcript) — ⚠ **no FK from `leads` links them either** |
| `properties` | Read |
| `users` | Read (owner dropdown) |

---

## 8. Roles & Permissions

| Action | `agent` (assigned) | `agent` (not assigned) | `admin` |
|---|---|---|---|
| View the lead | ✅ | ⚠ open (§11) | ✅ |
| Add a note | ✅ | ❌ | ✅ |
| Change the stage | ✅ | ❌ (403) | ✅ |
| Reassign | ❌ | ❌ | ✅ |
| Read the chat transcript | ✅ | ❌ | ✅ |

**`lead_notes` are internal.** They contain candid commercial judgments ("lowballing, not serious", "husband is the real decision-maker"). They must **never** be returned by any customer-facing endpoint. The portal's `LeadOut` schema and the admin's must be **separate Pydantic models** — not one model with fields the frontend is trusted to hide (`.claude/rules/backend.md`).

---

## 9. Validation & Edge Cases

- **The lead ↔ requirement_profile link doesn't exist.** `leads` has no `requirement_profile_id`, and `requirement_profiles` has no `lead_id`. So the panel's most valuable block — *what this person actually wants* — **cannot be populated.** The only join available is `session_id`/`user_id`, and `leads` has neither (Gap A10). **This is a schema gap with direct commercial consequence**, not a nicety: it's the difference between an agent who opens the call knowing the budget and one who doesn't.
- **The lead ↔ chat_conversation link doesn't exist either.** A lead with `source = 'chatbot'` has no pointer back to the conversation that produced it. The transcript is right there in the database and the agent can't reach it.
- **Follow-up reminders have no delivery mechanism.** `lead_notes.follow_up_at` is stored — but nothing reads it and nothing notifies the agent when it comes due. A reminder that doesn't remind is just a date in a database. This needs a scheduled job + the notification system (which itself has no table — customer Gap G1).
- **Notes are append-only.** No editing, no deleting — this is a CRM audit trail. (Or if editing is allowed, keep the history.)
- **XSS:** `note_text` is written by an admin, but the lead's own `message` field came from an **anonymous public form** and is rendered right here in the admin's browser. Escape on output ([customer 15](../16-customer-spec/15-feature-lead-capture.md) §9).
- **Deleted agent:** a lead assigned to a deactivated user must not become invisible. Show "Unassigned (was Ravi)" and let it be reassigned.

---

## 10. Acceptance Criteria

| ID | Case | Source |
|---|---|---|
| TC-LEAD-02 | Notes and follow-up reminders save and appear on the timeline | Sprint 4 |
| TC-LEAD-03 | A stage change here writes a timestamped `lead_activities` row | Sprint 4 |
| TC-CHAT-04 | An escalated conversation is visible to the assigned agent | Sprint 6 |
| TC-ROLE-01 | An agent cannot open or modify another agent's lead (403) | Sprint 8 |
| — | `lead_notes` never appear in any customer-facing API response | Security test |

---

## 11. Open Questions

- [ ] **BLOCKING for this panel's value — `leads` links to nothing.** No `requirement_profile_id`, no `chat_conversation_id`, no `user_id` (Gap A10). Add them to `03-database-schema.md`. Without them, this screen is a contact card with notes, and the "AI-first CRM" story doesn't reach the agent — which is the entire pitch.
- [ ] **Gap A2 — no way for an agent to reply in an escalated chat.** FR1.7 promises escalation; nothing delivers a human response back into the widget. Needs an endpoint *and* a delivery channel (Supabase Realtime? polling?). Resolve in `05-ai-chatbot-spec.md` + `04-api-spec.md`.
- [ ] **Follow-up reminders don't fire.** Needs a scheduled job and a notification channel. Currently they're decorative.
- [ ] **Can an agent view (read-only) a colleague's lead?** Affects both this panel and the board. Open in `08-auth-roles-spec.md` §6.
- [ ] Call logging: is `note_text` enough (FR10.3 says "notes, call logs"), or does a call need structured fields (duration, outcome, follow-up)? Structured call outcomes would make the agent-performance metrics in [10](10-agents.md) far more meaningful.
