from pydantic import BaseModel
from typing import Optional, List
from enum import Enum


class CleaningFrequency(str, Enum):
    daily = "daily"
    weekly = "weekly"
    biweekly = "biweekly"
    monthly = "monthly"


class CleaningStatus(str, Enum):
    scheduled = "scheduled"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"


class CleaningScheduleBase(BaseModel):
    building_id: str
    floor_id: Optional[str] = None
    unit_id: Optional[str] = None
    assigned_vendor_id: Optional[str] = None
    title: str
    frequency: CleaningFrequency = CleaningFrequency.daily
    start_date: str
    end_date: Optional[str] = None
    start_time: Optional[str] = None
    duration_minutes: Optional[int] = None
    schedule_days: Optional[List[str]] = None
    schedule_dates: Optional[List[int]] = None
    status: CleaningStatus = CleaningStatus.scheduled
    notes: Optional[str] = None


class CleaningScheduleCreate(CleaningScheduleBase):
    pass


class CleaningScheduleUpdate(BaseModel):
    title: Optional[str] = None
    assigned_vendor_id: Optional[str] = None
    frequency: Optional[CleaningFrequency] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    start_time: Optional[str] = None
    duration_minutes: Optional[int] = None
    schedule_days: Optional[List[str]] = None
    schedule_dates: Optional[List[int]] = None
    status: Optional[CleaningStatus] = None
    notes: Optional[str] = None


class CleaningScheduleResponse(CleaningScheduleBase):
    id: str
    building_name: Optional[str] = None
    vendor_name: Optional[str] = None
