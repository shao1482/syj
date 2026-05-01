from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os


# 注册中文字体
FONT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "fonts")
SIMHEI_PATH = os.path.join(FONT_DIR, "simhei.ttf")

if os.path.exists(SIMHEI_PATH):
    pdfmetrics.registerFont(TTFont('SimHei', SIMHEI_PATH))
    CN_FONT = 'SimHei'
else:
    CN_FONT = 'Helvetica'


def create_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='CNTitle', fontName=CN_FONT, fontSize=16, leading=20, alignment=1))
    styles.add(ParagraphStyle(name='CNHeading', fontName=CN_FONT, fontSize=12, leading=16))
    styles.add(ParagraphStyle(name='CNNormal', fontName=CN_FONT, fontSize=9, leading=12))
    return styles


def generate_patient_pdf(patient, tcm_scores, lab_tests, qol_records, treatments, alerts, output_path):
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    styles = create_styles()
    story = []

    # 标题
    story.append(Paragraph(f"患者临床数据报告 — {patient.name}", styles['CNTitle']))
    story.append(Spacer(1, 10))

    # 基本信息
    story.append(Paragraph("一、患者基本信息", styles['CNHeading']))
    info_data = [
        [Paragraph('姓名', styles['CNNormal']), Paragraph(patient.name or '', styles['CNNormal']),
         Paragraph('性别', styles['CNNormal']), Paragraph(patient.gender or '', styles['CNNormal']),
         Paragraph('年龄', styles['CNNormal']), Paragraph(str(patient.age) if patient.age else '', styles['CNNormal'])],
        [Paragraph('入院日期', styles['CNNormal']), Paragraph(str(patient.admission_date) if patient.admission_date else '', styles['CNNormal']),
         Paragraph('西医诊断', styles['CNNormal']), Paragraph(patient.diagnosis or '', styles['CNNormal']),
         Paragraph('中医诊断', styles['CNNormal']), Paragraph(patient.tcm_diagnosis or '', styles['CNNormal'])],
        [Paragraph('过敏史', styles['CNNormal']), Paragraph(patient.allergy_history or '无', styles['CNNormal']),
         Paragraph('既往史', styles['CNNormal']), Paragraph(patient.past_history or '无', styles['CNNormal']),
         Paragraph('家族史', styles['CNNormal']), Paragraph(patient.family_history or '无', styles['CNNormal'])],
    ]
    info_table = Table(info_data, colWidths=[35*mm, 50*mm, 35*mm, 50*mm, 35*mm, 50*mm])
    info_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('BACKGROUND', (2, 0), (2, -1), colors.lightgrey),
        ('BACKGROUND', (4, 0), (4, -1), colors.lightgrey),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 10))

    # 中医证候评分
    if tcm_scores:
        story.append(Paragraph("二、中医证候评分", styles['CNHeading']))
        tcm_header = ['日期', '脾胃虚弱', '肝胃不和', '脾胃湿热', '胃阴不足', '舌象', '脉象', '总分']
        tcm_rows = [tcm_header]
        for s in tcm_scores:
            tcm_rows.append([
                str(s.record_date), str(s.spleen_stomach_weak), str(s.liver_stomachdisharmony),
                str(s.spleen_stomach_dampheat), str(s.stomach_yin_deficiency),
                str(s.tongue_score), str(s.pulse_score), str(s.total_score),
            ])
        tcm_table = Table(tcm_rows, colWidths=[20*mm] + [17*mm]*7)
        tcm_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ]))
        story.append(tcm_table)
        story.append(Spacer(1, 10))

    # 实验室检验
    if lab_tests:
        story.append(Paragraph("三、实验室检验", styles['CNHeading']))
        lab_header = ['日期', '类型', 'WBC', 'HGB', 'ALT', 'AST', 'TBIL', 'ALB']
        lab_rows = [lab_header]
        for t in lab_tests:
            lab_rows.append([
                str(t.record_date), t.test_type,
                str(t.wbc or '-'), str(t.hgb or '-'), str(t.alt or '-'),
                str(t.ast or '-'), str(t.tbil or '-'), str(t.alb or '-'),
            ])
        lab_table = Table(lab_rows, colWidths=[20*mm, 20*mm] + [17*mm]*6)
        lab_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ]))
        story.append(lab_table)
        story.append(Spacer(1, 10))

    # 生活质量
    if qol_records:
        story.append(Paragraph("四、生活质量评估", styles['CNHeading']))
        qol_header = ['日期', '营养', '疼痛', '睡眠', '生理', '心理', '总分']
        qol_rows = [qol_header]
        for q in qol_records:
            qol_rows.append([
                str(q.record_date), str(q.nutrition_score), str(q.pain_score),
                str(q.sleep_score), str(q.physical_function), str(q.mental_health), str(q.total_score),
            ])
        qol_table = Table(qol_rows, colWidths=[20*mm] + [17*mm]*6)
        qol_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ]))
        story.append(qol_table)
        story.append(Spacer(1, 10))

    # 治疗方案
    if treatments:
        story.append(Paragraph("五、治疗方案", styles['CNHeading']))
        tx_header = ['开始日期', '方剂', '西药', '剂量', '疗效', '随访']
        tx_rows = [tx_header]
        for tx in treatments:
            tx_rows.append([
                str(tx.start_date), tx.formula_name or '-', tx.western_medicine or '-',
                tx.dosage or '-', str(tx.effect_rating or '-'), tx.followup_note or '-',
            ])
        tx_table = Table(tx_rows, colWidths=[22*mm, 35*mm, 30*mm, 20*mm, 15*mm, 30*mm])
        tx_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ]))
        story.append(tx_table)
        story.append(Spacer(1, 10))

    # 预警记录
    if alerts:
        story.append(Paragraph("六、预警记录", styles['CNHeading']))
        alert_header = ['类型', '级别', '信息', '状态']
        alert_rows = [alert_header]
        for a in alerts:
            alert_rows.append([a.alert_type, a.level, a.message, a.status])
        alert_table = Table(alert_rows, colWidths=[20*mm, 20*mm, 100*mm, 20*mm])
        alert_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ]))
        story.append(alert_table)

    doc.build(story)
    return output_path