from fastapi import APIRouter, Depends
from sqlalchemy import select, func, case
from app.models.transaction import Transaction
from app.models.event import Event
from app.api.deps import get_db
from app.core.config import settings

router = APIRouter(prefix=settings.API_PREFIX, tags=["Reconciliation"])

@router.get("/reconciliation/summary")
async def reconciliation_summary(db=Depends(get_db)):
    """
    API to provide a summary of transactions for reconciliation purposes. It aggregates transaction data by merchant, date, and status, providing counts and total amounts for each group.
    """
    query = select(
        Transaction.merchant_id,
        func.date(Transaction.created_at).label("date"),
        Transaction.status,
        func.count().label("count"),
        func.sum(Transaction.amount).label("total_amount")
    ).group_by(
        Transaction.merchant_id,
        func.date(Transaction.created_at),
        Transaction.status
    )

    result = await db.execute(query)

    return result.mappings().all()


@router.get("/reconciliation/discrepancies")
async def reconciliation_discrepancies(db=Depends(get_db)):
    """
    API to identify discrepancies in transactions based on their associated events. It checks for transactions that have inconsistent event patterns, such as a transaction that has a "payment_processed" event but no corresponding "settled" event, or a transaction that has a "payment_failed" event but also has a "settled" event.
    """
    subquery = (
        select(
            Event.transaction_id,
            func.sum(case((Event.event_type == "payment_processed", 1), else_=0)).label("processed"),
            func.sum(case((Event.event_type == "payment_failed", 1), else_=0)).label("failed"),
            func.sum(case((Event.event_type == "settled", 1), else_=0)).label("settled")
        )
        .group_by(Event.transaction_id)
        .subquery()
    )

    query = (
        select(Transaction)
        .join(subquery, Transaction.id == subquery.c.transaction_id)
        .where(
            # Case 1: processed but not settled
            (subquery.c.processed > 0) & (subquery.c.settled == 0)
            |
            # Case 2: failed but settled
            (subquery.c.failed > 0) & (subquery.c.settled > 0)
            |
            # Case 3: both processed and failed exist
            (subquery.c.processed > 0) & (subquery.c.failed > 0)
        )
    )

    result = await db.execute(query)

    return result.scalars().all()