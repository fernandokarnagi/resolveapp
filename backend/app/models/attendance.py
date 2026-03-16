from pydantic import BaseModel
from typing import Optional
from enum import Enum


class AttendanceStatus(str, Enum):
    present = "present"
    absent = "absent"
    late = "late"
    half_day = "half_day"


class AttendanceType(str, Enum):
    cleaner = "cleaner"
    security = "security"


class AttendanceBase(BaseModel):
    attendance_type: AttendanceType
    person_id: str
    building_id: str
    date: str
    check_in_time: Optional[str] = None
    check_out_time: Optional[str] = None
    status: AttendanceStatus = AttendanceStatus.present
    notes: Optional[str] = None
    supervisor_name: Optional[str] = None
    reviewed_by: Optional[str] = None
    reviewed_datetime: Optional[str] = None
    review_remarks: Optional[str] = None


class AttendanceCreate(AttendanceBase):
    pass


class AttendanceUpdate(BaseModel):
    check_in_time: Optional[str] = None
    check_out_time: Optional[str] = None
    status: Optional[AttendanceStatus] = None
    notes: Optional[str] = None
    supervisor_name: Optional[str] = None
    reviewed_by: Optional[str] = None
    reviewed_datetime: Optional[str] = None
    review_remarks: Optional[str] = None


class AttendanceResponse(AttendanceBase):
    id: str
    building_name: Optional[str] = None
    person_name: Optional[str] = None
