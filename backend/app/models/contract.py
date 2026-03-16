from pydantic import BaseModel
from typing import Optional, List
from enum import Enum


class ContractStatus(str, Enum):
    draft = "draft"
    active = "active"
    expired = "expired"
    terminated = "terminated"


class ContractBase(BaseModel):
    contract_number: str
    client_id: str
    title: str
    description: Optional[str] = None
    building_ids: List[str] = []
    start_date: str
    end_date: Optional[str] = None
    value: Optional[float] = None
    currency: str = "SGD"
    status: ContractStatus = ContractStatus.active
    notes: Optional[str] = None


class ContractCreate(ContractBase):
    pass


class ContractUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    building_ids: Optional[List[str]] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    value: Optional[float] = None
    currency: Optional[str] = None
    status: Optional[ContractStatus] = None
    notes: Optional[str] = None


class ContractResponse(ContractBase):
    id: str
    client_name: Optional[str] = None
    building_names: List[str] = []
