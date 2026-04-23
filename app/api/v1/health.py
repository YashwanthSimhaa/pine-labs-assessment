from fastapi import status, APIRouter
from fastapi.responses import JSONResponse
from app.core.config import settings

router = APIRouter(prefix=settings.API_PREFIX, tags=["Health Check"])

@router.get("/health-check")
async def health_check():
    """
    API to check whether the web server is up or down.
    """
    return JSONResponse(
        content={"status": "Server is up and running"},
        status_code=status.HTTP_200_OK
    )