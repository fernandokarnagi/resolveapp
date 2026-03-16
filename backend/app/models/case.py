from pydantic import BaseModel
from typing import Optional
from enum import Enum


class CaseStatus(str, Enum):
    open = "open"
    in_progress = "in_progress"
    resolved = "resolved"
    closed = "closed"


class CasePriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class CaseCategory(str, Enum):
    complaint = "complaint"
    request = "request"
    emergency = "emergency"
    inquiry = "inquiry"
    other = "other"


class CaseBase(BaseModel):
    building_id: str
    floor_id: Optional[str] = None
    unit_id: Optional[str] = None
    title: str
    description: str
    category: CaseCategory = CaseCategory.request
    reported_by: Optional[str] = None
    contact_phone: Optional[str] = None
    contract_id: Optional[str] = None
    status: CaseStatus = CaseStatus.open
    priority: CasePriority = CasePriority.medium
    assigned_to: Optional[str] = None
    resolution_notes: Optional[str] = None


class CaseCreate(CaseBase):
    pass


class CaseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[CaseCategory] = None
    status: Optional[CaseStatus] = None
    priority: Optional[CasePriority] = None
    assigned_to: Optional[str] = None
    contract_id: Optional[str] = None
    resolution_notes: Optional[str] = None


class CaseResponse(CaseBase):
    id: str
    case_number: str
    building_name: Optional[str] = None
    floor_name: Optional[str] = None
    unit_number: Optional[str] = None
    contract_number: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
