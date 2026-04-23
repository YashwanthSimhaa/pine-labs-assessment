import pytest

@pytest.mark.asyncio
async def test_list_transactions_filtering(client):
    response = await client.get("/api/v1/transactions?merchant_id=m_1")

    assert response.status_code == 200
    assert "data" in response.json()


@pytest.mark.asyncio
async def test_pagination(client):
    response = await client.get("/api/v1/transactions?limit=2&offset=0")

    assert response.status_code == 200
    assert len(response.json()["data"]) <= 2


@pytest.mark.asyncio
async def test_transaction_details_contains_events(client):
    response = await client.get("/api/v1/transactions/tx_flow")

    assert response.status_code == 200
    data = response.json()

    assert "transaction" in data
    assert "events" in data
    assert "merchant" in data