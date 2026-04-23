from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import selectinload
from sqlalchemy import select, asc, desc, func
from typing import Optional
from datetime import datetime
from app.models.transaction import Transaction
from app.api.deps import get_db
from app.core.config import settings

router = APIRouter(prefix=settings.API_PREFIX, tags=["Transactions"])

@router.get("/transactions")
async def list_transactions(
    merchant_id: Optional[str] = Query(None, description="Filter by merchant ID"),
    status: Optional[str] = Query(None, description="Filter by transaction status (e.g., payment_initiated, payment_processed, payment_failed, settled)"),
    start_date: Optional[datetime] = Query(
        None,
        description="Start date in ISO format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)",
        example="2026-01-01"
    ),
    end_date: Optional[datetime] = Query(
        None,
        description="End date in ISO format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)",
        example="2026-01-31"
    ),
    limit: int = Query(10, le=100, description="Number of records to return (max 100)"),
    offset: int = Query(0, description="Number of records to skip for pagination"),
    sort_by: str = Query(
        "created_at",
        description="Field to sort by (created_at, amount, status)"
    ),
    sort_order: str = Query(
        "desc",
        description="Sort order: asc or desc"
    ),
    db=Depends(get_db)
):
    """
    API to list transactions with support for filtering, pagination, and sorting. It allows clients to filter transactions based on merchant ID, status, and date range, as well as sort the results by specified fields in ascending or descending order.
    The response includes the total count of transactions, the count of transactions after applying filters, and the list of transactions for the current page.
    """
    base_query = select(Transaction)

    # Filtering
    if merchant_id:
        base_query = base_query.where(Transaction.merchant_id == merchant_id)

    if status:
        base_query = base_query.where(Transaction.status == status)

    if start_date:
        base_query = base_query.where(Transaction.created_at >= start_date)

    if end_date:
        base_query = base_query.where(Transaction.created_at <= end_date)

    # Filtered count
    filtered_count_query = select(func.count()).select_from(base_query.subquery())
    filtered_result = await db.execute(filtered_count_query)
    filtered_count = filtered_result.scalar()

    # Total count
    total_result = await db.execute(select(func.count()).select_from(Transaction))
    total_count = total_result.scalar()

    # Sorting
    allowed_sort_fields = {"created_at", "amount", "status"}

    if sort_by not in allowed_sort_fields:
        sort_by = "created_at"

    sort_column = getattr(Transaction, sort_by, Transaction.created_at)

    if sort_order == "asc":
        base_query = base_query.order_by(asc(sort_column))
    else:
        base_query = base_query.order_by(desc(sort_column))

    # Pagination
    paginated_query = base_query.limit(limit).offset(offset)

    result = await db.execute(paginated_query)
    transactions = result.scalars().all()

    # Response formatting
    return {
        "total": total_count,
        "filtered": filtered_count,
        "limit": limit,
        "offset": offset,
        "data": [
            {
                "id": t.id,
                "merchant_id": t.merchant_id,
                "amount": t.amount,
                "currency": t.currency,
                "status": t.status,
                "created_at": t.created_at
            }
            for t in transactions
        ]
    }



@router.get("/transactions/{transaction_id}")
async def fetch_transaction_details(transaction_id: str, db=Depends(get_db)):
    """
    API to fetch detailed information about a specific transaction, including its associated events and merchant details. It retrieves the transaction by its ID and includes related data such as the merchant's name and the list of events linked to the transaction.
     If the transaction is not found, it returns a 404 error.
    """
    result = await db.execute(
        select(Transaction)
        .options(
            selectinload(Transaction.events),
            selectinload(Transaction.merchant)
        )
        .where(Transaction.id == transaction_id)
    )

    transaction = result.scalars().first()

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    return {
        "transaction": {
            "id": transaction.id,
            "merchant_id": transaction.merchant_id,
            "amount": transaction.amount,
            "currency": transaction.currency,
            "status": transaction.status,
            "created_at": transaction.created_at
        },
        "merchant": {
            "id": transaction.merchant.id,
            "name": transaction.merchant.name
        } if transaction.merchant else None,
        "events": [
            {
                "event_id": event.id,
                "event_type": event.event_type,
                "transaction_id": event.transaction_id,
                "merchant_id": event.merchant_id,
                "amount": event.amount,
                "currency": event.currency,
                "timestamp": event.timestamp
            }
            for event in transaction.events
        ]
    }