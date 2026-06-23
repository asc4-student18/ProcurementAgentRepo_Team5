from typing import Literal

from pydantic import BaseModel, Field, field_validator


class PurchaseRequest(BaseModel):
    request_id: str
    requestor: str
    cost_center_id: str
    vendor_name: str
    vendor_id: str
    category: str
    item_description: str
    quantity: int = Field(gt=0)
    unit_price: float = Field(gt=0)
    total_amount: float = Field(gt=0)
    manager_approved: bool = False
    director_approved: bool = False


class ProcurementRecommendation(BaseModel):
    decision: Literal["approve", "deny", "escalate"]
    rationale: str

    @field_validator("rationale")
    @classmethod
    def rationale_must_be_non_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("rationale must be non-empty")
        return value


class VendorContractConflict(BaseModel):
    vendor_id: str
    vendor_name: str
    category: str
    contract_id: str
    contract_status: str


class VendorDuplicationResult(BaseModel):
    requested_vendor_id: str
    purchase_category: str
    total_amount: float | None = None
    policy_id: str = "POL-001"
    threshold_amount: float = Field(default=25000.0, ge=0)
    has_active_contract_conflict: bool
    deny_triggered: bool
    conflicting_vendor_ids: list[str]
    conflicting_contracts: list[VendorContractConflict]
    message: str


class PolicyViolation(BaseModel):
    policy_id: str
    rule_violated: str
    forced_decision: str


class PolicyComplianceResult(BaseModel):
    request_id: str | None = None
    violations: list[PolicyViolation]
    evaluated_policy_ids: list[str]


class VendorRiskProfile(BaseModel):
    vendor_id: str
    compliance_flag: bool
    contract_status: str
    risk_level: Literal["low", "medium", "high", "critical"]
