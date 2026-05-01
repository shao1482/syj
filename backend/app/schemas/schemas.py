from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


# Patient schemas
class PatientCreate(BaseModel):
    name: str
    gender: str
    age: int
    phone: Optional[str] = None
    admission_date: date
    diagnosis: Optional[str] = None
    tcm_diagnosis: Optional[str] = None
    notes: Optional[str] = None
    allergy_history: Optional[str] = None
    past_history: Optional[str] = None
    family_history: Optional[str] = None
    admission_assessment: Optional[str] = None
    discharge_summary: Optional[str] = None


class PatientUpdate(BaseModel):
    name: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    phone: Optional[str] = None
    admission_date: Optional[date] = None
    diagnosis: Optional[str] = None
    tcm_diagnosis: Optional[str] = None
    notes: Optional[str] = None
    allergy_history: Optional[str] = None
    past_history: Optional[str] = None
    family_history: Optional[str] = None
    admission_assessment: Optional[str] = None
    discharge_summary: Optional[str] = None


class PatientOut(BaseModel):
    id: int
    name: str
    gender: str
    age: int
    phone: Optional[str]
    admission_date: date
    diagnosis: Optional[str]
    tcm_diagnosis: Optional[str]
    notes: Optional[str]
    allergy_history: Optional[str]
    past_history: Optional[str]
    family_history: Optional[str]
    admission_assessment: Optional[str]
    discharge_summary: Optional[str]

    model_config = {"from_attributes": True}


# TcmScore schemas
class TcmScoreCreate(BaseModel):
    record_date: date
    spleen_stomach_weak: Optional[float] = 0
    liver_stomachdisharmony: Optional[float] = 0
    spleen_stomach_dampheat: Optional[float] = 0
    stomach_yin_deficiency: Optional[float] = 0
    tongue_score: Optional[float] = 0
    pulse_score: Optional[float] = 0
    total_score: Optional[float] = 0


class TcmScoreOut(BaseModel):
    id: int
    patient_id: int
    record_date: date
    spleen_stomach_weak: float
    liver_stomachdisharmony: float
    spleen_stomach_dampheat: float
    stomach_yin_deficiency: float
    tongue_score: float
    pulse_score: float
    total_score: float

    model_config = {"from_attributes": True}


# LabTest schemas
class LabTestCreate(BaseModel):
    record_date: date
    test_type: str
    wbc: Optional[float] = None
    rbc: Optional[float] = None
    hgb: Optional[float] = None
    plt: Optional[float] = None
    alt: Optional[float] = None
    ast: Optional[float] = None
    tbil: Optional[float] = None
    alb: Optional[float] = None
    gastrin: Optional[float] = None
    pepsinogen_i: Optional[float] = None
    pepsinogen_ii: Optional[float] = None
    other_name: Optional[str] = None
    other_value: Optional[float] = None


class LabTestOut(BaseModel):
    id: int
    patient_id: int
    record_date: date
    test_type: str
    wbc: Optional[float]
    rbc: Optional[float]
    hgb: Optional[float]
    plt: Optional[float]
    alt: Optional[float]
    ast: Optional[float]
    tbil: Optional[float]
    alb: Optional[float]
    gastrin: Optional[float]
    pepsinogen_i: Optional[float]
    pepsinogen_ii: Optional[float]
    other_name: Optional[str]
    other_value: Optional[float]

    model_config = {"from_attributes": True}


# QualityOfLife schemas
class QolCreate(BaseModel):
    record_date: date
    nutrition_score: Optional[float] = 0
    pain_score: Optional[float] = 0
    sleep_score: Optional[float] = 0
    physical_function: Optional[float] = 0
    mental_health: Optional[float] = 0
    social_function: Optional[float] = 0
    total_score: Optional[float] = 0


class QolOut(BaseModel):
    id: int
    patient_id: int
    record_date: date
    nutrition_score: float
    pain_score: float
    sleep_score: float
    physical_function: float
    mental_health: float
    social_function: float
    total_score: float

    model_config = {"from_attributes": True}


# Treatment schemas
class TreatmentCreate(BaseModel):
    start_date: date
    end_date: Optional[date] = None
    formula_name: Optional[str] = None
    formula_composition: Optional[str] = None
    western_medicine: Optional[str] = None
    dosage: Optional[str] = None
    effect_rating: Optional[float] = None
    followup_note: Optional[str] = None


class TreatmentOut(BaseModel):
    id: int
    patient_id: int
    start_date: date
    end_date: Optional[date]
    formula_name: Optional[str]
    formula_composition: Optional[str]
    western_medicine: Optional[str]
    dosage: Optional[str]
    effect_rating: Optional[float]
    followup_note: Optional[str]

    model_config = {"from_attributes": True}


# Alert schemas
class AlertOut(BaseModel):
    id: int
    patient_id: int
    alert_type: str
    level: str
    message: str
    trigger_value: Optional[float]
    threshold: Optional[float]
    created_at: datetime
    status: str

    model_config = {"from_attributes": True}


class AlertResolve(BaseModel):
    status: str = "resolved"