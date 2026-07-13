# Module: AI Search (USP)

Covers PRD Module 2. Natural-language property search ("3BHK under 80 lakhs near tech park") replacing/augmenting manual filters. One of the three USP features.

**Read:** `docs/06-ai-search-spec.md`, `docs/02-architecture.md` §6.1.
**Rules:** `.claude/rules/ai.md` (primary), plus `backend`, `database`, `security`, `testing`.

## Layer & data
`Router (api/v1/ai/search.py) → search_service.py → bedrock_client + embeddings_client + embedding_repository`. Reads `property_embeddings` (pgvector), scoped to `tenant_id`.

## Flow (`docs/02` §6.1)
`POST /api/v1/ai/search {query, tenant_id, filters}` →
1. Parse the query via Bedrock into structured constraints (type, budget, bedrooms, location, amenities).
2. Generate a query embedding (Titan Text Embeddings V2, 1024 dims).
3. Query pgvector for semantic matches — **scoped to `tenant_id`**.
4. Merge structured-filter results + semantic results and rank by combined relevance.
Return ranked property list.

## Key requirements
- FR2.1 single free-text bar; FR2.2 structured + semantic parse; FR2.3 combined-relevance ranking; FR2.4 auto-suggestions while typing; FR2.5 voice input (speech-to-text into the same pipeline); FR2.6 tenant-scoped — only that tenant's listings; **FR2.7 fallback to standard filter-based search if AI parsing fails or times out** (graceful degradation).
- AI search must be combinable with manual filters in one query without conflict.

## Testing
- Representative NL query set judged relevant by a human reviewer (target in `docs/06`) — separate eval suite, not fast CI.
- Latency budget from `docs/06` must hold even with the AI parse step.
- No cross-tenant results.
