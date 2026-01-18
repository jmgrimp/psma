from __future__ import annotations

from contextlib import asynccontextmanager
import logging
import time
import uuid

from fastapi import FastAPI
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import Response

from psma_api.deps import build_http_client
from psma_api.logging_config import setup_logging
from psma_api.logging_context import request_id_var
from psma_api.settings import settings
from psma_api.routes.providers_tmdb import router as providers_tmdb_router
from psma_api.routes.providers_tvmaze import router as providers_tvmaze_router
from psma_api.routes.availability_engine_v1 import router as availability_engine_v1_router
from psma_api.routes.availability_v1 import router as availability_v1_router
from psma_api.routes.planning_v1 import router as planning_v1_router


setup_logging(level=settings.log_level, fmt=settings.log_format)
logger = logging.getLogger("psma_api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    client = build_http_client()
    app.state.http_client = client
    try:
        yield
    finally:
        await client.aclose()


app = FastAPI(
    title="PSMA API",
    version="0.0.0",
    description="Program Subscription Manager Application (PSMA) backend API",
    lifespan=lifespan,
)

origins = [origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(providers_tvmaze_router)
app.include_router(providers_tmdb_router)
app.include_router(availability_engine_v1_router)
app.include_router(availability_v1_router)
app.include_router(planning_v1_router)


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    token = request_id_var.set(request_id)
    start = time.perf_counter()

    try:
        response: Response = await call_next(request)
    except Exception:
        duration_ms = (time.perf_counter() - start) * 1000
        logger.exception(
            "request_failed",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "duration_ms": round(duration_ms, 2),
            },
        )
        raise
    finally:
        request_id_var.reset(token)

    duration_ms = (time.perf_counter() - start) * 1000
    extra = {
        "request_id": request_id,
        "method": request.method,
        "path": request.url.path,
        "status_code": response.status_code,
        "duration_ms": round(duration_ms, 2),
    }
    if response.status_code >= 500:
        logger.error("request_completed", extra=extra)
    elif response.status_code >= 400:
        logger.warning("request_completed", extra=extra)
    else:
        logger.info("request_completed", extra=extra)

    response.headers["X-Request-ID"] = request_id
    return response


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/version")
def version() -> dict:
    return {"version": app.version}
