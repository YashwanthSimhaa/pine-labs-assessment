import pytest

@pytest.mark.asyncio
async def test_event_ingestion(client):
    response = await client.post("/api/v1/events", json={
        "event_id": "evt_1",
        "event_type": "payment_initiated",
        "transaction_id": "tx_1",
        "merchant_id": "m_1",
        "merchant_name": "Test Merchant",
        "amount": 100,
        "currency": "INR",
        "timestamp": "2026-01-01T00:00:00"
    })
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_duplicate_event(client):
    payload = {
        "event_id": "evt_dup",
        "event_type": "payment_initiated",
        "transaction_id": "tx_2",
        "merchant_id": "m_1",
        "merchant_name": "Test",
        "amount": 100,
        "currency": "INR",
        "timestamp": "2026-01-01T00:00:00"
    }

    await client.post("/api/v1/events", json=payload)
    response = await client.post("/api/v1/events", json=payload)

    assert response.status_code == 200
    assert "Duplicate" in response.json()["message"]


@pytest.mark.asyncio
async def test_payment_flow_processed_to_settled(client):
    # initiated
    await client.post("/api/v1/events", json={
        "event_id": "evt_10",
        "event_type": "payment_initiated",
        "transaction_id": "tx_flow",
        "merchant_id": "m_2",
        "merchant_name": "Flow Test",
        "amount": 200,
        "currency": "INR",
        "timestamp": "2026-01-01T00:00:00"
    })

    # processed
    await client.post("/api/v1/events", json={
        "event_id": "evt_11",
        "event_type": "payment_processed",
        "transaction_id": "tx_flow",
        "merchant_id": "m_2",
        "merchant_name": "Flow Test",
        "amount": 200,
        "currency": "INR",
        "timestamp": "2026-01-01T00:01:00"
    })

    # settled
    await client.post("/api/v1/events", json={
        "event_id": "evt_12",
        "event_type": "settled",
        "transaction_id": "tx_flow",
        "merchant_id": "m_2",
        "merchant_name": "Flow Test",
        "amount": 200,
        "currency": "INR",
        "timestamp": "2026-01-01T00:02:00"
    })

    response = await client.get("/api/v1/transactions/tx_flow")

    assert response.status_code == 200
    assert response.json()["transaction"]["status"] == "settled"