# Page: Agent Chat Console

> **Route:** `/admin/chat` · **PRD Module:** 1 (FR1.7) + 10 · **App:** `admin-portal/` → `pages/ChatConsole/`
> Part of [Doc 17 — Admin Spec](README.md). Read [`README.md` §4](README.md#4-cross-cutting-rules-for-every-admin-page) first.

---

## 1. Purpose & Traceability

**The screen where the chatbot's promise becomes true.** The bot tells a visitor *"I've looped in one of our agents"* — this is where that agent actually shows up.

Until now it didn't exist, and neither did the endpoints. `POST /ai/chat/escalate` handed a conversation to a human and **nothing let the human reply** (gap G7). FR1.7 promised a handoff the system could not perform.

| Requirement | Source |
|---|---|
| FR1.7 Bot escalates to human agent handoff | `01-prd.md` §2 |
| Acceptance: **"Escalation requests are visible to an agent in real time or near-real time"** | `01-prd.md` §2 |
| The handoff state machine | `05-ai-chatbot-spec.md` §10A |
| The four endpoints | `04-api-spec.md` §12A |

**This is the only genuinely real-time screen in the admin portal.** Everywhere else, a stale view costs someone a few minutes. Here, **a person is sitting in a chat window right now, waiting.**

---

## 2. Entry & Exit Points

**Entry:** the left nav (**with an unread/waiting badge** — this is the one nav item that must shout); the escalation row on the dashboard activity feed; a "View conversation →" link from the chat logs ([15](15-ai-config-chat-logs.md)) or a lead ([08](08-lead-detail.md)).

**Exit:** close the conversation; or jump to the linked lead / property.

**Who:** `agent` and `admin`. An agent sees their own tenant's queue — never another tenant's transcripts (`04-api-spec.md` §12A.5).

---

## 3. Layout & Regions

```
┌──────────┬────────────────────────┬──────────────────────────────────┐
│ SIDEBAR  │  QUEUE                 │  CONVERSATION                    │
│          │                        │                                  │
│  Chat ●3 │  ⚠ 3 waiting           │  Priya Sharma · +91 98xxx xxxxx  │
│          │                        │  Sunview Residences   [View →]   │
│          │  ┌──────────────────┐  │  ─────────────────────────────   │
│          │  │ Priya S.    14m🔴│  │                                  │
│          │  │ "I want to speak │  │  👤 Is Sunview still available?  │
│          │  │  to someone..."  │  │                                  │
│          │  │ 7 msgs  [ Take ] │  │  🤖 [🔧 lookup_property(a3f…)]   │
│          │  └──────────────────┘  │     Yes — ₹78,00,000. Would you  │
│          │  ┌──────────────────┐  │     like to schedule a visit?    │
│          │  │ Ravi K.      3m  │  │                                  │
│          │  │ "do you do home  │  │  👤 I'd rather talk to a person  │
│          │  │  loans?"         │  │                                  │
│          │  │ 2 msgs  [ Take ] │  │  🤖 I've looped in one of our    │
│          │  └──────────────────┘  │     agents — they'll respond     │
│          │  ┌──────────────────┐  │     shortly.                     │
│          │  │ Meera N.  ● mine │  │     ── escalated 14m ago ──      │
│          │  │ (you're handling)│  │                                  │
│          │  └──────────────────┘  │  🙋 Anjali: Hi Priya — happy to  │
│          │                        │     help. Are you free Saturday? │
│          │                        │                                  │
│          │                        │  ┌────────────────────────────┐  │
│          │                        │  │ Type your reply…      [→]  │  │
│          │                        │  └────────────────────────────┘  │
│          │                        │  [ Close conversation ]          │
└──────────┴────────────────────────┴──────────────────────────────────┘
```

| Region | Contents |
|---|---|
| **Queue** | Escalated conversations. **Unclaimed first, sorted by wait time, longest at the top.** Each: visitor name, **waiting time**, a preview of what they said, message count, and a **Take** button. Conversations you're already handling are marked and sorted below. |
| **Waiting time** | **The most important number on the screen.** It goes red past a threshold. It is what turns "a queue" into "someone is waiting". |
| **Conversation** | The full transcript — bot turns, tool calls, and the human turns — plus the visitor's contact details and the property in play. |
| **Composer** | Only enabled once **you** have claimed the conversation. |

### 3.1 The three voices must look different

This screen is the one place all three appear together, and confusing them is the worst thing it can do.

| Voice | Treatment |
|---|---|
| 👤 **Visitor** | Plain. Neutral surface. |
| 🤖 **Bot** | **`tertiary`** — it is model output. Tool calls rendered **inline** (`[🔧 lookup_property(id: "a3f…")]`), because that is how you verify the bot used live data instead of inventing it. |
| 🙋 **Agent** | **Never `tertiary`.** A human wrote it. Attribute it by name. |

> **This is the sharpest application of the AI-color rule (ADR-0007) anywhere in the product.** If a human agent's reply is painted in the AI color, the screen is lying about who is talking — on the one screen whose entire purpose is to make that distinction visible.

---

## 4. Workflow

```
Agent opens /admin/chat
   │
   ▼
GET /admin/chat/queue    → escalated: unclaimed + mine, by wait time desc
   │   Poll every ~10s (the queue is a pull signal; nothing pushes)
   │
   ├─→ Clicks [ Take ] on a waiting conversation
   │        │
   │        ▼
   │   POST /admin/chat/{id}/claim        ← ATOMIC
   │        │
   │        ├─ 200  → it's yours. Composer unlocks.
   │        └─ 409  → someone else got there first.
   │                  Show it plainly ("Ravi took this one"),
   │                  refresh the queue. NOT an error toast —
   │                  it's a normal race, and it happens.
   │
   ├─→ Reads the transcript (bot turns + tool calls inline)
   │
   ├─→ Types a reply → POST /admin/chat/{id}/reply
   │        → chat_messages { sender: 'agent' }
   │        → the visitor's widget picks it up on its next poll (~4s)
   │
   └─→ [ Close conversation ] → POST /admin/chat/{id}/close
            → status = closed; the visitor is told
```

**While the conversation is escalated, the bot is silent** (`05-ai-chatbot-spec.md` §10A.1). The visitor's messages still arrive and still appear here — they are persisted without invoking Bedrock. **If you walk away, nobody is answering them.**

---

## 5. States

| State | Behavior |
|---|---|
| **Queue empty** | *"No one's waiting."* Calm, not celebratory. This is the normal state and it should feel like it. |
| Loading | Skeleton rows. The queue count in the nav renders first — it's the actionable bit. |
| **Unclaimed, waiting** | The default. Waiting time visible and **rising**. |
| **Waiting > threshold** | **Loud.** `error` treatment, red flag. Someone has been ignored. |
| **Claimed by me** | Composer enabled. Marked clearly as yours. |
| **Claimed by someone else** | Visible but **read-only** — no composer. You can see it's handled; you cannot barge in. |
| **Claim race lost (409)** | *"Ravi picked this one up."* Refresh the queue. **Not an error** — a normal race. |
| Visitor left mid-handoff | Conversation goes `abandoned` on the staleness rule. It leaves the queue. **Do not leave a ghost.** |
| **Outside business hours** | The queue may still show items, but the bot should not have promised a human at all (`05-ai-chatbot-spec.md` §10A.4). If items appear here out of hours, the escalation rules are misconfigured. |
| Send failed | Keep the typed text. **Never make an agent retype into a live conversation.** |

---

## 6. API Calls

| Trigger | Call |
|---|---|
| Mount + every ~10s | `GET /admin/chat/queue` |
| Take | `POST /admin/chat/{conversation_id}/claim` → 200 / **409** |
| Send | `POST /admin/chat/{conversation_id}/reply` |
| Close | `POST /admin/chat/{conversation_id}/close` |
| Open a conversation | `GET /admin/ai-config/chat-logs` (existing — the transcript) |

All: `Authorization: Bearer <jwt>`. All defined in `04-api-spec.md` §12A. **Nothing on this screen calls an endpoint that isn't in the spec.**

---

## 7. Data Touched

| Table | Access |
|---|---|
| `chat_conversations` | Read (queue) · Update (`assigned_agent_id`, `status`) |
| `chat_messages` | Read (transcript) · **Write (`sender = 'agent'`)** |
| `users` | Read (the agent's name, shown to the visitor) |
| `leads` | Read (the linked lead, if any) |
| `properties` | Read (the property in play) |

**No migration needed.** `chat_messages.sender` already accepts `agent` (§3.14) and `chat_conversations` already has `status`, `escalated_at` and `assigned_agent_id` (§3.13). The schema anticipated this screen; only the API was missing.

---

## 8. Permissions & Tenancy

- `agent` and `admin`. Enforced **server-side** via `require_role` — hiding the nav item is not a control.
- **`conversation_id` arrives as a UUID in the path. Verify it belongs to the caller's tenant before acting on it.** Skipping that check turns this screen into a cross-tenant read of another business's customer conversations — which is exactly threat T1 (`19-security-and-privacy.md`), on data that includes phone numbers and budgets.
- The **claim is atomic** (`04-api-spec.md` §12A.1) — same mechanism as the lead claim. Reuse it.

---

## 9. Validation & Edge Cases

- **Two agents click Take at the same instant.** Exactly one wins. The loser sees who won, not a stack trace.
- **The agent closes, then the visitor sends another message.** The conversation is `closed`; the message must not silently vanish. Either it reopens the conversation or it creates a new one — **decide this, don't let it be emergent.** *(See §11.)*
- **The visitor's transcript may contain `<script>`.** It is rendered in an agent's browser. **Escape on output** (`03-database-schema.md` §3.14 says so explicitly — stored XSS, `19-security-and-privacy.md` T5).
- **An agent goes offline mid-conversation.** Nothing releases the claim. The visitor waits forever, and the queue shows nothing wrong because the chat is "handled". *(See §11.)*
- **A long transcript** — paginate the history, don't render 400 messages.

---

## 10. Acceptance Criteria

| ID | Case |
|---|---|
| — | An escalated conversation appears in the queue **within one poll cycle** (FR1.7 acceptance: *"real time or near-real time"*) |
| — | An agent claims it, replies, and **the reply reaches the visitor's open widget** — the whole point of the screen |
| — | Two agents claiming simultaneously → **exactly one owner**; the loser gets a clear message |
| — | While escalated, a visitor message is **persisted without invoking Bedrock** (`05-ai-chatbot-spec.md` §10A.1) |
| — | An agent from Tenant A **cannot open a Tenant B conversation** by guessing its UUID |
| — | The agent's reply is **not** rendered in the AI color (ADR-0007) |

---

## 11. Open Questions

- [ ] **Claim release.** Nothing un-claims a conversation when an agent closes their laptop. The visitor waits forever and the queue looks clean. A "release" action is the cheap fix; an auto-release on inactivity needs a timer — **and there is no scheduler (`GAPS.md` G9a)**, the same gap that blocks the mandatory stale-lead alert. **One fix closes both.**
- [ ] **A message arriving on a `closed` conversation** — reopen, or start a new one? Decide it; don't let it emerge.
- [ ] **Proactive "nobody picked this up" alert** needs the same scheduler (G9a). MVP ships with the pull signal only — the queue shouts, but only at someone already looking at it. **Accepted weakness, logged.**
- [ ] Should an agent be able to **hand back to the bot** after answering a one-off question? Cheap, and it would keep the bot useful in long sessions. Not specified.
