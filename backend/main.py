from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
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


@app.get("/")
async def root():
    return {"message": "Resolve Facility Management API", "docs": "/docs"}
