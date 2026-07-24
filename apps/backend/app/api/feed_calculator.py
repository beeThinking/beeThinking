from fastapi import APIRouter

from app.schemas.feed_calculator import FeedCalculatorRequest, FeedCalculatorResponse
from app.services.feed_calculator import calculate_feed_quantity

router = APIRouter()


@router.post("/calculate", response_model=FeedCalculatorResponse)
def calculate(payload: FeedCalculatorRequest):
    """Futtermengen-Rechner (#43). Public/unauthenticated — same as app.api.content's
    public routes, matching the existing pattern for endpoints with no Depends(get_current_user)."""
    return calculate_feed_quantity(payload)
