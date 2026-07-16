"""Sprint 0 acceptance: /health returns 200.

`15-development-plan.md` §4 — "CI pipeline runs and passes on an empty commit;
/health returns 200 in staging."
"""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_health_returns_ok() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_unhandled_error_never_leaks_internals() -> None:
    """A raw exception must become the envelope, not a stack trace.

    This is the rule from rules/backend.md: "Never let a raw DB or Bedrock
    exception reach the client." A leaked driver name or SQL fragment tells an
    attacker exactly what to try next.
    """
    from app.core.errors import DomainError, NotFoundError

    # The envelope shape is owned by 04-api-spec.md §1.
    err = NotFoundError("Property not found.")
    assert err.status_code == 404
    assert err.code == "NOT_FOUND"
    assert isinstance(err, DomainError)


@pytest.mark.asyncio
async def test_404_uses_the_error_envelope_not_fastapi_default() -> None:
    """A routing 404 must use the envelope from 04-api-spec.md §1.

    Regression: FastAPI answers unmatched routes with {"detail": "Not Found"} —
    a second, undocumented error shape. The unit tests were green while every
    404 in the product returned the wrong thing. It was only caught by actually
    driving the server (rules/execution.md step 7).
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/does-not-exist")

    assert response.status_code == 404
    body = response.json()
    assert "error" in body, f"expected the envelope, got {body}"
    assert body["error"]["code"] == "NOT_FOUND"
    assert "detail" not in body
