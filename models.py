from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator


class PurchaseRequest(BaseModel):
    """Validated input model for procurement purchase requests."""

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

    @field_validator(
        "request_id",
        "requestor",
        "cost_center_id",
        "vendor_name",
        "vendor_id",
        "category",
        "item_description",
    )
    @classmethod
    def must_be_non_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("field must be non-empty")
        return value

    @model_validator(mode="after")
    def validate_total_amount_consistency(self) -> "PurchaseRequest":
        expected_total = self.quantity * self.unit_price
        tolerance = 0.01
        if abs(self.total_amount - expected_total) > tolerance:
            raise ValueError(
                "total_amount must match quantity * unit_price within 0.01 tolerance"
            )
        return self


class ProcurementRecommendation(BaseModel):
    """Structured recommendation output constrained to procurement decisions."""

    decision: Literal["approve", "deny", "escalate"]
    rationale: str

    @field_validator("rationale")
    @classmethod
    def rationale_must_be_non_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("rationale must be non-empty")
        return value
