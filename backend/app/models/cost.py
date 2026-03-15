from pydantic import BaseModel
from typing import Optional
from enum import Enum


class CostCategory(str, Enum):
    maintenance = "maintenance"
    cleaning = "cleaning"
    utilities = "utilities"
    security = "security"
    renovation = "renovation"
    others = "others"


class CostStatus(str, Enum):
    pending = "pending"
    paid = "paid"
    cancelled = "cancelled"


class PaymentMethod(str, Enum):
    cash = "cash"
    bank_transfer = "bank_transfer"
    cheque = "cheque"
    online = "online"


class CostBase(BaseModel):
    building_id: str
    category: CostCategory
    description: str
    amount: float
    date: str
    vendor_id: Optional[str] = None
    reference_no: Optional[str] = None
    status: CostStatus = CostStatus.pending
    payment_method: Optional[PaymentMethod] = None
    notes: Optional[str] = None


class CostCreate(CostBase):
    pass


class CostUpdate(BaseModel):
    category: Optional[CostCategory] = None
    description: Optional[str] = None
    amount: Optional[float] = None
    date: Optional[str] = None
    vendor_id: Optional[str] = None
    reference_no: Optional[str] = None
    status: Optional[CostStatus] = None
    payment_method: Optional[PaymentMethod] = None
    notes: Optional[str] = None


class CostResponse(CostBase):
    id: str
    building_name: Optional[str] = None
    vendor_name: Optional[str] = None
