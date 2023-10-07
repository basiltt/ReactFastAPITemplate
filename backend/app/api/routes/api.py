from fastapi import APIRouter
from starlette import status
from backend.app.api.routes.user.user_router import router as user_router
from backend.app.api.routes.books.bookes_router import router as book_router

router = APIRouter()


@router.get("/ping", status_code=status.HTTP_200_OK)
async def ping() -> dict:
    """
    route for sanity check
    @return: response as dictionary
    """
    return {"ping": "pong!"}


router.include_router(user_router)
router.include_router(book_router)
