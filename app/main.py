import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

load_dotenv(override=True)

APP_NAME = "FitBuddy - AI Fitness Plan Generator"

app = FastAPI(
    title=APP_NAME,
    description="AI-powered fitness and nutrition plan generator",
    version="1.0.0"
)

templates = Jinja2Templates(directory="app/templates")

# Load application routes
from app.routes import router

app.include_router(router)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "application": APP_NAME
    }