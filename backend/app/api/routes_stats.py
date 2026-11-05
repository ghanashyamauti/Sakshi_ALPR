"""
Dashboard Analytics & Stats API Routes
"""
from fastapi import APIRouter
from backend.app.database.repository import PlateRepository

router = APIRouter(prefix="/api/v1/stats", tags=["Statistics"])

@router.get("")
async def get_dashboard_stats():
    """Retrieve top-level KPI metrics for the dashboard."""
    stats = PlateRepository.get_stats()
    return {
        "success": True,
        "stats": stats
    }

