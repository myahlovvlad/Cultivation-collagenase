from datetime import datetime

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
    audit_records = relationship("AuditRecord", back_populates="batch_run")


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


class AuditRecord(Base):
    __tablename__ = "audit_records"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    user = Column(String, nullable=False, default="system")
    session_id = Column(String, nullable=False, default="default")
    batch_id = Column(Integer, ForeignKey("batch_runs.id"), nullable=True)
    action_type = Column(String, nullable=False)
    module = Column(String, nullable=False, default="unknown")
    recommendation = Column(Text, nullable=False, default="")
    evidence_json = Column(Text, nullable=False, default="{}")
    confidence = Column(Float, nullable=True)
    decision = Column(String, nullable=True)
    decision_reason = Column(Text, nullable=True)
    outcome_json = Column(Text, nullable=True)
    record_hash = Column(String, nullable=False)

    batch_run = relationship("BatchRun", back_populates="audit_records")


class CultureFluidState(Base):
    __tablename__ = "culture_fluid_states"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("batch_runs.id"), nullable=True)
    time_h = Column(Float, nullable=False)
    biomass_g_l = Column(Float, nullable=True)
    density_g_ml = Column(Float, nullable=True)
    viscosity_mpa_s = Column(Float, nullable=True)
    conductivity_ms_cm = Column(Float, nullable=True)
    buffer_capacity_mmol_l_pH = Column(Float, nullable=True)
    state_json = Column(Text, nullable=False, default="{}")


class ExpertSystemLog(Base):
    __tablename__ = "expert_system_logs"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("batch_runs.id"), nullable=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    module = Column(String, nullable=False, default="expert_system")
    recommendations_json = Column(Text, nullable=False, default="[]")
    confidence = Column(Float, nullable=True)
    evidence_json = Column(Text, nullable=False, default="{}")


class TranscriptomeDataset(Base):
    __tablename__ = "transcriptome_datasets"

    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(String, nullable=False, unique=True)
    source_label = Column(String, nullable=False, default="uploaded_tpm")
    path = Column(Text, nullable=False)
    gene_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class DfbaRun(Base):
    __tablename__ = "dfba_runs"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("batch_runs.id"), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    status = Column(String, nullable=False, default="optimal")
    degraded_mode = Column(Integer, nullable=False, default=0)
    input_json = Column(Text, nullable=False, default="{}")
    result_json = Column(Text, nullable=False, default="{}")


class DoeDesign(Base):
    __tablename__ = "doe_designs"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    design_type = Column(String, nullable=False, default="latin_hypercube")
    factors_json = Column(Text, nullable=False, default="{}")
    runs_json = Column(Text, nullable=False, default="[]")


class ScalingPrediction(Base):
    __tablename__ = "scaling_predictions"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    source_volume_l = Column(Float, nullable=False)
    target_volume_l = Column(Float, nullable=False)
    source_kla_h = Column(Float, nullable=True)
    target_kla_h = Column(Float, nullable=True)
    recommended_rpm = Column(Float, nullable=True)
    result_json = Column(Text, nullable=False, default="{}")
