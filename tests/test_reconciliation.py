import pytest

@pytest.mark.asyncio
async def test_reconciliation_summary(client):
    response = await client.get("/api/v1/reconciliation/summary")

    assert response.status_code == 200
    assert isinstance(response.json(), list)