import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.logging_setup import setup_logging

setup_logging()
logger = logging.getLogger("api")

app = FastAPI(
    title="NMK Chatbot API",
    description="API for NMK Architecture Chatbot",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from api.routes import chat_router, health_router

app.include_router(health_router, tags=["health"])
app.include_router(chat_router, prefix="/api", tags=["chat"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "NMK Chatbot API",
        "version": "1.0.0",
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.app:app", host="0.0.0.0", port=8000, reload=True)
