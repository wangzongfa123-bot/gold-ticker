from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import crud, schemas

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.get("/", response_model=list[schemas.AlertOut])
def list_alerts(db: Session = Depends(get_db)):
    return crud.get_alerts(db)


@router.post("/", response_model=schemas.AlertOut)
def create_alert(alert: schemas.AlertCreate, db: Session = Depends(get_db)):
    if alert.condition not in ("above", "below"):
        raise HTTPException(400, "condition must be 'above' or 'below'")
    return crud.create_alert(
        db, name=alert.name, condition=alert.condition,
        threshold=alert.threshold,
    )


@router.put("/{alert_id}", response_model=schemas.AlertOut)
def update_alert(alert_id: int, alert: schemas.AlertUpdate, db: Session = Depends(get_db)):
    updated = crud.update_alert(db, alert_id, **alert.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(404, "Alert not found")
    return updated


@router.delete("/{alert_id}")
def delete_alert(alert_id: int, db: Session = Depends(get_db)):
    if not crud.delete_alert(db, alert_id):
        raise HTTPException(404, "Alert not found")
    return {"ok": True}
