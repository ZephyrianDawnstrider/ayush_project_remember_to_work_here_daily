import pytest
from fastapi.testclient import TestClient

from app.calculators.fastener import bolt_shear_margin
from app.main import app


def test_bolt_shear_margin_is_positive_when_allowable_exceeds_applied():
    margin = bolt_shear_margin(applied_shear_lbf=1000.0, allowable_shear_lbf=1500.0)

    assert margin == pytest.approx(0.5)


def test_bolt_shear_margin_is_zero_at_limit_load():
    margin = bolt_shear_margin(applied_shear_lbf=1000.0, allowable_shear_lbf=1000.0)

    assert margin == pytest.approx(0.0)


def test_bolt_shear_margin_is_negative_when_applied_exceeds_allowable():
    margin = bolt_shear_margin(applied_shear_lbf=1250.0, allowable_shear_lbf=1000.0)

    assert margin == pytest.approx(-0.2)


def test_bolt_shear_margin_rejects_non_positive_loads():
    with pytest.raises(ValueError):
        bolt_shear_margin(applied_shear_lbf=0.0, allowable_shear_lbf=1000.0)

    with pytest.raises(ValueError):
        bolt_shear_margin(applied_shear_lbf=1000.0, allowable_shear_lbf=0.0)


def test_calculate_shear_endpoint_returns_margin_and_pass_status():
    client = TestClient(app)

    response = client.post(
        "/calculate/shear",
        json={
            "applied_shear_lbf": 1000.0,
            "allowable_shear_lbf": 1500.0,
        },
    )

    assert response.status_code == 200
    assert response.json() == {"margin": 0.5, "passes": True}
