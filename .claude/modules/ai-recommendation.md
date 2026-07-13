# Module: AI Recommendation / Requirement Analysis (USP)

Covers PRD Module 3. Guided questionnaire that captures buyer/renter needs and returns a ranked, matched shortlist with explainable reasons. One of the three USP features. Also reused as "Similar properties" on Property Details (Module 5).

**Read:** `docs/07-ai-recommendation-spec.md`, `docs/02-architecture.md` §6.3.
**Rules:** `.claude/rules/ai.md` (primary), plus `backend`, `database`, `security`, `testing`.

## Layer & tables
`Router (api/v1/ai/recommend.py) → recommend_service.py → embeddings_client + embedding_repository`. Tables: `requirement_profiles`, `requirement_matches`; reads `property_embeddings` (tenant-scoped).

## Flow (`docs/02` §6.3)
`POST /api/v1/ai/recommend {requirements, tenant_id}` →
1. Generate an embedding from the structured requirements.
2. Query pgvector for candidate properties (tenant-scoped).
3. Score candidates using **tenant-configured weighting** (Module 13 — e.g. budget vs. location importance).
4. Optionally call Bedrock to generate a plain-language match reason per result.
Return ranked shortlist with match reasons.

## Key requirements
- FR3.1 multi-step form: budget range, location(s), property type, purpose (self-use/investment), timeline, must-have amenities.
- FR3.2 ranked shortlist with visible match reason/score — **always return at least a ranked list or a clear "no matches, here's the closest" fallback; never an empty/broken state.**
- FR3.3 registered users save/revisit/edit their requirement profile (`requirement_profiles`).
- FR3.4 saved profiles trigger notifications on new matching properties (ties to Module 7 + `notification_rules`).
- FR3.5 matching weights configurable per tenant (Module 13).
- Match reasoning must be explainable in plain language (e.g. "Matches your budget and location; missing 1 amenity").

## Testing
- Never returns an empty/broken state — assert the sparse-result fallback path.
- Scoring/weighting logic unit-tested with Bedrock mocked; tenant scoping enforced.
