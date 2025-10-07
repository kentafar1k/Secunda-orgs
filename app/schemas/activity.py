from typing import List, Optional
from pydantic import BaseModel


class ActivityBase(BaseModel):
    name: str
    parent_id: Optional[int] = None


class ActivityCreate(ActivityBase):
    pass


class Activity(ActivityBase):
    id: int

    class Config:
        from_attributes = True


class ActivityRead(Activity):
    children: List["ActivityRead"] = []  # populated only when needed


