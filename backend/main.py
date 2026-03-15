import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
from app.database import connect_db, close_db
from app.routers import auth, buildings, users, vendors, cleaning, maintenance, cases, costs, roster, attendance, analytics


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    yield
    await close_db()


app = FastAPI(
    title="Resolve - Facility Management System",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS – allow localhost in dev and the Heroku frontend URL in prod
allowed_origins = [
    "http://localhost:3000",
    "http://localhost:5173",
]
frontend_url = os.getenv("FRONTEND_URL")
if frontend_url:
    allowed_origins.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(buildings.router)
app.include_router(users.router)
app.include_router(vendors.router)
app.include_router(cleaning.router)
app.include_router(maintenance.router)
app.include_router(cases.router)
app.include_router(costs.router)
app.include_router(roster.router)
app.include_router(attendance.router)
app.include_router(analytics.router)

# Serve built React frontend (populated by heroku-postbuild)
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.isdir(static_dir):
    app.mount("/assets", StaticFiles(directory=os.path.join(static_dir, "assets")), name="assets")

    @app.get("/", include_in_schema=False)
    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str = ""):
        # API routes are handled above; everything else serves the SPA
        index = os.path.join(static_dir, "index.html")
        return FileResponse(index)
else:
    @app.get("/")
    async def root():
        return {"message": "Resolve Facility Management API", "docs": "/docs"}
