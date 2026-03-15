from pydantic import BaseModel
from typing import Optional
from enum import Enum


class MaintenanceCategory(str, Enum):
    electrical = "electrical"
    plumbing = "plumbing"
    hvac = "hvac"
    elevator = "elevator"
    fire_safety = "fire_safety"
    general = "general"
    structural = "structural"


class MaintenancePriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class PMFrequency(str, Enum):
    monthly = "monthly"
    quarterly = "quarterly"
    biannual = "biannual"
    yearly = "yearly"


class PMStatus(str, Enum):
    scheduled = "scheduled"
    in_progress = "in_progress"
    completed = "completed"
    overdue = "overdue"
    cancelled = "cancelled"


class CMStatus(str, Enum):
    open = "open"
    in_progress = "in_progress"
    completed = "completed"
    closed = "closed"


# --- Preventive Maintenance ---
class PreventiveMaintenanceBase(BaseModel):
    building_id: str
    floor_id: Optional[str] = None
    unit_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    category: MaintenanceCategory = MaintenanceCategory.general
    frequency: PMFrequency = PMFrequency.monthly
    next_due_date: str
    assigned_vendor_id: Optional[str] = None
    status: PMStatus = PMStatus.scheduled
    priority: MaintenancePriority = MaintenancePriority.medium
    estimated_cost: Optional[float] = None


class PreventiveMaintenanceCreate(PreventiveMaintenanceBase):
    pass


class PreventiveMaintenanceUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[MaintenanceCategory] = None
    frequency: Optional[PMFrequency] = None
    next_due_date: Optional[str] = None
    assigned_vendor_id: Optional[str] = None
    status: Optional[PMStatus] = None
    priority: Optional[MaintenancePriority] = None
    estimated_cost: Optional[float] = None


class PreventiveMaintenanceResponse(PreventiveMaintenanceBase):
    id: str
    building_name: Optional[str] = None
    vendor_name: Optional[str] = None


# --- Corrective Maintenance ---
class CorrectiveMaintenanceBase(BaseModel):
    building_id: str
    floor_id: Optional[str] = None
    unit_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    category: MaintenanceCategory = MaintenanceCategory.general
    reported_by: Optional[str] = None
    reported_date: str
    assigned_vendor_id: Optional[str] = None
    status: CMStatus = CMStatus.open
    priority: MaintenancePriority = MaintenancePriority.medium
    actual_cost: Optional[float] = None
    completion_date: Optional[str] = None
    resolution_notes: Optional[str] = None


class CorrectiveMaintenanceCreate(CorrectiveMaintenanceBase):
    pass


class CorrectiveMaintenanceUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[MaintenanceCategory] = None
    assigned_vendor_id: Optional[str] = None
    status: Optional[CMStatus] = None
    priority: Optional[MaintenancePriority] = None
    actual_cost: Optional[float] = None
    completion_date: Optional[str] = None
    resolution_notes: Optional[str] = None


class CorrectiveMaintenanceResponse(CorrectiveMaintenanceBase):
    id: str
    building_name: Optional[str] = None
    floor_name: Optional[str] = None
    unit_number: Optional[str] = None
    vendor_name: Optional[str] = None
