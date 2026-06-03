"""Tests for fastener.py — verified against NASA-TM-2012-217454 §3.1."""
import pytest
from app.calculators.fastener import bolt_shear_margin, BOLT_GRADES


def test_known_case_m8_iso88_single_shear():
    """
    M8, ISO 8.8, single shear, 10 000 N.
    Manual: fsu=461.6, area=50.265, allow=23202 N, MS=1.3202
    """
    r = bolt_shear_margin("ISO_8.8", 8.0, 10_000, shear_planes=1)
    assert r.status == "PASS"
    assert abs(r.margin_of_safety - 1.3202) < 0.01
    assert r.standard_ref == "NASA-TM-2012-217454 §3.1"


def test_fail_case_overloaded_bolt():
    r = bolt_shear_margin("ISO_8.8", 6.0, 25_000, shear_planes=1)
    assert r.status == "FAIL"
    assert r.margin_of_safety < 0.0


def test_double_shear_doubles_allowable():
    single = bolt_shear_margin("ISO_8.8", 10.0, 5_000, shear_planes=1)
    double = bolt_shear_margin("ISO_8.8", 10.0, 5_000, shear_planes=2)
    assert abs(double.shear_allowable_N - single.shear_allowable_N * 2) < 1.0


def test_marginal_band():
    r = bolt_shear_margin("ISO_8.8", 8.0, 21_500, shear_planes=1)
    assert r.status == "MARGINAL"
    assert 0.0 <= r.margin_of_safety < 0.2


def test_invalid_grade_raises():
    with pytest.raises(ValueError, match="Unknown grade"):
        bolt_shear_margin("FAKE_GRADE", 8.0, 1_000)


def test_zero_diameter_raises():
    with pytest.raises(ValueError):
        bolt_shear_margin("ISO_8.8", 0.0, 1_000)


def test_zero_load_raises():
    with pytest.raises(ValueError):
        bolt_shear_margin("ISO_8.8", 8.0, 0.0)


def test_fitting_factor_reduces_margin():
    r1 = bolt_shear_margin("ISO_8.8", 8.0, 10_000, fitting_factor=1.0)
    r2 = bolt_shear_margin("ISO_8.8", 8.0, 10_000, fitting_factor=1.15)
    assert r2.margin_of_safety < r1.margin_of_safety


def test_all_grades_present():
    assert set(BOLT_GRADES.keys()) == {"ISO_8.8","ISO_10.9","ISO_12.9","NAS_3","A2_70"}