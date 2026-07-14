# PropVista — one-command local dev.
#
# Sprint 0's Definition of Done (15-development-plan.md §4) is literally:
#   "a developer can clone the repo, run all three apps locally, and hit a real
#    (empty) staging deployment."
#
# That must be a command, not a wiki page.

.PHONY: help setup dev backend admin site test check tokens verify clean

help:
	@echo ""
	@echo "  make setup    install everything (backend venv + both frontends)"
	@echo "  make dev      run all three apps"
	@echo "  make test     backend pytest + frontend vitest"
	@echo "  make check    drift gate + lint + types  (run before every commit)"
	@echo "  make tokens   regenerate design tokens FROM docs/DESIGN.md"
	@echo "  make verify   drive the app in a real browser (see .claude/skills/verify)"
	@echo ""

# --- setup ----------------------------------------------------------------
setup:
	@echo ">> backend (Python 3.12 — pinned; 3.14 has no wheels for asyncpg/pydantic-core)"
	cd backend && uv venv --python 3.12 .venv && uv pip install -r requirements-dev.txt
	@echo ">> design tokens (generated FROM docs/DESIGN.md — never hand-edited)"
	python scripts/gen_tokens.py
	@echo ">> frontends"
	cd admin-portal && npm install --no-fund --no-audit
	cd public-site && npm install --no-fund --no-audit
	@echo ">> git hooks (the drift gate)"
	git config core.hooksPath .githooks
	@echo ""
	@echo "Done. 'make dev' to run."

# --- run ------------------------------------------------------------------
backend:
	cd backend && ./.venv/Scripts/python.exe -m uvicorn app.main:app --reload --port 8000

admin:
	cd admin-portal && npm run dev

site:
	cd public-site && npm run dev

dev:
	@echo "Run these in three terminals:"
	@echo "  make backend    → http://localhost:8000/health"
	@echo "  make admin      → the admin portal"
	@echo "  make site       → the public site"

# --- quality --------------------------------------------------------------
tokens:
	python scripts/gen_tokens.py

test:
	cd backend && ./.venv/Scripts/python.exe -m pytest -q
	cd admin-portal && npm run test
	cd public-site && npm run test

check:
	@echo ">> drift gate"
	python scripts/check_drift.py
	@echo ">> tokens current with DESIGN.md?"
	python scripts/gen_tokens.py --check
	@echo ">> backend lint + format"
	cd backend && ./.venv/Scripts/python.exe -m ruff check . && ./.venv/Scripts/python.exe -m black --check .
	@echo ">> frontend types"
	cd admin-portal && npx tsc --noEmit
	cd public-site && npx tsc --noEmit

verify:
	@echo "Load the verify skill: /verify"
	@echo "A passing unit test is NOT verification — jsdom is not a browser."
	@echo "Launch the app, drive the flow, screenshot, and LOOK at it."

clean:
	rm -rf backend/.venv admin-portal/node_modules public-site/node_modules
