from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_user
from app.db.database import get_db
from app.models.apiary import Apiary
from app.models.feeding import Feeding
from app.models.harvest import Harvest
from app.models.hive import Hive, HiveStatus
from app.models.inspection import Inspection
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


@router.get("/harvest-by-crop")
def harvest_by_crop(
    from_date: date | None = None,
    to_date: date | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    query = db.query(Harvest.crop_type, func.sum(Harvest.amount_kg)).filter(Harvest.owner_id == current_user.id)
    if from_date:
        query = query.filter(Harvest.harvest_date >= from_date)
    if to_date:
        query = query.filter(Harvest.harvest_date <= to_date)
    return [
        {"crop_type": crop_type or "Unbekannt", "amount_kg": float(amount or 0)}
        for crop_type, amount in query.group_by(Harvest.crop_type).order_by(func.sum(Harvest.amount_kg).desc()).all()
    ]


@router.get("/harvest-by-apiary")
def harvest_by_apiary(
    from_date: date | None = None,
    to_date: date | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    query = (
        db.query(Apiary.id, Apiary.name, func.sum(Harvest.amount_kg))
        .join(Harvest, Harvest.apiary_id == Apiary.id)
        .filter(Harvest.owner_id == current_user.id)
    )
    if from_date:
        query = query.filter(Harvest.harvest_date >= from_date)
    if to_date:
        query = query.filter(Harvest.harvest_date <= to_date)
    return [
        {"apiary_id": apiary_id, "apiary_name": name, "amount_kg": float(amount or 0)}
        for apiary_id, name, amount in query.group_by(Apiary.id, Apiary.name).order_by(func.sum(Harvest.amount_kg).desc()).all()
    ]


@router.get("/varroa")
def varroa_report(
    from_date: date | None = None,
    to_date: date | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    query = db.query(Inspection.date, Hive.id, Hive.name, Inspection.varroa_count).join(Hive).filter(
        Hive.owner_id == current_user.id,
        Inspection.varroa_count.isnot(None),
    )
    if from_date:
        query = query.filter(Inspection.date >= from_date)
    if to_date:
        query = query.filter(Inspection.date <= to_date)
    return [
        {"date": seen_at, "hive_id": hive_id, "hive_name": hive_name, "varroa_count": float(varroa_count or 0)}
        for seen_at, hive_id, hive_name, varroa_count in query.order_by(Inspection.date.asc()).all()
    ]


@router.get("/feedings")
def feedings_report(
    from_date: date | None = None,
    to_date: date | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    query = (
        db.query(Apiary.id, Apiary.name, func.sum(Feeding.amount_kg_or_l))
        .join(Feeding, Feeding.apiary_id == Apiary.id)
        .filter(Feeding.owner_id == current_user.id)
    )
    if from_date:
        query = query.filter(Feeding.date >= from_date)
    if to_date:
        query = query.filter(Feeding.date <= to_date)
    return [
        {"apiary_id": apiary_id, "apiary_name": name, "amount_kg_or_l": float(amount or 0)}
        for apiary_id, name, amount in query.group_by(Apiary.id, Apiary.name).order_by(Apiary.name).all()
    ]
