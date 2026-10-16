from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from signup import app as signup_app
from login import app as login_app
from diary import app as diary_app
from dashboard import app as dashboard_app
from suggestion import app as suggestion_app

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"])

app.include_router(signup_app)
app.include_router(login_app)
app.include_router(diary_app)
app.include_router(dashboard_app)
app.include_router(suggestion_app)