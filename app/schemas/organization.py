from typing import List
from pydantic import BaseModel


class OrganizationBase(BaseModel):
    name: str
    building_id: int
    activity_ids: List[int] = []
    phones: List[str] = []


class OrganizationCreate(OrganizationBase):
    pass


class Organization(OrganizationBase):
    id: int

    class Config:
        from_attributes = True


class OrganizationRead(BaseModel):
    id: int
    name: str
    building_id: int
    phones: List[str]
    activity_ids: List[int]


class OrganizationSearchResponse(BaseModel):
    results: List[OrganizationRead]
    total: int


