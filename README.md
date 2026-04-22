# Gold Monitor - 实时黄金价格监控

一个实时黄金价格监控 Web 应用，支持价格可视化、K 线图表和价格预警功能。

## 技术栈

**前端：** Vue 3 + Pinia + Vue Router + ECharts + Vite

**后端：** FastAPI + SQLAlchemy + APScheduler + WebSocket

**数据库：** SQLite

## 功能特性

- **实时价格监控** — 定时从外部 API 获取黄金价格（默认每 5 分钟），支持 API Ninjas、GoldAPI、FreeGoldAPI 三个数据源自动降级
- **双币种显示** — 同时展示 USD/盎司 和 CNY/克 价格
- **K 线图表** — 支持 5 分钟、15 分钟、1 小时、4 小时、日线等多个周期，包含 MA5 均线
- **趋势图表** — 收盘价走势面积图
- **价格预警** — 自定义价格上穿/下穿阈值，触发后通过 WebSocket 推送、浏览器通知和页面 Toast 提醒
- **实时推送** — 基于 WebSocket 的实时价格更新和预警推送
- **深色主题** — 金融风格深色 UI

## 项目结构

```
gold-monitor/
├── backend/
│   ├── .env                  # 环境变量配置
│   ├── requirements.txt      # Python 依赖
│   ├── run.py                # 启动入口
│   └── app/
│       ├── main.py           # FastAPI 应用
│       ├── config.py         # 配置管理
│       ├── database.py       # 数据库连接
│       ├── models.py         # ORM 模型
│       ├── schemas.py        # Pydantic 模型
│       ├── crud.py           # 数据库操作
│       ├── scheduler.py      # 定时任务
│       ├── websocket_manager.py
│       ├── services/
│       │   ├── gold_price.py # 金价获取服务
│       │   └── alert.py      # 预警检查服务
│       └── routers/
│           ├── prices.py     # 价格相关 API
│           ├── alerts.py     # 预警相关 API
│           └── ws.py         # WebSocket 端点
└── frontend/
    ├── package.json
    ├── vite.config.js
    └── src/
        ├── main.js
        ├── App.vue
        ├── api/index.js       # API 客户端
        ├── router/index.js    # 路由配置
        ├── stores/            # Pinia 状态管理
        ├── composables/       # 组合式函数
        ├── components/        # 通用组件
        ├── views/             # 页面组件
        └── styles/main.css    # 全局样式
```

## 快速开始

### 环境要求

- Python 3.9+
- Node.js 18+

### 启动后端

```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
python run.py
```

后端服务运行在 `http://localhost:8000`，API 文档访问 `http://localhost:8000/docs`。

### 启动前端

```bash
cd frontend
npm install
npm run dev
```

前端开发服务器运行在 `http://localhost:5173`，已配置代理自动转发 API 和 WebSocket 请求到后端。

### 构建前端

```bash
cd frontend
npm run build
```

构建产物输出到 `frontend/dist/` 目录。

## 环境变量

在 `backend/.env` 中配置：

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `API_NINJAS_KEY` | API Ninjas 密钥（可选） | 空 |
| `GOLD_API_KEY` | GoldAPI 密钥（可选） | 空 |
| `FETCH_INTERVAL_SECONDS` | 价格获取间隔（秒） | 300 |
| `DATA_RETENTION_DAYS` | 数据保留天数 | 90 |

> 如果不配置 API 密钥，将自动使用免费的 FreeGoldAPI 作为数据源。

## API 接口

### 价格

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/prices/current` | 获取当前价格及 24h 统计 |
| GET | `/api/prices/history` | 获取历史价格 |
| GET | `/api/prices/kline` | 获取 K 线数据 |
| GET | `/api/prices/stats` | 获取 24h 统计数据 |

### 预警

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/alerts/` | 获取所有预警 |
| POST | `/api/alerts/` | 创建预警 |
| PUT | `/api/alerts/{id}` | 更新预警 |
| DELETE | `/api/alerts/{id}` | 删除预警 |

### WebSocket

| 路径 | 说明 |
|------|------|
| `/ws/prices` | 实时价格推送和预警通知 |
