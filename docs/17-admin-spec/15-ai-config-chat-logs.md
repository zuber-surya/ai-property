# Page: AI Configuration — Conversation Logs

> **Route:** `/admin/ai-config/chat-logs` · **PRD Module:** 13 · **App:** `admin-portal/` → `pages/AIConfig/ChatLogs`
> Part of [Doc 17 — Admin Spec](README.md). Read [`README.md` §4](README.md#4-cross-cutting-rules-for-every-admin-page) first.

---

## 1. Purpose & Traceability

**The feedback loop that makes the chatbot good.** Everything else about the bot — the prompt, the model, the tools — is guesswork until someone reads what it actually said to real people.

This screen is where a tenant admin discovers that the bot has been confidently telling visitors about a "clubhouse" that doesn't exist, or that 40% of conversations die at the same unanswered question. Then they go fix the [FAQ](13-ai-config-chatbot.md). That loop *is* the product's quality mechanism.

| Requirement | Source |
|---|---|
| FR13.2 Conversation log viewer with flagging for review | `01-prd.md` §14 |
| FR1.8 All conversations are logged for admin review | `01-prd.md` §2 |
| Logging detail | `05-ai-chatbot-spec.md` §11 |

---

## 2. Entry & Exit Points

**Entry:** sidebar → AI Config → Logs; a Dashboard activity item ("chatbot escalation"); after saving a chatbot config change (*"did that help?"*).

**Exit:** the [chatbot config](13-ai-config-chatbot.md) (to fix what you just found); the [lead](08-lead-detail.md) a conversation produced.

---

## 3. Layout & Regions

```
┌──────────┬────────────────────────────────────────────────────────────┐
│ SIDEBAR  │  AI Config   [Chatbot] [Recommendation] [▪Logs] [Search]   │
│          │                                                            │
│          │  ┌── LAST 7 DAYS ─────────────────────────────────────┐    │
│          │  │  312 conversations · 58 leads (18.6%) ·            │    │
│          │  │  41 escalated (13.1%) · 12 flagged                 │    │
│          │  └────────────────────────────────────────────────────┘    │
│          │                                                            │
│          │  Status:[All ▾] Outcome:[All ▾] [☐ Flagged only]           │
│          │                                                            │
│          │  ┌──────────────────────────────────────────────────────┐  │
│          │  │ When   │Msgs│ Outcome         │ Preview       │ ⚑   │  │
│          │  ├──────────────────────────────────────────────────────┤  │
│          │  │ 2h ago │ 12 │ ✅ Lead created │"Is Sunview…"  │     │  │
│          │  │ 3h ago │  4 │ ⚠ Escalated     │"I want to     │ ⚑   │  │
│          │  │        │    │                 │ speak to a…"  │     │  │
│          │  │ 5h ago │  2 │ ○ Abandoned     │"do you have   │     │  │
│          │  │        │    │                 │ anything in…" │     │  │
│          │  └──────────────────────────────────────────────────────┘  │
│          │                                                            │
│          │  ── Transcript ──────────────────────────────────────────  │
│          │                                                            │
│          │   👤 Is Sunview Residences still available?                │
│          │                                                            │
│          │   🤖 [ 🔧 lookup_property(property_id: "a3f…") ]           │
│          │      Yes — Sunview Residences is available at ₹78,00,000.  │
│          │      Would you like to schedule a visit?                   │
│          │      ↑ tool calls shown inline. THIS is how you verify the │
│          │        bot used live data instead of making it up.         │
│          │                                                            │
│          │   👤 Yes, this weekend                                     │
│          │                                                            │
│          │   🤖 [ 🔧 create_lead(...) ] Great — I've passed your      │
│          │      details to Anjali.                                    │
│          │                                                            │
│          │   [ ⚑ Flag for review ]     [ View the lead → ]            │
└──────────┴────────────────────────────────────────────────────────────┘
```

| Region | Contents |
|---|---|
| Summary bar | Conversations, lead-conversion rate, **escalation rate**, flagged count. The escalation rate is the number to watch: rising means the bot is failing |
| Filters | Status (`active`/`escalated`/`closed`), outcome (lead / escalated / abandoned), flagged-only |
| Transcript | The full conversation with **tool calls rendered inline** (from `chat_messages.metadata`) |
| Flag | Mark for review (FR13.2) |

**Rendering the tool calls is the point.** A transcript that just shows the bot's words can't tell you whether "₹78,00,000" came from the database or from the model's imagination. `chat_messages.metadata` records the tool calls (`05-ai-chatbot-spec.md` §11) — surface them, and the "never invent property facts" rule (FR1.3) becomes *verifiable* instead of aspirational.

---

## 4. Workflow

```
Admin opens Chat Logs
   │
   ▼
GET /admin/ai-config/chat-logs  → conversations (paginated)
   │
   ▼
Reviews the summary: "escalation rate 13.1%" — is that bad?
   │   (it needs a baseline to mean anything — see §11)
   ▼
Filters to Escalated
   │
   ▼
Opens a transcript
   │
   ├─→ Reads what actually happened
   │        │
   │        ├─ The bot couldn't answer "do you handle rentals in Indiranagar?"
   │        │        │
   │        │        ▼
   │        │   → go add it to the FAQ                            [→ 13]
   │        │
   │        ├─ The bot invented a fact (no tool call in the metadata)
   │        │        │
   │        │        ▼
   │        │   → ⚑ FLAG. This is a prompt/model bug, not a config
   │        │     problem. It belongs in the golden test set
   │        │     (05-ai-chatbot-spec.md §12), not in an FAQ entry.
   │        │
   │        └─ The visitor asked for a human and got one
   │                 │
   │                 ▼
   │            → fine. That's the system working.
   │
   └─→ ⚠ An ESCALATED conversation is a person waiting for a reply.
         There is NO WAY to reply from here (Gap A2). The admin reads
         the escalation, and... phones them. The chat window the
         visitor is staring at stays silent.
```

---

## 5. States

| State | Behavior |
|---|---|
| Loading | Skeleton |
| Empty | "No conversations yet." For a new tenant, expected |
| Escalated, unhandled | **Visually loud** — the `error` family (`DESIGN.md` → Semantic Status Colors). Someone is waiting *right now*. This is the only real-time item in the admin portal, and it should not look like a log entry |
| Flagged | Persists in the flagged filter until cleared |
| Long conversation | Virtualize; jump-to-tool-call would be a genuinely useful affordance |
| Conversation → lead | Link to the lead ([08](08-lead-detail.md)) |
| Anonymous conversation | No user identity. That's the normal case, and the transcript is still the whole value |

---

## 6. API Calls

| Trigger | Call | Notes |
|---|---|---|
| Mount / filter | `GET /admin/ai-config/chat-logs` | Browse/flag conversation logs. `04-api-spec.md` §12 |
| Open a transcript | `GET /admin/ai-config/chat-logs/{id}` | ⚠ **not explicitly in the API spec** — the spec has a list endpoint, no detail endpoint |
| Flag | *(none)* | FR13.2 says "with flagging for review". **No endpoint, and no `flagged` column on `chat_conversations`.** See §11 |
| **Reply to an escalated chat** | *(none)* | **Gap A2** |

---

## 7. Data Touched

| Table | Access |
|---|---|
| `chat_conversations` | Read (status, outcome). ⚠ **no `flagged` column** |
| `chat_messages` | Read (transcript + `metadata` tool calls) |
| `leads` | Read (the lead a conversation produced) — ⚠ **no FK links them** ([08](08-lead-detail.md) §9) |
| `properties` | Read (properties referenced in the conversation) |

---

## 8. Roles & Permissions

| Action | `agent` | `admin` | `super_admin` |
|---|---|---|---|
| View chat logs | ⚠ open (§11) | ✅ | ✅ |
| Flag | ❌ | ✅ | ✅ |

- **Tenant-scoped, absolutely.** Chat transcripts contain visitors' names, phone numbers, budgets, and life circumstances ("we're relocating for my wife's job"). A cross-tenant leak here is a privacy incident, not a bug.
- **Should agents see chat logs?** They'd benefit from reading the conversation that produced their lead (it's a briefing). But that's an argument for surfacing the transcript **on the lead detail panel** ([08](08-lead-detail.md)), scoped to their own leads — **not** for giving agents a window into every visitor conversation on the site. Different question, different answer.

