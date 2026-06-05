from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_user
from app.db.database import get_db
from app.models.hive import Hive, HiveStatus
from app.models.user import User

router = APIRouter()


@router.get("/yearly")
def yearly_report(
    year: int = date.today().year,
    include_archived: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    query = db.query(Hive).filter(Hive.owner_id == current_user.id)
    if not include_archived:
        query = query.filter(Hive.is_active.is_(True))
    hives = query.all()
    return {
        "year": year,
        "include_archived": include_archived,
        "active_hives": sum(1 for hive in hives if hive.status == HiveStatus.active),
        "new_hives": sum(1 for hive in hives if hive.created_at and hive.created_at.year == year),
        "sold_hives": sum(1 for hive in hives if hive.status == HiveStatus.sold),
        "merged_hives": sum(1 for hive in hives if hive.status == HiveStatus.merged),
        "losses": sum(1 for hive in hives if hive.status in {HiveStatus.dead, HiveStatus.lost}),
        "hives": [
            {
                "id": hive.id,
                "name": hive.name,
                "status": hive.status,
                "archived_at": hive.archived_at,
                "merged_into_hive_id": hive.merged_into_hive_id,
            }
            for hive in hives
        ],
    }
