from pydantic import BaseModel, EmailStr
from typing import List, Optional, Literal


class EntitlementItem(BaseModel):
    status: Literal["issued", "redeemed", "revoked"]
    email: EmailStr
    programTemplateId: str
    code: Optional[str] = None


class AutoEnrollRequest(BaseModel):
    email: EmailStr
    entitlements: List[EntitlementItem]


class RedeemRequest(BaseModel):
    code: str
    entitlement: EntitlementItem


