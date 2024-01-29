""" Exception handlers for FastAPI module. """
# pylint: disable=unused-argument
from fastapi import Request, Response
from pydantic_core import ValidationError
from starlette.responses import JSONResponse
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY


async def pydantic_validation_error_exception_handler(request: Request, exc: ValidationError) -> Response:  # noqa
    return JSONResponse(
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "message": "Validation error",
            "error": str(exc),
        },
    )
