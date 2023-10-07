import pytest
from httpx import AsyncClient


# @pytest.mark.run()
# #  Test for get application users
# async def test_get_application_user(async_client: AsyncClient) -> None:
#     email = "tt.basil@gmail.com"
#     response = await async_client.get(
#         "/api/access/users/get-application-users", follow_redirects=True
#     )
#     assert response.status_code == 200
#     assert response.json().get("email") == email


@pytest.mark.run(order=1)
#  Test for create users
async def test_create_user(async_client: AsyncClient) -> None:
    data = {
        "email": "basil.tt@hpe.com",
        "first_name": "Basil",
        "last_name": "T T",
        "password": "My!Password777",
        "repeat_password": "My!Password777",
        "phone": "8547948528",
    }
    response = await async_client.post(
        "/api/users/create-users", follow_redirects=True, json=data
    )
    assert response.status_code == 201
    assert response.json().get("users").get("email") == data.get("email")
    assert response.json().get("users").get("first_name") == data.get("first_name")
    assert response.json().get("users").get("last_name") == data.get("last_name")
    assert response.json().get("users").get("phone") == data.get("phone")
