from app.database import engine, SessionLocal, Base
from app.models import Patient, TcmScore, LabTest, QualityOfLife, Treatment, Alert
from datetime import date

Base.metadata.create_all(bind=engine)

db = SessionLocal()

# 示例患者数据
patients_data = [
    Patient(name="张三", gender="男", age=45, phone="13800001111",
            admission_date=date(2024, 3, 1), diagnosis="慢性胃炎",
            tcm_diagnosis="脾胃虚弱证"),
    Patient(name="李四", gender="女", age=52, phone="13900002222",
            admission_date=date(2024, 3, 5), diagnosis="胃溃疡",
            tcm_diagnosis="肝胃不和证"),
    Patient(name="王五", gender="男", age=60, phone="13700003333",
            admission_date=date(2024, 3, 10), diagnosis="功能性消化不良",
            tcm_diagnosis="脾胃湿热证"),
]

for p in patients_data:
    db.add(p)
db.commit()

# 示例中医证候评分
tcm_data = [
    TcmScore(patient_id=1, record_date=date(2024, 3, 2),
             spleen_stomach_weak=12, liver_stomachdisharmony=5,
             spleen_stomach_dampheat=3, stomach_yin_deficiency=2,
             tongue_score=6, pulse_score=5, total_score=33),
    TcmScore(patient_id=1, record_date=date(2024, 3, 15),
             spleen_stomach_weak=8, liver_stomachdisharmony=4,
             spleen_stomach_dampheat=2, stomach_yin_deficiency=2,
             tongue_score=5, pulse_score=4, total_score=25),
    TcmScore(patient_id=2, record_date=date(2024, 3, 6),
             spleen_stomach_weak=4, liver_stomachdisharmony=14,
             spleen_stomach_dampheat=3, stomach_yin_deficiency=3,
             tongue_score=7, pulse_score=6, total_score=37),
]

for t in tcm_data:
    db.add(t)
db.commit()

# 示例实验室检验
lab_data = [
    LabTest(patient_id=1, record_date=date(2024, 3, 3), test_type="blood_routine",
            wbc=6.5, rbc=4.2, hgb=130, plt=220),
    LabTest(patient_id=1, record_date=date(2024, 3, 16), test_type="liver_func",
            alt=55, ast=48, tbil=12, alb=38),
    LabTest(patient_id=2, record_date=date(2024, 3, 7), test_type="blood_routine",
            wbc=3.2, rbc=3.8, hgb=85, plt=180),
    LabTest(patient_id=2, record_date=date(2024, 3, 7), test_type="liver_func",
            alt=25, ast=22, tbil=8, alb=42),
]

for l in lab_data:
    db.add(l)
db.commit()

# 示例生活质量
qol_data = [
    QualityOfLife(patient_id=1, record_date=date(2024, 3, 2),
                  nutrition_score=6, pain_score=3, sleep_score=5,
                  physical_function=7, mental_health=6, social_function=8, total_score=35),
    QualityOfLife(patient_id=2, record_date=date(2024, 3, 6),
                  nutrition_score=5, pain_score=6, sleep_score=4,
                  physical_function=5, mental_health=4, social_function=6, total_score=24),
]

for q in qol_data:
    db.add(q)
db.commit()

# 示例治疗方案
treatment_data = [
    Treatment(patient_id=1, start_date=date(2024, 3, 1),
              formula_name="四君子汤加减", formula_composition="党参15g 白术10g 茯苓15g 甘草6g",
              western_medicine="奥美拉唑", dosage="20mg/日", effect_rating=4.0,
              followup_note="服药后胃胀减轻"),
    Treatment(patient_id=2, start_date=date(2024, 3, 5),
              formula_name="柴胡疏肝散加减", formula_composition="柴胡10g 枳壳10g 白芍15g 甘草6g",
              western_medicine="雷贝拉唑", dosage="10mg/日", effect_rating=3.0),
]

for t in treatment_data:
    db.add(t)
db.commit()

print("数据库初始化完成，已添加示例数据")
db.close()