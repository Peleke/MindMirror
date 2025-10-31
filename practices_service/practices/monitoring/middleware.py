import time

from fastapi import Request, Response
from loguru import logger


async def log_requests_middleware(request: Request, call_next) -> Response:
    """Logs incoming HTTP requests and their responses."""
    start_time = time.perf_counter()

    # Log request details
    log_context = {
        "method": request.method,
        "url_path": request.url.path,
        "query_params": str(request.query_params),
        "client_host": request.client.host if request.client else "Unknown",
        "headers": dict(request.headers),
    }
    logger.info(f"HTTP REQ START: {log_context['method']} {log_context['url_path']}", extra=log_context)

    try:
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start_time) * 1000

        # Log response details
        response_log_context = {
            "method": request.method,
            "url_path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": round(duration_ms, 2),
        }
        logger.info(
            f"HTTP REQ END: {log_context['method']} {log_context['url_path']} - STATUS: {response.status_code}",
            extra=response_log_context,
        )
        return response
    except Exception as e:
        duration_ms = (time.perf_counter() - start_time) * 1000
        # Log exception details
        exception_log_context = {
            "method": request.method,
            "url_path": request.url.path,
            "duration_ms": round(duration_ms, 2),
            "error": str(e),
            "error_type": type(e).__name__,
        }
        logger.exception(
            f"HTTP REQ FAIL: {log_context['method']} {log_context['url_path']} - ERROR: {type(e).__name__}",
            extra=exception_log_context,
        )
        # Re-raise the exception to be handled by FastAPI's default error handling or other middlewares
        raise
