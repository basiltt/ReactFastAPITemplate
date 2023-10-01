import base64

import requests
from O365 import Account
from starlette import status
from starlette.exceptions import HTTPException
from starlette.requests import Request


async def get_user_profile_picture_from_o365(
    email: str, request: Request, raise_exception_on_not_found=False
) -> any:
    account = Account(
        (
            request.app.state.settings.o365_client_id,
            request.app.state.settings.o365_client_secret,
        )
    )
    get_directory = account.directory()
    try:
        image_url_bytes = get_directory.get_user(email).get_profile_photo()
    except requests.exceptions.HTTPError:
        if raise_exception_on_not_found:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile picture not found!",
            )
        else:
            return None
    if image_url_bytes:
        return base64.b64encode(image_url_bytes).decode("utf-8")
    else:
        return {"detail": "User profile picture not found!"}
