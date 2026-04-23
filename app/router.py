from fastapi import APIRouter
from app.api.v1 import events, transactions, reconciliation, health

router = APIRouter()

router.include_router(health.router)
router.include_router(events.router)
router.include_router(transactions.router)
router.include_router(reconciliation.router)