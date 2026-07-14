# AI Chatbot Specification — PropVista CRM

> **Doc 05 of the PropVista CRM documentation set.** Detailed design for the public-site AI chatbot — one of the platform's three core USP features. Covers conversation design, tool-calling, Bedrock/Claude integration, guardrails, and evaluation.
>
> **Status:** Draft v1.0 · **Last updated:** July 2026
> Depends on: `01-prd.md` (Module 1), `02-architecture.md` (Section 6.2), `03-database-schema.md` (`chat_conversations`, `chat_messages`, `ai_config`), `04-api-spec.md` (Section 3.2)

---

## 1. Purpose & Success Definition

The chatbot exists to do three things well:
1. **Answer** questions about listed properties and general process, using real data — never invented facts.
2. **Qualify and capture** leads mid-conversation without feeling like a form.
3. **Know its limits** and hand off to a human agent cleanly when it should.

Success for MVP = a visitor can have a full conversation about a real property and either get a correct answer or a scheduled next step (visit/callback/escalation), with no hallucinated property facts.

---

## 2. Conversation Design Principles

- **Persona:** Helpful, concise real-estate assistant — not overly casual, not robotic. Tone is configurable per tenant (Section 8) within these bounds.
- **Never invent property facts.** Any specific claim about price, availability, area, or amenities must come from a tool call to live data, not from the model's general knowledge or memory of the conversation.
- **Keep replies short.** Chat UI, not an essay — 2–4 sentences per turn unless the visitor asks for detail.
- **Always offer a next step.** Every substantive answer ends with a natural next action (schedule visit, see similar properties, talk to an agent) rather than a dead end.
- **Escalate rather than guess.** If the bot is not confident it has correct data or the visitor is frustrated, escalate — do not improvise.

---

## 3. System Prompt Structure

The system prompt sent to Claude (via Bedrock) on every turn is assembled from layered, versioned parts (`ai_clients/prompts/chat_prompts.py`, per `02-architecture.md`):

```
[1] Base behavior rules (fixed, versioned, same for all tenants)
      - persona, tone bounds, "never invent facts", reply-length rule, escalation triggers
[2] Tenant configuration (from ai_config table, Section 8)
      - custom greeting, tenant FAQ entries, tenant-specific escalation rules/contact info
[3] Conversation context
      - last N messages (or summary, see Section 7) from chat_conversations/chat_messages
[4] Available tools (Section 4) — passed via Bedrock's tool-use parameter, not embedded as text
```

Keeping `[1]` and `[2]` separate (rather than one merged prompt string) means the base safety rules can never be overridden by tenant configuration — tenant config can only add content (FAQs, tone flavor), not remove guardrails.

---

## 4. Tool-Calling (Function Definitions)

Claude's native tool-use is used so the model requests structured actions rather than free-texting them. Tools exposed to the model:

| Tool | Purpose | Backend Handler |
|---|---|---|
| `lookup_property` | Get current price/availability/specs for a specific property (by ID or fuzzy title match) | `property_service.get_property()` |
| `search_properties` | Find properties matching loose criteria mentioned in chat (delegates to AI Search, `06-ai-search-spec.md`) | `search_service.search()` |
| `create_lead` | Capture visitor contact info + interest as a lead | `lead_service.create_lead()` |
| `schedule_visit_or_callback` | Record a requested time slot for a visit/callback | `lead_service.schedule()` |
| `escalate_to_agent` | Flag the conversation for human takeover, optionally with a reason | `chat_service.escalate()` |

