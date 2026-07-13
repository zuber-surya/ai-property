# Rule: AI Modules (Bedrock / Claude)

Applies to: `app/services/ai/`, `app/ai_clients/`, and the AI endpoints. Source: `docs/02-architecture.md` §4.3/§6, `docs/09-coding-standards.md` §2.7, `docs/10-deployment-devops.md` §5/§6.

LLM provider is **Anthropic Claude via Amazon Bedrock** (`boto3` bedrock-runtime). Embeddings: **Amazon Titan Text Embeddings V2, 1024 dims**.

## Isolation of AI concerns
- `app/ai_clients/` (Bedrock wrapper, embeddings client, prompts) is isolated from `app/services/` so prompt/model changes never touch business logic and Bedrock can be mocked/swapped in tests.
- Flow: `Router → AI Service → AI Client (Bedrock) + Repository`. Routers never call `ai_clients/` directly.

## Prompts are versioned files
- Prompts live **only** in `app/ai_clients/prompts/*.py` — never inlined in a service function.
- Version each prompt constant/function in a comment/docstring (e.g. `# v1 - initial chatbot base prompt`) so changes are traceable when eval results shift.

## Tenant scoping is mandatory in AI
- Always pass `tenant_id` into every embeddings query and Bedrock prompt context. **Never search, recommend, or chat across tenants.**

## Latency, cost & abuse control
- Chat/search/recommend are latency-sensitive → async boto3, no event-loop blocking.
- Log every Bedrock call's latency, token usage, and model ID (for cost tracking + quality debugging).
- Public `ai/*` endpoints need per-session/IP rate limiting to cap Bedrock cost exposure.
- Validate input before building prompts (basic prompt-injection hygiene — full detail in `docs/05-ai-chatbot-spec.md`).
- Provide graceful degradation (e.g. fall back to non-AI filter search) rather than hard failure when parsing fails, times out, or a soft cap is hit.

## Model selection
- Pick the Claude model per task with cost/latency in mind (a lighter model for quick search-query parsing vs. a stronger model for chatbot/recommendation reasoning). Confirm the exact model ID in the relevant AI spec doc before hardcoding it — and read `/claude-api` guidance for current model IDs.
