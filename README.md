<p align="center">
  <img src="frontend/src/assets/images/logo-placeholder.svg" alt="Game Boosting Platform" width="80" height="80" onerror="this.style.display='none'" />
</p>

<h1 align="center">Game Boosting Platform</h1>

<p align="center">
  <strong>全栈游戏代练 / 陪玩 / 教学服务平台</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/FastAPI-0.109-009688?logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/Vue-3.x-4FC08D?logo=vuedotjs&logoColor=white" alt="Vue 3" />
  <img src="https://img.shields.io/badge/MySQL-8.0-4479A1?logo=mysql&logoColor=white" alt="MySQL" />
  <img src="https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white" alt="Docker" />
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/Tailwind_CSS-3.x-06B6D4?logo=tailwindcss&logoColor=white" alt="Tailwind" />
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License" />
</p>

---

## Overview

Game Boosting Platform 是一个面向游戏代练场景的全栈 Web 应用，涵盖从用户注册、AI 智能下单、代练接单、实时聊天到支付模拟和双向评价的完整业务闭环。

前端采用赛博朋克视觉风格，后端基于 FastAPI 异步架构，支持 Docker 一键部署。

### 核心亮点

- **AI 需求解析** — 用户输入自然语言描述，DeepSeek API 自动提取游戏、段位、价格等结构化字段
- **实时通信** — WebSocket 双向聊天，支持文本/图片消息、输入指示、已读回执
- **完整订单生命周期** — 发布 → 接单 → 完成 → 支付 → 评价，含争议处理与管理员介入
- **59 款游戏目录** — 每款游戏独立配色、服务模板和筛选维度
- **一键 Docker 部署** — `docker compose up -d --build` 即可启动全部服务

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.10 &middot; FastAPI &middot; SQLAlchemy 2.0 (async) &middot; Alembic &middot; Pydantic v2 |
| **Frontend** | Vue 3 &middot; Vite 5 &middot; Pinia &middot; Vue Router &middot; Tailwind CSS &middot; Axios |
| **Database** | MySQL 8.0 (aiomysql async driver) |
| **Realtime** | WebSocket (FastAPI native) |
| **AI** | DeepSeek API (OpenAI SDK compatible) |
| **DevOps** | Docker Compose &middot; Nginx reverse proxy &middot; Multi-stage builds |
| **Testing** | pytest &middot; pytest-asyncio &middot; httpx &middot; 18+ test cases |
| **Linting** | Ruff (lint + format) &middot; mypy |

---

## Features

<table>
<tr>
<td width="50%">

**用户系统**
- 三角色模型：用户 / 代练 / 管理员
- JWT 双 token 认证 (access + refresh)
- 代练申请 → 管理员审核 → 额度分配

**订单系统**
- 状态机：PENDING → LOCKED → COMPLETED
- 支付模拟 (UNPAID → PAID → REFUNDED)
- AI 自然语言需求解析
- 管理员争议介入与解决

**评价系统**
- 双向评价：用户 ↔ 代练
- 1-5 星评分 + 文字评价
- 可编辑已提交的评价

</td>
<td width="50%">

**服务卡市场**
- 代练发布服务卡片 (定价/描述/标签)
- 用户按游戏、类型、价格筛选
- 从卡片一键下单

**实时聊天**
- REST + WebSocket 双通道
- 文本 & 图片消息
- 输入状态指示、已读回执、未读计数
- 订单关联会话、管理员介入

**管理后台**
- 代练申请审核
- 订单干预 (取消/争议/完结/退款)
- 游戏目录上下架

</td>
</tr>
</table>

---

## Architecture

```
                 ┌──────────────┐
                 │   Nginx :80  │  ← 静态文件 + 反向代理
                 └──────┬───────┘
                        │
          ┌─────────────┴─────────────┐
          │                           │
  ┌───────▼───────┐          ┌────────▼────────┐
  │  Vue 3 SPA    │          │  FastAPI :8000   │
  │  Vite + Pinia │          │  async + WS      │
  └───────────────┘          └────────┬─────────┘
                                      │
                          ┌───────────┴───────────┐
                          │                       │
                  ┌───────▼───────┐      ┌────────▼────────┐
                  │  MySQL 8.0    │      │  DeepSeek API   │
                  │  aiomysql     │      │  (AI analysis)  │
                  └───────────────┘      └─────────────────┘
```

---

