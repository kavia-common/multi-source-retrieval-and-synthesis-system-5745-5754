from fastapi import APIRouter

router = APIRouter()

# PUBLIC_INTERFACE
@router.get("/", summary="Health Check", description="Simple health check endpoint.", tags=["health"])
def health_check():
    """Return health status for liveness probe."""
    return {"message": "Healthy"}
