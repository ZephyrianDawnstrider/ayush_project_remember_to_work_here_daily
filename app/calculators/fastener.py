"""Fastener calculation functions for EngCalc."""
import math
from dataclasses import dataclass

# Bolt grade data: ultimate tensile strength (MPa) and yield strength (MPa)
# Source: ISO 898-1, NAS 1348
BOLT_GRADES = {
    "ISO_8.8":  {"ftu": 800,  "fty": 640},
    "ISO_10.9": {"ftu": 1040, "fty": 940},
    "ISO_12.9": {"ftu": 1220, "fty": 1100},
    "NAS_3":    {"ftu": 862,  "fty": 724},
    "A2_70":    {"ftu": 700,  "fty": 450},
}


@dataclass
class ShearResult:
    bolt_area_mm2: float
    shear_allowable_N: float
    applied_per_plane_N: float
    margin_of_safety: float
    status: str          # "PASS", "MARGINAL", or "FAIL"
    standard_ref: str


def bolt_shear_margin(
    grade: str,
    diameter_mm: float,
    applied_shear_N: float,
    shear_planes: int = 1,
    fitting_factor: float = 1.0,
) -> ShearResult:
    """
    Bolt shear margin of safety per NASA-TM-2012-217454 Section 3.1.

    MS = (Fsu * A * n) / (V * FF) - 1.0

    Where:
        Fsu  = 0.577 * Ftu  (Von Mises criterion)
        A    = bolt cross-sectional area (full shank)
        n    = number of shear planes
        V    = applied shear force (N)
        FF   = fitting factor (>= 1.0)
    """
    if grade not in BOLT_GRADES:
        raise ValueError(
            f"Unknown grade '{grade}'. Valid: {list(BOLT_GRADES.keys())}"
        )
    if diameter_mm <= 0:
        raise ValueError("diameter_mm must be positive")
    if applied_shear_N <= 0:
        raise ValueError("applied_shear_N must be positive")
    if shear_planes not in (1, 2):
        raise ValueError("shear_planes must be 1 or 2")
    if fitting_factor < 1.0:
        raise ValueError("fitting_factor must be >= 1.0")

    ftu = BOLT_GRADES[grade]["ftu"]

    # Von Mises shear strength — NASA-TM-2012-217454 §3.1 Eq.(3)
    fsu = 0.577 * ftu

    # Full shank cross-sectional area
    area = math.pi * (diameter_mm / 2.0) ** 2

    # Total shear allowable
    allowable = fsu * area * shear_planes

    # Margin of safety — NASA-TM-2012-217454 §3.1 Eq.(5)
    ms = (allowable / (applied_shear_N * fitting_factor)) - 1.0

    if ms >= 0.2:
        status = "PASS"
    elif ms >= 0.0:
        status = "MARGINAL"
    else:
        status = "FAIL"

    return ShearResult(
        bolt_area_mm2=round(area, 2),
        shear_allowable_N=round(allowable, 1),
        applied_per_plane_N=round(applied_shear_N / shear_planes, 1),
        margin_of_safety=round(ms, 4),
        status=status,
        standard_ref="NASA-TM-2012-217454 §3.1",
    )