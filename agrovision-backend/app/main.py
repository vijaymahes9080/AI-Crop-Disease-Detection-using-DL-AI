# app/main.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "agrovision-ml")))

from fastapi import FastAPI, Request, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api.v1.api import router as v1_router

app = FastAPI(
    title="AgroVision AI API",
    description="Backend services for crop disease detection scans",
    version="1.0.0"
)

# CORS Boundaries configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom Error Handling Middleware
@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"status": "error", "error_code": exc.status_code, "message": exc.detail},
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"status": "error", "error_code": 500, "message": "An unexpected error occurred on the server"},
    )

app.include_router(v1_router, prefix="/api/v1")

# Mount local uploads directory
from fastapi.staticfiles import StaticFiles
import os
os.makedirs("static_uploads", exist_ok=True)
app.mount("/static", StaticFiles(directory="static_uploads"), name="static")

