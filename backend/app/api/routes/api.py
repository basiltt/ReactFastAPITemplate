from fastapi import APIRouter
from starlette import status

router = APIRouter()


@router.get("/ping", status_code=status.HTTP_200_OK)
async def ping() -> dict:
    """
    route for sanity check
    @return: response as dictionary
    """
    return {"ping": "pong!"}
