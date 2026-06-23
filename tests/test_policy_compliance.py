from tools.policy_compliance import check_policy_compliance


def test_policy_compliance_evaluates_all_eight_policies() -> None:
    request = {
        "vendor_id": "V-001",
        "category": "office_supplies",
        "cost_center_id": "CC-004",
        "quantity": 1,
        "total_amount": 5000.0,
        "manager_approved": True,
        "director_approved": False,
    }

    result = check_policy_compliance(request)

    assert result["evaluated_policy_ids"] == [
        "POL-001",
        "POL-002",
        "POL-003",
        "POL-004",
        "POL-005",
        "POL-006",
        "POL-007",
        "POL-008",
    ]


def test_policy_compliance_violation_shape_and_forced_decision() -> None:
    request = {
        "vendor_id": "V-017",
        "category": "catering",
        "cost_center_id": "CC-005",
        "quantity": 1,
        "total_amount": 2550.0,
    }

    result = check_policy_compliance(request)

    assert len(result["violations"]) >= 1
    violation = result["violations"][0]

    assert set(violation.keys()) == {"policy_id", "rule_violated", "forced_decision"}
    assert violation["policy_id"] == "POL-004"
    assert violation["forced_decision"] == "deny"


def test_policy_compliance_pol_004_catering_prohibition_req_009() -> None:
    request = {
        "request_id": "REQ-009",
        "vendor_id": "V-017",
        "category": "catering",
        "cost_center_id": "CC-005",
        "quantity": 1,
        "total_amount": 3200.0,
    }

    result = check_policy_compliance(request)

    violations = {item["policy_id"]: item for item in result["violations"]}
    assert "POL-004" in violations
    assert violations["POL-004"]["forced_decision"] == "deny"


def test_policy_compliance_pol_002_manager_approval_threshold() -> None:
    request = {
        "vendor_id": "V-011",
        "category": "security",
        "cost_center_id": "CC-001",
        "quantity": 1,
        "total_amount": 14200.0,
        "manager_approved": False,
        "director_approved": False,
    }

    result = check_policy_compliance(request)

    violations = {item["policy_id"]: item for item in result["violations"]}
    assert "POL-002" in violations
    assert violations["POL-002"]["forced_decision"] == "escalate"


def test_policy_compliance_pol_005_expired_contract_req_007() -> None:
    request = {
        "request_id": "REQ-007",
        "vendor_id": "V-010",
        "category": "marketing_materials",
        "cost_center_id": "CC-010",
        "quantity": 1,
        "total_amount": 5400.0,
    }

    result = check_policy_compliance(request)

    violations = {item["policy_id"]: item for item in result["violations"]}
    assert "POL-005" in violations
    assert violations["POL-005"]["forced_decision"] == "deny"


def test_policy_compliance_budget_overage_returns_pol_008_deny() -> None:
    request = {
        "vendor_id": "V-007",
        "category": "facilities",
        "cost_center_id": "CC-003",
        "quantity": 1,
        "total_amount": 11200.0,
    }

    result = check_policy_compliance(request)

    violations = {item["policy_id"]: item for item in result["violations"]}
    assert "POL-008" in violations
    assert violations["POL-008"]["forced_decision"] == "deny"
