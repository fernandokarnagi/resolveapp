from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class BuildingStatus(str, Enum):
    active = "active"
    inactive = "inactive"
    under_maintenance = "under_maintenance"


class UnitType(str, Enum):
    residential = "residential"
    commercial = "commercial"
    common = "common"


class UnitStatus(str, Enum):
    occupied = "occupied"
    vacant = "vacant"
    maintenance = "maintenance"


# --- Building ---
class BuildingBase(BaseModel):
    name: str
    address: str
    total_floors: int = 0
    status: BuildingStatus = BuildingStatus.active
    description: Optional[str] = None
    client_id: Optional[str] = None


class BuildingCreate(BuildingBase):
    pass


class BuildingUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    total_floors: Optional[int] = None
    status: Optional[BuildingStatus] = None
    description: Optional[str] = None
    client_id: Optional[str] = None


class BuildingResponse(BuildingBase):
    id: str
    client_name: Optional[str] = None


# --- Floor ---
class FloorBase(BaseModel):
    floor_number: int
    name: str
    building_id: str
    total_units: int = 0


class FloorCreate(FloorBase):
    pass


class FloorUpdate(BaseModel):
    floor_number: Optional[int] = None
    name: Optional[str] = None
    total_units: Optional[int] = None


class FloorResponse(FloorBase):
    id: str
    building_name: Optional[str] = None


# --- Unit ---
class UnitBase(BaseModel):
    unit_number: str
    floor_id: str
    building_id: str
    type: UnitType = UnitType.residential
    status: UnitStatus = UnitStatus.vacant
    area_sqft: Optional[float] = None
    tenant_name: Optional[str] = None
    tenant_contact: Optional[str] = None


class UnitCreate(UnitBase):
    pass


class UnitUpdate(BaseModel):
    unit_number: Optional[str] = None
    type: Optional[UnitType] = None
    status: Optional[UnitStatus] = None
    area_sqft: Optional[float] = None
    tenant_name: Optional[str] = None
    tenant_contact: Optional[str] = None


class UnitResponse(UnitBase):
    id: str
    building_name: Optional[str] = None
    floor_name: Optional[str] = None
