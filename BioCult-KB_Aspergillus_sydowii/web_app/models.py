from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from .db import SessionLocal
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Strain(Base):
    __tablename__ = "strains"

    id = Column(Integer, primary_key=True, index=True)
    species = Column(String, nullable=False)
    collection_number = Column(String, default="")
    origin = Column(String, default="")
    biosafety_level = Column(String, default="")
    reactivation_rule = Column(Text, default="")

    batch_runs = relationship("BatchRun", back_populates="strain")


class Medium(Base):
    __tablename__ = "media"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    purpose = Column(String, default="")
    pH = Column(Float, nullable=True)
    state = Column(String, default="liquid")
    status = Column(String, default="draft")

    components = relationship("MediumComponent", back_populates="medium")
    batch_runs = relationship("BatchRun", back_populates="medium")


class MediumComponent(Base):
    __tablename__ = "medium_components"

    id = Column(Integer, primary_key=True, index=True)
    medium_id = Column(Integer, ForeignKey("media.id"), nullable=False)
    component = Column(String, nullable=False)
    concentration_g_l = Column(Float, nullable=True)
    hydrate_form = Column(String, default="")
    role = Column(String, default="")

    medium = relationship("Medium", back_populates="components")


class Bioreactor(Base):
    __tablename__ = "bioreactors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    working_volume_l = Column(Float, nullable=True)
    model = Column(String, default="")
    description = Column(Text, default="")

    batch_runs = relationship("BatchRun", back_populates="bioreactor")


class BatchRun(Base):
    __tablename__ = "batch_runs"

    id = Column(Integer, primary_key=True, index=True)
    strain_id = Column(Integer, ForeignKey("strains.id"), nullable=False)
    medium_id = Column(Integer, ForeignKey("media.id"), nullable=False)
    bioreactor_id = Column(Integer, ForeignKey("bioreactors.id"), nullable=True)
    working_volume_l = Column(Float, nullable=True)
    inoculum_volume_ml = Column(Float, nullable=True)
    start_datetime = Column(DateTime, nullable=True)

    strain = relationship("Strain", back_populates="batch_runs")
    medium = relationship("Medium", back_populates="batch_runs")
    bioreactor = relationship("Bioreactor", back_populates="batch_runs")
    observations = relationship("Observation", back_populates="batch_run")


class Observation(Base):
    __tablename__ = "observations"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("batch_runs.id"), nullable=True)
    time_h = Column(Float, nullable=False)
    pH = Column(Float, nullable=True)
    pO2_percent = Column(Float, nullable=True)
    temperature_C = Column(Float, nullable=True)
    rpm = Column(Float, nullable=True)
    biomass = Column(Float, nullable=True)
    kla = Column(Float, nullable=True)
    protein = Column(Float, nullable=True)
    sugars = Column(Float, nullable=True)
    amino_nitrogen = Column(Float, nullable=True)

    batch_run = relationship("BatchRun", back_populates="observations")


class Rule(Base):
    __tablename__ = "rules"

    id = Column(Integer, primary_key=True, index=True)
    condition = Column(Text, nullable=False)
    conclusion = Column(Text, nullable=False)
    recommendation = Column(Text, nullable=False)
    confidence = Column(String, default="medium")
