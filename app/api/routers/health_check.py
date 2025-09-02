from fastapi import APIRouter, status
router = APIRouter()

@router.get("/health")
async def get_health():
    return {"status":"OK", "status_code": status.HTTP_200_OK}