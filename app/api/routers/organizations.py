from typing import List, Optional, Set
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_

from app.api.deps import get_db, api_key_auth
from app.models import Organization, Building, Activity, Phone
from app.models.organization import organization_activity
from app.schemas.organization import OrganizationRead, OrganizationSearchResponse

router = APIRouter(prefix="/organizations", tags=["organizations"], dependencies=[Depends(api_key_auth)])


@router.get("/{organization_id}", response_model=OrganizationRead)
def get_organization(organization_id: int, db: Session = Depends(get_db)):
    org = db.query(Organization).filter(Organization.id == organization_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return OrganizationRead(
        id=org.id,
        name=org.name,
        building_id=org.building_id,
        phones=[p.number for p in org.phones],
        activity_ids=[a.id for a in org.activities],
    )


@router.get("/by-building/{building_id}", response_model=List[OrganizationRead])
def organizations_by_building(building_id: int, db: Session = Depends(get_db)):
    orgs = db.query(Organization).filter(Organization.building_id == building_id).all()
    return [
        OrganizationRead(
            id=o.id,
            name=o.name,
            building_id=o.building_id,
            phones=[p.number for p in o.phones],
            activity_ids=[a.id for a in o.activities],
        )
        for o in orgs
    ]


def collect_activity_ids_recursive(db: Session, root_activity_id: int, max_depth: int = 3) -> Set[int]:
    # BFS up to depth 3
    collected: Set[int] = set()
    current_level = [root_activity_id]
    depth = 0
    while current_level and depth < max_depth:
        next_level = []
        for aid in current_level:
            collected.add(aid)
            children = db.query(Activity).filter(Activity.parent_id == aid).all()
            next_level.extend([c.id for c in children])
        current_level = next_level
        depth += 1
    return collected


@router.get("/by-activity/{activity_id}", response_model=List[OrganizationRead])
def organizations_by_activity(activity_id: int, db: Session = Depends(get_db)):
    ids = collect_activity_ids_recursive(db, activity_id, max_depth=3)
    orgs = (
        db.query(Organization)
        .join(organization_activity, Organization.id == organization_activity.c.organization_id)
        .filter(organization_activity.c.activity_id.in_(ids))
        .all()
    )
    return [
        OrganizationRead(
            id=o.id,
            name=o.name,
            building_id=o.building_id,
            phones=[p.number for p in o.phones],
            activity_ids=[a.id for a in o.activities],
        )
        for o in orgs
    ]


@router.get("/search", response_model=OrganizationSearchResponse)
def search_organizations(
    name: Optional[str] = Query(None, description="Substring match by name"),
    activity_id: Optional[int] = Query(None, description="Filter by activity including descendants (<=3 levels)"),
    activity_name: Optional[str] = Query(None, description="Filter by activity name (includes descendants)"),
    building_id: Optional[int] = Query(None, description="Filter by building"),
    lat: Optional[float] = Query(None, description="Latitude for geospatial search"),
    lon: Optional[float] = Query(None, description="Longitude for geospatial search"),
    radius_km: Optional[float] = Query(None, description="Radius in km around (lat, lon)"),
    min_lat: Optional[float] = Query(None),
    max_lat: Optional[float] = Query(None),
    min_lon: Optional[float] = Query(None),
    max_lon: Optional[float] = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    q = db.query(Organization)
    if name:
        q = q.filter(Organization.name.ilike(f"%{name}%"))
    if building_id:
        q = q.filter(Organization.building_id == building_id)
    if activity_name and not activity_id:
        act = db.query(Activity).filter(Activity.name == activity_name).first()
        if act:
            activity_id = act.id
    if activity_id:
        ids = collect_activity_ids_recursive(db, activity_id, max_depth=3)
        q = q.join(organization_activity, Organization.id == organization_activity.c.organization_id).filter(
            organization_activity.c.activity_id.in_(ids)
        )

    # Geospatial: either circle (radius) or bounding box
    if radius_km is not None and lat is not None and lon is not None:
        # naive haversine-like filter using bounding box approximation first
        # 1 deg lat ~ 111 km, 1 deg lon ~ 111 km * cos(lat)
        lat_delta = radius_km / 111.0
        lon_delta = radius_km / (111.0 * func.cos(func.radians(lat)))
        q = q.join(Building, Building.id == Organization.building_id).filter(
            and_(
                Building.latitude.between(lat - lat_delta, lat + lat_delta),
                Building.longitude.between(lon - lon_delta, lon + lon_delta),
            )
        )
    elif None not in (min_lat, max_lat, min_lon, max_lon):
        q = q.join(Building, Building.id == Organization.building_id).filter(
            and_(
                Building.latitude.between(min_lat, max_lat),
                Building.longitude.between(min_lon, max_lon),
            )
        )

    total = q.count()
    orgs = q.offset(skip).limit(limit).all()
    results = [
        OrganizationRead(
            id=o.id,
            name=o.name,
            building_id=o.building_id,
            phones=[p.number for p in o.phones],
            activity_ids=[a.id for a in o.activities],
        )
        for o in orgs
    ]
    return OrganizationSearchResponse(results=results, total=total)


