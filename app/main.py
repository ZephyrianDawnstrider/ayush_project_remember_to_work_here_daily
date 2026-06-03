"""EngCalc FastAPI application."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from app.database import Calculation, SessionLocal
from app.calculators.fastener import bolt_shear_margin, BOLT_GRADES

app = FastAPI(title="EngCalc", version="0.1.0")

app.mount("/static", StaticFiles(directory="app/static", check_dir=False), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ShearRequest(BaseModel):
    grade: str = Field(..., example="ISO_8.8")
    diameter_mm: float = Field(..., gt=0, example=8.0)
    applied_shear_N: float = Field(..., gt=0, example=10000.0)
    shear_planes: int = Field(1, ge=1, le=2)
    fitting_factor: float = Field(1.0, ge=1.0, le=2.0)


@app.get("/")
def root():
    return {"status": "ok", "version": "0.1.0"}


@app.get("/ui")
def ui():
    return FileResponse("app/static/index.html")


@app.get("/grades")
def list_grades():
    return {"grades": list(BOLT_GRADES.keys())}


@app.post("/calculate/shear")
def calculate_shear(req: ShearRequest):
    try:
        result = bolt_shear_margin(
            grade=req.grade,
            diameter_mm=req.diameter_mm,
            applied_shear_N=req.applied_shear_N,
            shear_planes=req.shear_planes,
            fitting_factor=req.fitting_factor,
        )
        session = SessionLocal()
        try:
            session.add(
                Calculation(
                    calc_type="bolt_shear",
                    grade=req.grade,
                    diameter_mm=req.diameter_mm,
                    applied_N=req.applied_shear_N,
                    shear_planes=req.shear_planes,
                    margin=result.margin_of_safety,
                    status=result.status,
                )
            )
            session.commit()
        finally:
            session.close()
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
