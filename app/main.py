from fastapi import FastAPI
from pydantic import BaseModel, Field

from app.calculators.fastener import bolt_shear_margin


app = FastAPI(title="EngCalc")


class ShearCalculationRequest(BaseModel):
    applied_shear_lbf: float = Field(gt=0)
    allowable_shear_lbf: float = Field(gt=0)


class ShearCalculationResponse(BaseModel):
    margin: float
    passes: bool


@app.post("/calculate/shear", response_model=ShearCalculationResponse)
def calculate_shear(request: ShearCalculationRequest) -> ShearCalculationResponse:
    margin = bolt_shear_margin(
        applied_shear_lbf=request.applied_shear_lbf,
        allowable_shear_lbf=request.allowable_shear_lbf,
    )
    return ShearCalculationResponse(margin=margin, passes=margin >= 0.0)
