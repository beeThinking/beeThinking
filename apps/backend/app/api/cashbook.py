from datetime import date

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_user
from app.crud import cashbook as cashbook_crud
from app.db.database import get_db
from app.models.user import User
from app.schemas.cashbook import (
    CashbookEntryCreate,
    CashbookEntryResponse,
    CashbookEntryUpdate,
    CashbookReceiptResponse,
    CashbookSummary,
)

router = APIRouter()


@router.get("/entries", response_model=list[CashbookEntryResponse])
def list_entries(
    from_date: date | None = None,
    to_date: date | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return cashbook_crud.list_entries(db, current_user.id, from_date=from_date, to_date=to_date)


@router.post("/entries", response_model=CashbookEntryResponse, status_code=status.HTTP_201_CREATED)
def create_entry(
    entry: CashbookEntryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    created = cashbook_crud.create_entry(db, entry, user_id=current_user.id)
    if not created:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Related apiary not found")
    return created


@router.put("/entries/{entry_id}", response_model=CashbookEntryResponse)
def update_entry(
    entry_id: int,
    entry: CashbookEntryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    updated = cashbook_crud.update_entry(db, entry_id, entry, user_id=current_user.id)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cashbook entry not found")
    return updated


@router.delete("/entries/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if not cashbook_crud.delete_entry(db, entry_id, user_id=current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cashbook entry not found")


@router.get("/summary", response_model=CashbookSummary)
def get_summary(
    from_date: date | None = None,
    to_date: date | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    income, expenses = cashbook_crud.summary(db, current_user.id, from_date=from_date, to_date=to_date)
    return CashbookSummary(income=income, expenses=expenses, surplus=income - expenses)


@router.get("/receipts", response_model=list[CashbookReceiptResponse])
def list_receipts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return cashbook_crud.list_receipts(db, current_user.id)


@router.post("/receipts", response_model=CashbookReceiptResponse, status_code=status.HTTP_201_CREATED)
async def upload_receipt(
    file: UploadFile = File(...),
    ocr_text: str | None = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    content = await file.read()
    return cashbook_crud.create_receipt(
        db,
        user_id=current_user.id,
        filename=file.filename or "receipt",
        content_type=file.content_type or "application/octet-stream",
        size_bytes=len(content),
        ocr_text=ocr_text,
    )
