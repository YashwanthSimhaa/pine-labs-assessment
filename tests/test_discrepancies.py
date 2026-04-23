import pytest

@pytest.mark.asyncio
async def test_discrepancy_processed_not_settled(client):
    # processed but not settled
    await client.post("/api/v1/events", json={
        "event_id": "evt_d1",
        "event_type": "payment_processed",
        "transaction_id": "tx_d1",
        "merchant_id": "m_3",
        "merchant_name": "Test",
        "amount": 100,
        "currency": "INR",
        "timestamp": "2026-01-01T00:00:00"
    })

    response = await client.get("/api/v1/reconciliation/discrepancies")

    assert response.status_code == 200