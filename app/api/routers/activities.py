from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, api_key_auth
from app.models import Activity
from app.schemas.activity import Activity as ActivitySchema

router = APIRouter(prefix="/activities", tags=["activities"], dependencies=[Depends(api_key_auth)])


@router.get("/", response_model=List[ActivitySchema])
def list_activities(db: Session = Depends(get_db)):
    return db.query(Activity).all()


@router.get("/{activity_id}", response_model=ActivitySchema)
def get_activity(activity_id: int, db: Session = Depends(get_db)):
    act = db.query(Activity).filter(Activity.id == activity_id).first()
    if not act:
        raise HTTPException(status_code=404, detail="Activity not found")
    return act


