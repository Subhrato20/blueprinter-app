import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.routes.plan import router as plan_router
from .api.routes.ask import router as ask_router
from .api.routes.plan_patch import router as patch_router
from .api.routes.cursor_link import router as cursor_router


def get_cors_origins() -> list[str]:
    raw = os.getenv("CORS_ORIGINS", "http://localhost:5173")
    return [o.strip() for o in raw.split(",") if o.strip()]


app = FastAPI(title="Blueprinter API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.get("/api/health")
def health():
    return {"status": "ok"}


app.include_router(plan_router, prefix="/api")
app.include_router(ask_router, prefix="/api")
app.include_router(patch_router, prefix="/api")
app.include_router(cursor_router, prefix="/api")

