from pydantic import BaseModel, field_validator
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
    patient_no: Optional[str] = None
    inpatient_no: Optional[str] = None
    bed_no: Optional[str] = None
    department: Optional[str] = None
    responsible_doctor: Optional[str] = None
    responsible_nurse: Optional[str] = None
    status: Optional[str] = "在院"
    risk_level: Optional[str] = None

    @field_validator('age')
    @classmethod
    def validate_age(cls, v):
        if v < 0 or v > 150:
            raise ValueError('年龄应在0-150之间')
        return v

    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        valid = ['在院', '出院', '随访中', '结案', '失访']
        if v and v not in valid:
            raise ValueError(f'状态必须为: {", ".join(valid)}')
        return v

    @field_validator('risk_level')
    @classmethod
    def validate_risk_level(cls, v):
        if v and v not in ('low', 'medium', 'high'):
            raise ValueError('风险等级必须为 low/medium/high')
        return v


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
    patient_no: Optional[str] = None
    inpatient_no: Optional[str] = None
    bed_no: Optional[str] = None
    department: Optional[str] = None
    responsible_doctor: Optional[str] = None
    responsible_nurse: Optional[str] = None
    status: Optional[str] = None
    risk_level: Optional[str] = None

    @field_validator('age')
    @classmethod
    def validate_age(cls, v):
        if v is not None and (v < 0 or v > 150):
            raise ValueError('年龄应在0-150之间')
        return v

    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        valid = ['在院', '出院', '随访中', '结案', '失访']
        if v and v not in valid:
            raise ValueError(f'状态必须为: {", ".join(valid)}')
        return v

    @field_validator('risk_level')
    @classmethod
    def validate_risk_level(cls, v):
        if v and v not in ('low', 'medium', 'high'):
            raise ValueError('风险等级必须为 low/medium/high')
        return v


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
    patient_no: Optional[str] = None
    inpatient_no: Optional[str] = None
    bed_no: Optional[str] = None
    department: Optional[str] = None
    responsible_doctor: Optional[str] = None
    responsible_nurse: Optional[str] = None
    status: Optional[str] = "在院"
    risk_level: Optional[str] = None

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

    @field_validator('spleen_stomach_weak', 'liver_stomachdisharmony',
                     'spleen_stomach_dampheat', 'stomach_yin_deficiency')
    @classmethod
    def validate_sympathy_score(cls, v):
        if v is not None and (v < 0 or v > 30):
            raise ValueError('证候评分应在0-30之间')
        return v

    @field_validator('tongue_score', 'pulse_score')
    @classmethod
    def validate_tongue_pulse(cls, v):
        if v is not None and (v < 0 or v > 15):
            raise ValueError('舌象/脉象评分应在0-15之间')
        return v


class TcmScoreUpdate(BaseModel):
    record_date: Optional[date] = None
    spleen_stomach_weak: Optional[float] = None
    liver_stomachdisharmony: Optional[float] = None
    spleen_stomach_dampheat: Optional[float] = None
    stomach_yin_deficiency: Optional[float] = None
    tongue_score: Optional[float] = None
    pulse_score: Optional[float] = None
    total_score: Optional[float] = None


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


class LabTestUpdate(BaseModel):
    record_date: Optional[date] = None
    test_type: Optional[str] = None
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

    @field_validator('nutrition_score', 'pain_score', 'sleep_score',
                     'physical_function', 'mental_health', 'social_function')
    @classmethod
    def validate_qol_score(cls, v):
        if v is not None and (v < 0 or v > 10):
            raise ValueError('生活质量评分应在0-10之间')
        return v


class QolUpdate(BaseModel):
    record_date: Optional[date] = None
    nutrition_score: Optional[float] = None
    pain_score: Optional[float] = None
    sleep_score: Optional[float] = None
    physical_function: Optional[float] = None
    mental_health: Optional[float] = None
    social_function: Optional[float] = None
    total_score: Optional[float] = None


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

    @field_validator('effect_rating')
    @classmethod
    def validate_effect(cls, v):
        if v is not None and (v < 1 or v > 5):
            raise ValueError('疗效评价应在1-5之间')
        return v


class TreatmentUpdate(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    formula_name: Optional[str] = None
    formula_composition: Optional[str] = None
    western_medicine: Optional[str] = None
    dosage: Optional[str] = None
    effect_rating: Optional[float] = None
    followup_note: Optional[str] = None

    @field_validator('effect_rating')
    @classmethod
    def validate_effect(cls, v):
        if v is not None and (v < 1 or v > 5):
            raise ValueError('疗效评价应在1-5之间')
        return v


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