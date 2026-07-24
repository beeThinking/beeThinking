from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_user
from app.crud.honey_price_calculator import calculate_honey_price
from app.db.database import get_db
from app.models.user import User
from app.schemas.honey_price_calculator import HoneyPriceCalculatorRequest, HoneyPriceCalculatorResponse

router = APIRouter()


@router.post("/calculate", response_model=HoneyPriceCalculatorResponse)
def calculate(
    payload: HoneyPriceCalculatorRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Honigpreis-Rechner (#44). Requires auth because it reads real cashbook/harvest data."""
    result = calculate_honey_price(db, owner_id=current_user.id, payload=payload)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Apiary not found")
    return result