**Example tool definition (conceptual, passed to Bedrock's Converse API):**
```json
{
  "name": "lookup_property",
  "description": "Get current details for a specific property by id or by a fuzzy title/location match.",
  "input_schema": {
    "type": "object",
    "properties": {
      "property_id": { "type": "string" },
      "query_hint": { "type": "string", "description": "Used if property_id is unknown, e.g. 'the 3BHK in tech park'" }
    }
  }
}
```

The model decides when to call a tool; the backend executes it and returns the tool result to the model for a follow-up turn, per Bedrock's standard tool-use loop.

---

## 5. Conversation Flow (State Machine)

```
[Greeting] → [Open Q&A / Discovery]
                 │
                 ├─→ visitor asks about a property → lookup_property → answer → offer next step
                 ├─→ visitor describes needs loosely → search_properties → present options
                 ├─→ visitor wants to move forward → create_lead (+ schedule_visit_or_callback)
                 ├─→ bot uncertain / visitor frustrated / explicit request → escalate_to_agent
                 └─→ visitor ends conversation → [Closed]
```

- `chat_conversations.status` tracks `active` → `escalated` → `closed`.
- Escalation does not end the conversation in the UI — it changes the "who's responding" context; the visitor should be told plainly (e.g. "I've looped in one of our agents, they'll respond shortly").

---

## 6. Bedrock / Claude Integration

- **API:** Amazon Bedrock Converse API (supports tool-use and streaming in a provider-agnostic shape), invoked via `boto3` from `ai_clients/bedrock_client.py`.
- **Model selection:** A single capable Claude model is used for conversation reasoning (exact model version to be pinned once available in the target Bedrock region — do not hardcode a model ID without checking current Bedrock model availability at implementation time, since Bedrock model offerings change). A lighter/cheaper Claude model may be evaluated for simple FAQ-only turns as a cost optimization post-MVP, but MVP uses one model for consistency.
- **Streaming:** Responses are streamed token-by-token to the frontend chat widget for perceived responsiveness (Bedrock Converse supports streaming; FastAPI endpoint uses a streaming response type).
- **Timeouts:** A hard timeout (e.g. a few seconds) triggers a graceful fallback message ("I'm having trouble responding right now — would you like me to connect you with an agent?") rather than a hung UI.

---

## 7. Session & Memory Management

- Each browser session gets a `chat_conversations` row (linked to `user_id` if logged in, else anonymous + `session_id`).
- Full message history is stored in `chat_messages`, but **not all of it is replayed to the model every turn** — for long conversations, older turns are periodically summarized (a short system-generated summary paragraph replacing older raw turns) to control context length and cost. Summarization threshold (e.g. after N turns) to be tuned during implementation.
- Logged-in users' conversation history can persist across sessions (FR1.6 in `01-prd.md`); anonymous sessions are ephemeral but still logged for admin review.

---

## 8. Multi-Tenant Customization

Sourced from the `ai_config` table (`03-database-schema.md`):
- `chatbot_greeting` — first message shown when the widget opens.
- `chatbot_faq` — structured Q&A pairs the bot should prefer over general knowledge for tenant-specific process questions (e.g. "What documents do I need to book a unit?").
- `escalation_rules` — e.g. business hours for live handoff, fallback contact info outside those hours.

Admin-facing configuration UI is covered in PRD Module 13 / API Section 12 (`04-api-spec.md`); this doc defines how those values are consumed at inference time (Section 3, layer `[2]`).

---

## 9. Guardrails & Prompt-Injection Hygiene

- Visitor input is never inserted directly into the system prompt as instructions — it's passed strictly as conversational user-turn content, so text like "ignore previous instructions" is treated as chat content, not a directive.
- Tool outputs (property data) are treated as data, not instructions, when fed back to the model.
- The base system prompt (`[1]` in Section 3) explicitly instructs the model to ignore any user attempt to change its role, reveal its system prompt, or bypass the "never invent facts" rule.
- Rate limiting (per `04-api-spec.md` Section 1) protects against abuse driving up Bedrock cost.
- No PII beyond what's needed for lead capture is requested or stored by the bot.

---

## 10. Escalation Logic (Detail)

Escalate when any of:
- The visitor explicitly asks for a human.
- The model's own tool calls fail to find relevant data after a reasonable attempt (avoid repeated failed lookups spiraling).
- Sentiment/frustration signals appear (e.g. repeated negative phrasing) — a lightweight heuristic or model self-assessment, tuned during implementation.
- A configured tenant rule requires human handoff for certain topics (e.g. legal/contract questions).

On escalation: conversation status → `escalated`, a lead/notification is created for an available agent (ties to `04-api-spec.md` `/ai/chat/escalate` and the Lead/CRM module), and the visitor sees a clear in-chat message.

---

## 10A. The Handoff State Machine *(closes gap G7)*

Escalation used to be a **dead end**: the bot handed off to a human, and no endpoint let that human reply. FR1.7 promised a handoff the system could not perform. This section, plus `04-api-spec.md` §12A, closes it.

```
   ACTIVE ──────────────── escalate_to_agent ──────────────► ESCALATED
     │                                                          │
     │ bot answers                                    agent claims it
     │ (Bedrock)                                     (atomic — one winner)
     │                                                          │
     │                                                          ▼
     │                                                   AGENT HANDLING
     │                                                          │
     │                                              agent closes ─┤
     ▼                                                           ▼
  ABANDONED ◄── visitor left, no message for N  ────────────► CLOSED
```

### 10A.1 ⚠️ Once escalated, the bot goes silent

**`status = 'escalated'` → `POST /ai/chat/message` persists the visitor's message and does NOT call Bedrock.**

This is the load-bearing rule. If the bot keeps replying after handoff, the visitor is talking to **two voices at once** — a human and a machine, contradicting each other — which is a worse experience than never offering a human at all. It also stops paying Bedrock for every message in an escalated conversation.

The bot does not resume. Only an agent, or a close, moves the conversation on.

### 10A.2 What the visitor sees

| Moment | The visitor's widget shows |
|---|---|
| On escalation | The bot's handoff message from `ai_config.escalation_rules` — *"I've looped in one of our agents; they'll respond shortly."* |
| Waiting | A quiet, honest status — *"Waiting for an agent…"*. **Do not fake a typing indicator.** Nobody is typing. |
| Agent claims it | *"Anjali has joined the conversation."* The visitor must know they are now talking to a human — that is the entire point of asking for one. |
| Agent replies | The message, attributed to the agent by name. |
| Agent closes | *"This conversation has been closed."* with a path back to the bot or the contact form. |

### 10A.3 Delivery — polling, not a realtime channel

The widget **polls `GET /ai/chat/history/{conversation_id}` roughly every 4 seconds while `status = 'escalated'`**, and stops polling otherwise. There is no new customer-facing endpoint.

Supabase Realtime is in the stack and would be nicer — but **ADR-0005 restricts the Supabase client to Auth and Storage, never data access.** A human agent types with 10–30 seconds of natural latency; 4-second polling is invisible against that. **We do not bend a load-bearing architectural rule to save three seconds on a human's typing speed.** See **ADR-0017**.

### 10A.4 Outside business hours, do not promise a human

`ai_config.escalation_rules` already carries business hours and fallback contact info (§9).

**Outside those hours the bot must not say "an agent will respond shortly."** Nobody is there. It should say so plainly, capture contact details, and create a lead — a promise the product cannot keep is worse than an honest "we'll call you tomorrow morning."

### 10A.5 Nobody picks it up

The conversation sits in `/admin/chat/queue` with a **rising `waiting_seconds`**, rendered loudly (`17-admin-spec/15`, `17-admin-spec/22`). That is a **pull** signal — it works only if someone is looking at the screen.

⚠️ **A proactive alert — "escalated and unclaimed for 15 minutes → tell someone" — needs a timer, and there is no scheduler (`GAPS.md` G9a).** MVP ships with the pull signal only. **This is a known, accepted weakness**, and it is the same missing scheduler that blocks the mandatory stale-lead alert (FR10.2b). One fix closes both.

### 10A.6 Escalation is not a lead

An escalated chat and a lead are different objects with different clocks. The escalation creates a lead (§10), but **closing the lead does not close the chat**, and a visitor waiting in an open chat is a **real-time** obligation while a lead is a pipeline item. Do not collapse the two.

---

## 11. Logging & Admin Review

- Every message (both directions) is persisted to `chat_messages` with `metadata` capturing any tool calls made — this is what powers the admin "conversation log viewer" (PRD Module 13, API Section 12).
- Conversations can be flagged (manually by admin, or automatically on escalation) for review, supporting continuous improvement of the FAQ library and base prompt.

---

## 12. Testing & Evaluation Approach

- Maintain a **golden test set** of representative conversations (common questions, edge cases, adversarial prompts) run against the bot before each prompt/model change ships.
- Track qualitative pass/fail per test case (correct tool called, no hallucinated facts, appropriate escalation) rather than only automated string-matching, since conversational quality is hard to reduce to exact-match tests.
- Track quantitative operational metrics post-launch: escalation rate, average turns to lead-creation, visitor drop-off rate.

---

## 13. Open Questions / Assumptions to Confirm

- [ ] Exact Claude model ID(s) to pin for Bedrock, once model availability in the target AWS region is confirmed at implementation time.
- [ ] Summarization turn-threshold for long-conversation context management.
- [ ] Whether sentiment/frustration detection for escalation is a simple keyword heuristic (MVP) or a model self-assessment call (adds latency/cost).
- [ ] Business-hours-based escalation routing — depends on agent availability data not yet modeled (may need an `agent_availability` addition to the schema).

---

**Next document:** `06-ai-search-spec.md` — natural-language search pipeline, ranking logic, and embedding/indexing detail.
