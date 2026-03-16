from pydantic import BaseModel
from typing import Optional, List
from enum import Enum


class ShiftType(str, Enum):
    morning = "morning"
    evening = "evening"
    night = "night"


class RosterStatus(str, Enum):
    scheduled = "scheduled"
    confirmed = "confirmed"
    completed = "completed"
    cancelled = "cancelled"


class RosterBase(BaseModel):
    building_id: str
    date: str
    shift: ShiftType
    assigned_officer_ids: List[str] = []
    start_time: str
    end_time: str
    contract_id: Optional[str] = None
    notes: Optional[str] = None
    status: RosterStatus = RosterStatus.scheduled


class RosterCreate(RosterBase):
    pass


class RosterUpdate(BaseModel):
    date: Optional[str] = None
    shift: Optional[ShiftType] = None
    assigned_officer_ids: Optional[List[str]] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    contract_id: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[RosterStatus] = None


class RosterResponse(RosterBase):
    id: str
    building_name: Optional[str] = None
    officer_names: Optional[List[str]] = None
    contract_number: Optional[str] = None
