import json
import httpx
import asyncio
from pathlib import Path
from app.core.config import settings

URL = f"{settings.BASE_URL}{settings.API_PREFIX}/events"
FILE_PATH = Path(__file__).resolve().parent.parent / "data" / "sample_events.json"

print(f"\nLoading sample data from {FILE_PATH} to {URL}")

BATCH_SIZE = 50
SLEEP_TIME = 0.1

async def safe_post(client, event):
    try:
        response = await client.post(URL, json=event)
        return response
    except Exception as e:
        return e

async def send_batch(client, batch, batch_num):
    tasks = [safe_post(client, event) for event in batch]
    responses = await asyncio.gather(*tasks, return_exceptions=True)

    success = 0
    failed = 0

    for r in responses:
        if isinstance(r, httpx.Response):
            if r.status_code == 200:
                success += 1
            else:
                failed += 1
                print(f"\nHTTP Error: {r.status_code} | {r.text[:100]}")
        else:
            failed += 1
            print(f"\nException: {r}")

    print(f"Batch {batch_num}: {success} success | {failed} failed")


async def load():
    try:
        if not FILE_PATH.exists():
            raise FileNotFoundError(f"{FILE_PATH} not found")

        with open(FILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

    except FileNotFoundError as e:
        print(f"Error: {e}")
        return
    except json.JSONDecodeError:
        print("Error: Invalid JSON format")
        return

    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            await client.get(f"{settings.BASE_URL}{settings.API_PREFIX}/health-check")
    except Exception:
        print("\nAPI server is not running")
        return

    async with httpx.AsyncClient(timeout=5.0) as client:
        for i in range(0, len(data), BATCH_SIZE):
            batch = data[i:i + BATCH_SIZE]
            await send_batch(client, batch, i // BATCH_SIZE + 1)
            await asyncio.sleep(SLEEP_TIME)

    print("\nSample data loaded successfully")


if __name__ == "__main__":
    asyncio.run(load())