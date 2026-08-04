import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.error import JobHoundError, ProfileAlreadyExistsError, ProfileNotFoundError
from src.infra.routers import matches, pipeline, profile, stats

_STATUS_BY_ERROR = {
    ProfileAlreadyExistsError: 409,
    ProfileNotFoundError: 404,
}

_DEFAULT_CORS_ORIGINS = "http://localhost:3000,http://localhost:5173"


def create_app() -> FastAPI:
    app = FastAPI(title="jobhound API", version="0.1.0")
    origins = os.getenv("CORS_ORIGINS", _DEFAULT_CORS_ORIGINS)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[o.strip() for o in origins.split(",") if o.strip()],
        allow_methods=["GET", "POST", "PUT"],
        allow_headers=["*"],
    )
    app.include_router(matches.router)
    app.include_router(pipeline.router)
    app.include_router(profile.router)
    app.include_router(stats.router)

    @app.exception_handler(JobHoundError)
    def job_hound_error_handler(request: Request, exc: JobHoundError) -> JSONResponse:
        status_code = _STATUS_BY_ERROR.get(type(exc), 400)
        return JSONResponse(status_code=status_code, content={"detail": str(exc)})

    @app.get("/health", tags=["health"])
    async def health() -> dict:
        return {"status": "ok"}

    return app


app = create_app()
