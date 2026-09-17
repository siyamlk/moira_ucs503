from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect, text

from app.core.config import get_settings
from app.database.base import Base
from app.database.connection import engine
from app.routes import auth, backlogs, electives, faculty, profile, recommendations
from app.routes.admin import audit as admin_audit
from app.routes.admin import config as admin_config
from app.routes.admin import dashboard as admin_dashboard
from app.routes.admin import electives as admin_electives
from app.routes.admin import faculty as admin_faculty
from app.routes.admin import schedules as admin_schedules

settings = get_settings()

app = FastAPI(title="MOIRA Academic Advisory API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _upgrade_existing_schema() -> None:
    """One-off, idempotent upgrade for columns added after tables already
    existed in a real Postgres DB. Base.metadata.create_all is additive-only
    (it never alters existing tables), so a pre-Admin-feature DB needs this
    to pick up the new columns without losing any existing data. No-op on a
    fresh DB (create_all below creates the columns from the model directly)
    and on the SQLite test engine (tests fully recreate schema every run)."""
    if engine.dialect.name != "postgresql":
        return
    with engine.begin() as conn:
        existing_tables = inspect(conn).get_table_names()
        if "users" in existing_tables:
            conn.execute(
                text("ALTER TABLE users ADD COLUMN IF NOT EXISTS role VARCHAR(20) NOT NULL DEFAULT 'student'")
            )
        if "faculty_schedules" in existing_tables:
            conn.execute(
                text(
                    "ALTER TABLE faculty_schedules ADD COLUMN IF NOT EXISTS semester VARCHAR(40) NOT NULL DEFAULT ''"
                )
            )


@app.on_event("startup")
def on_startup() -> None:
    _upgrade_existing_schema()
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
app.include_router(admin_dashboard.router)
app.include_router(admin_electives.router)
app.include_router(admin_faculty.router)
app.include_router(admin_schedules.router)
app.include_router(admin_config.router)
app.include_router(admin_audit.router)
