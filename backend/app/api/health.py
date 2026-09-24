"""Health check endpoint."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    """Return a simple status, to confirm the server is running."""
    return {"status": "ok"}
