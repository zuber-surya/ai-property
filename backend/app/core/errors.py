"""Domain exceptions and the single place they become HTTP responses.

The error envelope is owned by `docs/04-api-spec.md` §1:

    { "error": { "code": "PROPERTY_NOT_FOUND", "message": "Property not found." } }

⚠️ A raw DB or Bedrock exception must NEVER reach a client. It leaks schema,
credentials and stack frames, and it tells an attacker what to try next. Every
unhandled exception funnels through `unhandled_handler` below and becomes a
generic 500 — the detail goes to the logs, not the response body.
"""

from __future__ import annotations

import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)

# Framework errors that never reach a service — a 404 from an unmatched route,
# a 405 from a wrong verb. FastAPI answers these with its own {"detail": ...}
# shape, which is NOT the envelope in 04-api-spec.md §1.
#
# This was found by actually driving the server, not by a unit test: the tests
# were green while every 404 in the product returned the wrong shape.
_HTTP_CODES: dict[int, str] = {
    400: "BAD_REQUEST",
    401: "UNAUTHENTICATED",
    403: "PERMISSION_DENIED",
    404: "NOT_FOUND",
    405: "METHOD_NOT_ALLOWED",
    409: "CONFLICT",
    429: "RATE_LIMITED",
}


class DomainError(Exception):
    """Base for every error the SERVICE layer raises.

    Services raise these; routers never catch them. The handlers below map them
    to the envelope, so the mapping lives in exactly one place.
    """

    code: str = "INTERNAL_ERROR"
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class NotFoundError(DomainError):
    status_code = status.HTTP_404_NOT_FOUND
    code = "NOT_FOUND"


class ValidationError(DomainError):
    status_code = status.HTTP_400_BAD_REQUEST
    code = "VALIDATION_ERROR"


class PermissionDeniedError(DomainError):
    """A restricted role called an out-of-scope endpoint.

    Enforced server-side. Hiding a nav item is a courtesy, not a control.
    """

    status_code = status.HTTP_403_FORBIDDEN
    code = "PERMISSION_DENIED"


class ConflictError(DomainError):
    """Lost a race — e.g. two agents claiming one lead or one chat.

    This is a NORMAL outcome, not a failure. The loser gets a clear message,
    not a stack trace.
    """

    status_code = status.HTTP_409_CONFLICT
    code = "CONFLICT"


def _envelope(code: str, message: str, status_code: int) -> JSONResponse:
    return JSONResponse(
        status_code=status_code, content={"error": {"code": code, "message": message}}
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Wire the handlers. Called once, from main.py."""

    @app.exception_handler(DomainError)
    async def domain_handler(_: Request, exc: DomainError) -> JSONResponse:
        return _envelope(exc.code, exc.message, exc.status_code)

    @app.exception_handler(RequestValidationError)
    async def validation_handler(
        _: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return _envelope(
            "VALIDATION_ERROR",
            "The request could not be validated.",
            status.HTTP_400_BAD_REQUEST,
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_handler(_: Request, exc: StarletteHTTPException) -> JSONResponse:
        """Routing-level errors (404, 405) must use the envelope too.

        Without this, every unmatched route in the product returns FastAPI's
        {"detail": "Not Found"} — a second, undocumented error shape that no
        frontend error-mapper knows about.
        """
        code = _HTTP_CODES.get(exc.status_code, "ERROR")
        return _envelope(code, str(exc.detail), exc.status_code)

    @app.exception_handler(Exception)
    async def unhandled_handler(request: Request, exc: Exception) -> JSONResponse:
        # The detail goes to the log. The client gets nothing that would help
        # an attacker — no driver name, no SQL, no stack frame.
        logger.exception(
            "unhandled_exception", extra={"path": request.url.path, "error": str(exc)}
        )
        return _envelope(
            "INTERNAL_ERROR",
            "Something went wrong. Please try again.",
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
