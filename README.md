# 脾胃消化患者临床数据监测系统

## 项目简介

本系统为脾胃消化科临床医生/护士提供患者数据监测平台，支持：

- **中医证候评分** — 脾胃虚弱、肝胃不和、脾胃湿热、胃阴不足等证候评估
- **实验室检验** — 血常规、肝功能、胃功能指标监测
- **生活质量评估** — 营养状态、疼痛、睡眠质量评分
- **治疗方案追踪** — 中药方剂、西药、随访记录
- **预警提醒** — 异常指标自动预警
- **数据分析报表** — 统计概览与趋势分析

## 技术栈

- 后端：Python FastAPI + SQLAlchemy + SQLite
- 前端：Vue 3 + Vite + Element Plus + ECharts + Pinia

## 快速启动

### 后端

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
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
├── backend/          # FastAPI 后端
│   └── app/          # 应用代码
│       ├── models/   # 数据模型
│       ├── schemas/  # 请求/响应模型
│       ├── routers/  # API 路由
│       └── services/ # 业务逻辑
├── frontend/         # Vue 3 前端
│   └── src/          # 源代码
│       ├── views/    # 页面
│       ├── components/ # 组件
│       ├── stores/   # Pinia 状态
│       └── api/      # API 封装
└── README.md
```