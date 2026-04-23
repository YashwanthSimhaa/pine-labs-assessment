from fastapi import APIRouter, Depends
from sqlalchemy.exc import IntegrityError
from app.utils.state_machine import derive_status
from app.schemas.event import EventCreate
from app.api.deps import get_db
from app.core.config import settings
from app.models.event import Event
from app.models.transaction import Transaction
from app.models.merchant import Merchant

router = APIRouter(prefix=settings.API_PREFIX, tags=["Events"])

@router.post("/events")
async def ingest_events(payload: EventCreate, db=Depends(get_db)):
    """
    API to ingest events related to transactions. It accepts event details in the request body and processes them accordingly.
    """
    try:
        async with db.begin():  # atomic transaction

            # 1. Insert event FIRST (idempotency via DB constraint)
            event = Event(
                id=payload.event_id,
                event_type=payload.event_type,
                transaction_id=payload.transaction_id,
                merchant_id=payload.merchant_id,
                amount=payload.amount,
                currency=payload.currency,
                timestamp=payload.timestamp
            )
            db.add(event)

            # 2. Upsert merchant
            merchant = await db.get(Merchant, payload.merchant_id)
            if not merchant:
                merchant = Merchant(
                    id=payload.merchant_id,
                    name=payload.merchant_name
                )
                db.add(merchant)

            # 3. Upsert transaction
            transaction = await db.get(Transaction, payload.transaction_id)

            if not transaction:
                transaction = Transaction(
                    id=payload.transaction_id,
                    merchant_id=payload.merchant_id,
                    amount=payload.amount,
                    currency=payload.currency,
                    status="payment_initiated",
                    created_at=payload.timestamp
                )
                db.add(transaction)
            else:
                transaction.amount = payload.amount

            # 4. Update status safely
            transaction.status = derive_status(
                transaction.status,
                payload.event_type
            )

        return {"message": "Event processed"}

    except IntegrityError:
        # duplicate event (idempotent behavior)
        await db.rollback()
        return {"message": "Duplicate event ignored"}