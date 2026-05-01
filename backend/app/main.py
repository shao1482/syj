from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.models import Patient, TcmScore, LabTest, QualityOfLife, Treatment, Alert, FollowupPlan
from app.routers import patient, tcm, lab, qol, treatment, alert, report, followup

Base.metadata.create_all(bind=engine)

app = FastAPI(title="脾胃消化患者临床数据监测系统", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(patient.router)
app.include_router(tcm.router)
app.include_router(lab.router)
app.include_router(qol.router)
app.include_router(treatment.router)
app.include_router(alert.router)
app.include_router(report.router)
app.include_router(followup.router)