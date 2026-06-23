from tools.check_policy_compliance import check_policy_compliance


def test_check_policy_compliance_evaluates_all_policies() -> None:
    request = {
        "request_id": "REQ-TST-001",
        "vendor_id": "V-001",
        "category": "office_supplies",
        "cost_center_id": "CC-004",
        "quantity": 1,
        "total_amount": 5000.0,
        "manager_approved": True,
        "director_approved": False,
    }

    result = check_policy_compliance(request)

    assert len(result["evaluated_policy_ids"]) == 8
    assert set(result["evaluated_policy_ids"]) == {
        "POL-001",
        "POL-002",
        "POL-003",
        "POL-004",
        "POL-005",
        "POL-006",
        "POL-007",
        "POL-008",
    }


def test_check_policy_compliance_returns_policy_001_and_002_violations() -> None:
    request = {
        "request_id": "REQ-TST-002",
        "vendor_id": "V-012",
        "category": "office_supplies",
        "cost_center_id": "CC-004",
        "quantity": 1,
        "total_amount": 28500.0,
        "manager_approved": False,
        "director_approved": False,
    }

    result = check_policy_compliance(request)

    violations = {violation["policy_id"]: violation for violation in result["violations"]}

    assert "POL-001" in violations
    assert violations["POL-001"]["forced_decision"] == "deny"

    assert "POL-002" in violations
    assert violations["POL-002"]["forced_decision"] == "escalate"


def test_check_policy_compliance_returns_policy_006_escalate() -> None:
    request = {
        "request_id": "REQ-TST-003",
        "vendor_id": "V-006",
        "category": "professional_services",
        "cost_center_id": "CC-001",
        "quantity": 1,
        "total_amount": 35000.0,
        "manager_approved": True,
        "director_approved": False,
    }

    result = check_policy_compliance(request)

    policy_ids = [violation["policy_id"] for violation in result["violations"]]
    assert "POL-006" in policy_ids

    pol_006 = next(
        violation for violation in result["violations"] if violation["policy_id"] == "POL-006"
    )
    assert pol_006["forced_decision"] == "escalate"


def test_check_policy_compliance_returns_policy_008_deny() -> None:
    request = {
        "request_id": "REQ-TST-004",
        "vendor_id": "V-007",
        "category": "facilities",
        "cost_center_id": "CC-003",
        "quantity": 1,
        "total_amount": 11200.0,
        "manager_approved": False,
        "director_approved": False,
    }

    result = check_policy_compliance(request)

    violations = {violation["policy_id"]: violation for violation in result["violations"]}
    assert "POL-008" in violations
    assert violations["POL-008"]["forced_decision"] == "deny"


def test_check_policy_compliance_violation_shape() -> None:
    request = {
        "request_id": "REQ-TST-005",
        "vendor_id": "V-010",
        "category": "marketing_materials",
        "cost_center_id": "CC-010",
        "quantity": 1,
        "total_amount": 5400.0,
        "manager_approved": True,
        "director_approved": False,
    }

    result = check_policy_compliance(request)

    assert len(result["violations"]) >= 1
    for violation in result["violations"]:
        assert violation["policy_id"].startswith("POL-")
        assert violation["rule_violated"]
        assert violation["forced_decision"] in {"deny", "escalate"}
