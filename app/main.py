from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.routers.organizations import router as org_router
from app.api.routers.buildings import router as bld_router
from app.api.routers.activities import router as act_router


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, version="1.0.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(bld_router, prefix=settings.api_v1_prefix)
    app.include_router(act_router, prefix=settings.api_v1_prefix)
    app.include_router(org_router, prefix=settings.api_v1_prefix)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app


app = create_app()


