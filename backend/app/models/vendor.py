from pydantic import BaseModel, EmailStr
from typing import Optional
from enum import Enum
from datetime import date


class VendorType(str, Enum):
    cleaning = "cleaning"
    maintenance = "maintenance"
    security = "security"
    other = "other"


class VendorStatus(str, Enum):
    active = "active"
    inactive = "inactive"
    suspended = "suspended"


class VendorBase(BaseModel):
    name: str
    type: VendorType
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    status: VendorStatus = VendorStatus.active
    contract_start: Optional[str] = None
    contract_end: Optional[str] = None
    hourly_rate: Optional[float] = None


class VendorCreate(VendorBase):
    pass


class VendorUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[VendorType] = None
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    status: Optional[VendorStatus] = None
    contract_start: Optional[str] = None
    contract_end: Optional[str] = None
    hourly_rate: Optional[float] = None


class VendorResponse(VendorBase):
    id: str
