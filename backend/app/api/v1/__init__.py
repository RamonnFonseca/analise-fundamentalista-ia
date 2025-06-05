# backend/app/api/v1/__init__.py
from fastapi import APIRouter
from .endpoints import documents #, reports

api_router = APIRouter()
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
# api_router.include_router(reports.router, prefix="/reports", tags=["reports"]) 