## Quick Start

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) & Docker Compose v2
- (可选) [Make](https://www.gnu.org/software/make/) — 用于快捷命令

### 1. Clone & Configure

```bash
git clone https://github.com/Mikeaaaa14/game-boosting-platform.git
cd game-boosting-platform
cp .env.local .env
# 编辑 .env 填入 DEEPSEEK_API_KEY 等配置
```

### 2. Start Services

```bash
# 一键启动（构建镜像 + 启动容器）
docker compose up -d --build

# 等待 MySQL 就绪后执行数据库迁移
docker compose exec backend alembic upgrade head
```

> 首次启动时 MySQL 初始化约需 30 秒，后端 health check 会自动等待。

### 3. Verify

```bash
# 查看容器状态
docker compose ps

# 健康检查
curl http://localhost:8000/health
```

### Access Points

| Service | URL |
|---------|-----|
| Frontend | http://localhost |
| Backend API | http://localhost:8000 |
| Swagger Docs | http://localhost:8000/api/v1/docs |
| MySQL | `localhost:3306` |

### Development Mode

```bash
# 带热重载的开发环境
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build
```

开发模式下前端运行在 `http://localhost:3000` (Vite HMR)，后端自动重载。

### Stop & Cleanup

```bash
docker compose down          # 停止容器
docker compose down -v       # 停止并清除数据卷
```

---

## Testing

```bash
# 安装测试依赖并运行
docker compose exec backend pip install -r requirements-dev.txt
docker compose exec backend pytest tests/ -v
```

测试覆盖：认证流程、订单生命周期、支付模拟、评价系统、健康检查 (18+ cases)。

---

## Project Structure

```
game-boosting-platform/
├── backend/
│   ├── app/
│   │   ├── api/endpoints/      # 9 route groups (auth, orders, reviews, chat, ...)
│   │   ├── core/               # Config, DB session, security utils
│   │   ├── models/             # SQLAlchemy ORM models
│   │   ├── schemas/            # Pydantic v2 request/response schemas
│   │   └── services/           # Business logic layer
│   ├── alembic/versions/       # 7 database migrations
│   ├── tests/                  # pytest async test suite
│   ├── Dockerfile              # Multi-stage build
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── views/              # 16 page components
│   │   ├── components/         # Reusable UI components
│   │   ├── stores/             # 7 Pinia stores
│   │   ├── data/               # Game images & static data
│   │   ├── utils/              # Helper functions
│   │   └── assets/             # Styles & image assets
│   ├── Dockerfile              # Multi-stage build
│   └── nginx.conf              # Reverse proxy config
├── docker/                     # MySQL init scripts & config
├── docker-compose.yml          # Production orchestration
├── docker-compose.dev.yml      # Dev mode overrides
└── Makefile                    # Shortcut commands
```

---

## API Reference

| Prefix | Module | Description |
|--------|--------|-------------|
| `/api/v1/auth` | Auth | Register, login, refresh token |
| `/api/v1/users` | Users | Profile, password, booster application |
| `/api/v1/orders` | Orders | CRUD, status transitions, pay, refund |
| `/api/v1/games` | Games | Catalog, categories, search |
| `/api/v1/services` | Services | Booster service cards marketplace |
| `/api/v1/chat` | Chat | REST endpoints + WebSocket |
| `/api/v1/search` | Search | Cross-entity full-text search |
| `/api/v1/admin` | Admin | User review, order intervention |
| `/api/v1/.../reviews` | Reviews | Bidirectional review system |

> Interactive API docs available at `/api/v1/docs` (Swagger UI) after starting the backend.

---

## Database Migrations

| Version | Description |
|---------|-------------|
| 001 | Users & orders tables |
| 002 | Booster application & admin fields |
| 003 | Chat conversations & messages |
| 004 | Game catalog (59 games seed data) |
| 005 | Order extended fields |
| 006 | Booster service cards |
| 007 | Payment status & reviews |

```bash
docker compose exec backend alembic upgrade head    # Apply all
docker compose exec backend alembic downgrade -1     # Rollback one
```

---

## Makefile Commands

```bash
make help           # Show all commands
make up             # Start production
make dev            # Start development (with HMR)
make down           # Stop all services
make logs           # Tail all logs
make logs-backend   # Tail backend logs
make migrate        # Run database migrations
make status         # Show container status
make health         # Health check
make shell          # Enter backend container
make mysql          # Enter MySQL CLI
```

---

## Frontend Routes

| Path | Page | Access |
|------|------|--------|
| `/` | Home | Public |
| `/login` | Login | Guest |
| `/register` | Register | Guest |
| `/games` | Game Catalog | Public |
| `/games/:id` | Game Detail | Public |
| `/services` | Service Marketplace | Public |
| `/services/:id` | Service Detail | Public |
| `/search` | Search Results | Public |
| `/orders` | Order List | Auth |
| `/orders/create` | Create Order | Auth |
| `/orders/:id` | Order Detail | Auth |
| `/chat` | Chat List | Auth |
| `/chat/:id` | Chat Room | Auth |
| `/profile` | Profile | Auth |
| `/admin` | Admin Dashboard | Admin |

---

## Code Quality

```bash
cd backend
ruff check app/         # Lint
ruff check --fix app/   # Auto-fix
ruff format app/        # Format
```

Ruff config: [`backend/pyproject.toml`](backend/pyproject.toml) — rules: E/W/F/I/N/UP/B/SIM/T20/RUF, line-length 120.

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MYSQL_ROOT_PASSWORD` | MySQL root password | `rootpassword` |
| `MYSQL_DATABASE` | Database name | `game_boosting` |
| `MYSQL_USER` | Database user | `boosting_user` |
| `MYSQL_PASSWORD` | Database password | `boosting_password` |
| `DEEPSEEK_API_KEY` | DeepSeek API key for AI features | — |
| `SECRET_KEY` | JWT signing key | — |
| `BACKEND_CORS_ORIGINS` | Allowed CORS origins | `http://localhost,...` |

See [`.env.local`](.env.local) for the full template.

---

## License

[MIT](LICENSE)
