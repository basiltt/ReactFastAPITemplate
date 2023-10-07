from httpx import AsyncClient


async def test_ping(async_client: AsyncClient) -> None:
    response = await async_client.get("/api/ping")
    assert response.status_code == 200
    assert response.json() == {"ping": "pong!"}
