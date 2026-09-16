from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.database.base import Base
from app.database.connection import engine
from app.routes import auth, backlogs, electives, faculty, profile, recommendations

settings = get_settings()

app = FastAPI(title="MOIRA Academic Advisory API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "moira-api"}


app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(electives.router)
app.include_router(backlogs.router)
app.include_router(faculty.router)
app.include_router(recommendations.router)
