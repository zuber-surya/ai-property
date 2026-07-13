# Module: AI Chatbot (USP)

Covers PRD Module 1. Conversational assistant on every public page that answers questions, qualifies visitors, and captures leads. One of the three USP features — highest product risk.

**Read:** `docs/05-ai-chatbot-spec.md`, `docs/02-architecture.md` §6.2.
**Rules:** `.claude/rules/ai.md` (primary), plus `backend`, `security`, `testing`.

## Layer & tables
`Router (api/v1/ai/chat.py) → chat_service.py → bedrock_client + repositories`. Tables: `chat_conversations`, `chat_messages`.

## Flow (`docs/02` §6.2)
`POST /api/v1/ai/chat {message, session_id, tenant_id}` →
1. Load conversation history (session- or user-scoped).
2. Build prompt: system prompt + tenant config (Module 13) + history + message. **Prompt lives in `app/ai_clients/prompts/chat_prompts.py`, versioned.**
3. Call Bedrock (Claude) with **tool calling** for live property lookups (Module 9) and lead creation (Module 10) — never hallucinate property data.
4. Persist assistant response + any lead/appointment created.
Return bot response + any UI actions (e.g. "show property card").

## Key requirements
- FR1.1 widget on every public page, persists across navigation within a session.
- FR1.2 answers FAQs from tenant-configured content; FR1.3 live property data via tool calls (not hallucinated); FR1.4 capture contact info → create lead (`source = "chatbot"`); FR1.5 schedule visit/callback into CRM; FR1.6 history within session (and across sessions for logged-in users); FR1.7 human-agent escalation (on failure or explicit request), visible in CRM near-real-time; FR1.8 all conversations logged for admin review (Module 13).

## Testing
- Mock Bedrock: assert the service calls `create_lead` / schedule tools when the model requests them.
- Golden conversation set from `docs/05` runs as a separate eval suite, not fast CI.
- Tenant scoping: chatbot must never surface another tenant's properties.
