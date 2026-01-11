# backend/routers/history.py
from fastapi import APIRouter
from backend.db import list_invoices

router = APIRouter(tags=["history"])

@router.get("/history")
def history(limit: int = 50):
    return {"items": list_invoices(limit=limit)}
