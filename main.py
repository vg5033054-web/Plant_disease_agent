import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from backend.api.routes import router as api_router

# Load environment configuration
load_dotenv()

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("plant_disease_agent")

app = FastAPI(
    title="Plant Disease Information Agent",
    description="Intelligent agronomic assistant delivering grounded, structured plant disease diagnosis and management advice.",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Router
app.include_router(api_router)

# Mount frontend directory for static assets and single-page web app
frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")
    logger.info(f"Mounted frontend assets from {frontend_dir}")
else:
    logger.warning(f"Frontend directory not found at {frontend_dir}")

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    logger.info(f"Starting Plant Disease Information Agent on http://{host}:{port}")
    uvicorn.run("backend.main.app", host=host, port=port, reload=True)
