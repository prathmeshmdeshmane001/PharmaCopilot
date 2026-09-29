from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers.chat import router as chat_router
from app.routers.documents import router as documents_router

app_title = "PharmaCopilot API"
if settings.app_name and settings.app_name.strip():
    app_title = settings.app_name.strip()

app = FastAPI(
    title=app_title,
    version=settings.app_version or "0.1.0",
    description="Backend API for PharmaCopilot — AI-powered customer complaint management prototype.",
)

# CORS Middleware - allows Vercel deployments, custom domains, and local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(chat_router)
app.include_router(documents_router)

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
        "environment": settings.app_env,
        "llm_provider": settings.llm_provider,
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
