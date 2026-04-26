import sys
import os

# Add the src directory to the python path so absolute imports work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from fastapi import FastAPI
from interfaces.api.routes import router

app = FastAPI(title="Agentic KB Auditor API", version="0.1.0")

app.include_router(router, prefix="/api/v1")

@app.get("/health")
def health_check():
    return {"status": "healthy"}
