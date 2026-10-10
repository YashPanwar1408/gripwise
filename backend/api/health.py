"""GripWise Backend — Health check router."""
from fastapi import APIRouter
from backend.schemas import ApiResponse

router = APIRouter()


@router.get("/health", tags=["health"])
async def health():
    return ApiResponse.ok({"status": "ok", "service": "gripwise-api", "version": "0.1.0"})
