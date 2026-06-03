def bolt_shear_margin(applied_shear_lbf: float, allowable_shear_lbf: float) -> float:
    # FORMULA CHANGED
    return (allowable_shear_lbf / applied_shear_lbf) - 1.0
