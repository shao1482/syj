# 脾胃消化患者临床数据监测系统

## 项目简介

脾胃消化科临床数据监测平台，面向临床医生与护理人员，实现患者数据采集、预警、分析与随访的全流程闭环管理。

### 核心功能

- **患者管理** — 患者信息录入与管理，支持门诊号/住院号/床号/科室/责任医护/风险等级/状态等字段
- **中医证候评分** — 脾胃虚弱、肝胃不和、脾胃湿热、胃阴不足等证候量化评估，自动计算总分与主导证型
- **实验室检验** — 血常规、肝功能、胃功能指标监测，录入时实时标注异常值
- **生活质量评估** — 营养状态、疼痛、睡眠、生理功能、心理健康、社会功能评分
- **治疗方案追踪** — 中药方剂与西药记录、疗效评价、随访记录
- **自动预警** — 检验/证候/生活质量录入时自动触发预警规则（固定阈值+动态阈值+联合规则+证型关联），预警写入预警中心
- **临床时间轴** — 按时间合并入院、证候、检验、生活质量、治疗、预警、随访等全部事件，帮助医生快速了解病情变化
- **随访管理** — 随访计划新增/编辑/完成/删除/取消，全局提醒（今日/即将到期/已逾期）
- **智能分析流水线** — 数据采集→指标解析→风险评估→干预建议，规则引擎+可选本地模型推理，闭环验证一致性
- **数据报表** — 统计概览（高危患者数/随访逾期数/证型分布）、趋势图、疗效评价
- **PDF/Excel** — 患者报告导出（含风险等级/预警摘要/免责声明）、Excel导入导出

### 技术栈

- 后端：Python FastAPI + SQLAlchemy + SQLite + Pydantic
- 前端：Vue 3 + Vite + Element Plus + ECharts + Pinia
- 数据隐私：所有模型调用均为本地（默认模板引擎 + 可选 Ollama），医疗数据不外泄

## 快速启动

### 后端

```bash
cd backend
pip install -r requirements.txt

# 首次运行：数据库迁移（安全补列，不破坏已有数据）
python migrate_patient_fields.py

# 初始化示例数据（可选）
python init_db.py

# 启动服务
uvicorn app.main:app --reload --port 8000
```

访问 http://localhost:8000/docs 查看 API 文档

### 前端

```bash
cd frontend
npm install
npm run dev
```

访问 http://localhost:5173

## 项目结构

```
syj/
├── backend/              # FastAPI 后端
│   ├── clinical.db        # SQLite 数据库
│   ├── alert_config.json  # 预警规则配置（可编辑）
│   ├── migrate_patient_fields.py  # 数据库迁移脚本
│   └── app/
│       ├── models/        # 数据模型（Patient/TcmScore/LabTest/QOL/Treatment/Alert/FollowupPlan）
│       ├── schemas/       # 请求/响应模型（含校验）
│       ├── routers/       # API 路由（REST风格，CRUD完整）
│       ├── services/      # 业务逻辑
│       │   ├── agents/    # 智能分析流水线（Collector/Analyzer/Assessor/Recommender/Pipeline）
│       │   ├── alert_engine.py   # 预警引擎
│       │   ├── alert_config.py   # 预警配置管理
│       │   ├── analysis_engine.py # 分析引擎
│       │   └── pdf_service.py    # PDF生成
│       └── main.py        # 入口
├── frontend/              # Vue 3 前端
│   └ src/
│   │   ├── views/         # 页面（患者列表/详情/Dashboard/预警中心/报表/随访）
│   │   ├── components/    # 组件（表单/趋势图/疗效评价/临床时间轴）
│   │   ├── stores/        # Pinia 状态管理
│   │   ├── api/           # API 封装层
│   │   └ router/          # 路由
│   └ App.vue
│   └ main.js
└── README.md
```

## 主要API一览

| 路径 | 方法 | 说明 |
|------|------|------|
| `/api/patients/` | GET/POST | 患者列表/新增 |
| `/api/patients/{id}` | GET/PUT/DELETE | 患者详情/修改/删除 |
| `/api/patients/{id}/tcm-scores/` | GET/POST | 证候评分列表/新增 |
| `/api/patients/{id}/tcm-scores/{sid}` | PUT/DELETE | 证候修改/删除 |
| `/api/patients/{id}/lab-tests/` | GET/POST | 检验列表/新增（自动触发预警） |
| `/api/patients/{id}/lab-tests/{lid}` | PUT/DELETE | 检验修改/删除 |
| `/api/patients/{id}/qol/` | GET/POST | 生活质量列表/新增（自动触发预警） |
| `/api/patients/{id}/qol/{qid}` | PUT/DELETE | 生活质量修改/删除 |
| `/api/patients/{id}/treatments/` | GET/POST | 治疗方案列表/新增 |
| `/api/patients/{id}/treatments/{tid}` | PUT/DELETE | 治疗修改/删除 |
| `/api/patients/{id}/followups/` | GET/POST | 随访列表/新增 |
| `/api/patients/{id}/followups/{fid}` | PUT/DELETE | 随访修改/删除 |
| `/api/patients/{id}/timeline/` | GET | 临床时间轴 |
| `/api/alerts/list` | GET | 预警列表 |
| `/api/alerts/{id}` | PUT | 处理预警 |
| `/api/alerts/config` | GET/PUT | 预警规则配置 |
| `/api/followups/reminders/` | GET | 全局随访提醒 |
| `/api/reports/overview` | GET | 统计概览 |
| `/api/reports/ai-analysis/{id}` | POST | 智能分析 |
| `/api/reports/agent-analysis/{id}` | POST | 流水线分析 |
| `/api/reports/efficacy/{id}` | GET | 疗效评价 |
| `/api/reports/patient/{id}/pdf` | GET | PDF导出 |

## 免责声明

本系统为辅助参考工具，所有分析建议不构成最终诊断。医疗决策应由执业医师综合判断。