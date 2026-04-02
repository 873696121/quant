import time
import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logging import get_logger

logger = get_logger(__name__)


class TracingMiddleware(BaseHTTPMiddleware):
    """请求追踪中间件 - 为每个请求添加唯一追踪ID"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        trace_id = request.headers.get("X-Trace-ID", str(uuid.uuid4()))
        request.state.trace_id = trace_id

        start_time = time.time()

        logger.info(
            f"Request started",
            extra={
                "trace_id": trace_id,
                "method": request.method,
                "path": request.url.path,
                "client_ip": request.client.host if request.client else None,
            }
        )

        try:
            response = await call_next(request)
            duration = time.time() - start_time

            logger.info(
                f"Request completed",
                extra={
                    "trace_id": trace_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "duration_ms": round(duration * 1000, 2),
                }
            )

            response.headers["X-Trace-ID"] = trace_id
            return response

        except Exception as e:
            duration = time.time() - start_time
            logger.exception(
                f"Request failed",
                extra={
                    "trace_id": trace_id,
                    "method": request.method,
                    "path": request.url.path,
                    "duration_ms": round(duration * 1000, 2),
                    "error": str(e),
                }
            )
            raise