---

## 9. Validation & Edge Cases

- **Transcripts are PII.** Names, phones, budgets, plans. Tenant-owned, RLS-protected, and covered by whatever retention policy gets decided (`03-database-schema.md` §6 flags `chat_messages` retention as open — **this is where that question gets real**).
- **Bot output is rendered in the admin's browser.** The model's reply is text, but it may echo user-supplied content. **Escape it.** A visitor who types `<script>` into the chat should not get script execution in the admin's browser via the transcript view. This is a genuine XSS path and an easy one to miss, because "it's just the bot's reply" feels safe.
- **A conversation with no messages** (the widget was opened and abandoned): don't list it. It's noise.
- **Distinguishing "abandoned" from "closed":** `chat_conversations.status` has `active`/`escalated`/`closed`, with no notion of abandonment. A visitor who closes the tab leaves the conversation `active` forever. **So the "abandoned" outcome in the UI above cannot actually be computed** — it needs either a timeout-to-closed job or a new status.
- **Escalation rate needs a baseline.** "13.1%" is meaningless without knowing what's normal. Show a trend line (vs. last week) rather than a bare number — a rising rate is the signal; the absolute value isn't.

---

## 10. Acceptance Criteria

| ID | Case | Source |
|---|---|---|
| TC-CHAT-04 | Escalated conversations are visible here and to the assigned agent | Sprint 6 |
| TC-AICONFIG-01 | Conversations are logged with their tool calls and are reviewable | Sprint 8 |
| TC-TENANT-01 | Tenant A's admin can never read tenant B's transcripts | Sprint 1 |
| — | A transcript shows the tool calls, so an invented fact is **detectable** | FR1.3 + `05-ai-chatbot-spec.md` §11 |
| — | A `<script>` typed by a visitor does not execute in the admin's transcript view | Security test |

---

## 11. Open Questions

- [ ] **Flagging (FR13.2) has no column and no endpoint.** Add `flagged boolean` (+ maybe `flag_reason`) to `chat_conversations` and a `PATCH` route. It's in the requirement and in the page's name; it just doesn't exist anywhere else.
- [ ] **No conversation-detail endpoint** — only the list. Add it to `04-api-spec.md`.
- [ ] **Gap A2 — no way to reply to an escalated conversation.** The bot promises the visitor a human; the human has no way to speak. **This is the largest functional hole in the chatbot feature**, and it spans `05-ai-chatbot-spec.md` (needs a delivery channel) and `04-api-spec.md` (needs an endpoint).
- [ ] **"Abandoned" is not modeled** (§9) — so the outcome filter can't be built as drawn.
- [ ] **Retention for `chat_messages`** — open in `03-database-schema.md` §6, and this screen is what makes it a real decision. Transcripts are the highest-value debugging data in the product *and* the most sensitive PII in it. Those pull in opposite directions.
- [ ] Whether agents get read access to the transcript of **their own** leads (recommended — see §8).
