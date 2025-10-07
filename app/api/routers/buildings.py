from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, api_key_auth
from app.models import Building
from app.schemas.building import BuildingRead

router = APIRouter(prefix="/buildings", tags=["buildings"], dependencies=[Depends(api_key_auth)])


@router.get("/", response_model=List[BuildingRead])
def list_buildings(db: Session = Depends(get_db)):
    return db.query(Building).all()


