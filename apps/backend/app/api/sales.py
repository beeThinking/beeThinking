from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_user
from app.crud import sale as sale_crud
from app.db.database import get_db
from app.models.user import User
from app.schemas.sale import SaleCreate, SaleReportRow, SaleResponse

router = APIRouter()


@router.get("", response_model=list[SaleResponse])
def list_sales(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    return sale_crud.get_sales(db, owner_id=current_user.id)


@router.post("", response_model=SaleResponse, status_code=status.HTTP_201_CREATED)
def create_sale(
    sale: SaleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    try:
        return sale_crud.create_sale(db, sale=sale, owner_id=current_user.id)
    except sale_crud.InsufficientStockError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    except sale_crud.InvalidSaleError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.get("/report", response_model=list[SaleReportRow])
def sales_report(
    from_date: date | None = None,
    to_date: date | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return sale_crud.sales_report(db, owner_id=current_user.id, from_date=from_date, to_date=to_date)


@router.get("/{sale_id}", response_model=SaleResponse)
def get_sale(
    sale_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_sale = sale_crud.get_sale(db, sale_id=sale_id, owner_id=current_user.id)
    if not db_sale:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sale not found")
    return db_sale


@router.delete("/{sale_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sale(
    sale_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if not sale_crud.delete_sale(db, sale_id=sale_id, owner_id=current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sale not found")
