"""
Database Records & Logs API Routes
"""
from typing import Optional
from fastapi import APIRouter, Query, Response
from backend.app.database.repository import PlateRepository

router = APIRouter(prefix="/api/v1/records", tags=["Records"])

@router.get("")
async def list_records(
    search: Optional[str] = Query(None, description="Search by plate number, RTO, or text"),
    state: Optional[str] = Query(None, description="Filter by state code e.g. MH, DL"),
    mode: Optional[str] = Query(None, description="Filter by detection mode"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    """Fetch logged license plate records from PostgreSQL database."""
    records = PlateRepository.get_records(
        search=search,
        state=state,
        mode=mode,
        limit=limit,
        offset=offset
    )
    return {
        "success": True,
        "count": len(records),
        "records": records
    }

@router.get("/export/csv")
async def export_csv():
    """Export all recognized license plates to CSV format."""
    csv_content = PlateRepository.export_csv()
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=sakshi_alpr_records.csv"}
    )

@router.delete("")
async def clear_records():
    """Clear all records from database (Testing utility)."""
    PlateRepository.delete_all()
    return {"success": True, "message": "All records cleared from database."}

