from datetime import datetime
import os

from sqlalchemy import Column, DateTime, Float, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres@localhost:5432/engcalc")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Calculation(Base):
    __tablename__ = "calculations"

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    calc_type = Column(String)
    grade = Column(String)
    diameter_mm = Column(Float)
    applied_N = Column(Float)
    shear_planes = Column(Integer)
    margin = Column(Float)
    status = Column(String)


Base.metadata.create_all(bind=engine)
