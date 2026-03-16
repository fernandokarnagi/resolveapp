from pydantic import BaseModel
from typing import Optional, List
from enum import Enum


class ClientStatus(str, Enum):
    active = "active"
    inactive = "inactive"


class ClientContact(BaseModel):
    name: str
    role: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None


class ClientBase(BaseModel):
    name: str
    registration_number: Optional[str] = None
    industry: Optional[str] = None
    website: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address_street: Optional[str] = None
    address_city: Optional[str] = None
    address_state: Optional[str] = None
    address_country: Optional[str] = None
    address_postal: Optional[str] = None
    contacts: List[ClientContact] = []
    status: ClientStatus = ClientStatus.active
    notes: Optional[str] = None


class ClientCreate(ClientBase):
    pass


class ClientUpdate(BaseModel):
    name: Optional[str] = None
    registration_number: Optional[str] = None
    industry: Optional[str] = None
    website: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address_street: Optional[str] = None
    address_city: Optional[str] = None
    address_state: Optional[str] = None
    address_country: Optional[str] = None
    address_postal: Optional[str] = None
    contacts: Optional[List[ClientContact]] = None
    status: Optional[ClientStatus] = None
    notes: Optional[str] = None


class ClientResponse(ClientBase):
    id: str
