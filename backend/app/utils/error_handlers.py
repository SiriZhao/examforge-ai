from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(HTTPException)
    async def http_exception_handler(
        _: Request, exc: HTTPException
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": True,
                "message": normalize_detail(exc.detail),
                "detail": exc.detail,
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        _: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={
                "error": True,
                "message": "请求参数校验失败。",
                "detail": exc.errors(),
            },
        )

    @app.exception_handler(Exception)
    async def unexpected_exception_handler(
        _: Request, exc: Exception
    ) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content={
                "error": True,
                "message": "服务器内部错误。",
                "detail": exc.__class__.__name__,
            },
        )


def normalize_detail(detail: object) -> str:
    if isinstance(detail, str):
        return detail
    return "请求失败。"
