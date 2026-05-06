<p align="center">
  <img src="frontend/src/assets/images/logo-placeholder.svg" alt="游戏代练平台" width="80" height="80" onerror="this.style.display='none'" />
</p>

<h1 align="center">游戏代练平台</h1>

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

## 项目简介

Game Boosting Platform 是一个面向游戏服务场景的全栈 Web 应用，涵盖从用户注册、AI 智能下单、代练接单、实时聊天到支付模拟和双向评价的完整业务闭环。

前端采用赛博朋克视觉风格，后端基于 FastAPI 异步架构，支持 Docker 一键部署。

### 核心亮点

- **AI 需求解析** — 用户输入自然语言描述，DeepSeek API 自动提取游戏、段位、价格等结构化字段
- **实时通信** — WebSocket 双向聊天，支持文本/图片消息、输入指示、已读回执
- **完整订单生命周期** — 发布 → 接单 → 完成 → 支付 → 评价，含争议处理与管理员介入
- **59 款游戏目录** — 每款游戏独立配色、服务模板和筛选维度
- **一键 Docker 部署** — `docker compose up -d --build` 即可启动全部服务

---

## 技术栈

| 分层 | 选型 |
|------|------|
| **后端** | Python 3.10 &middot; FastAPI &middot; SQLAlchemy 2.0（异步）&middot; Alembic &middot; Pydantic v2 |
| **前端** | Vue 3 &middot; Vite 5 &middot; Pinia &middot; Vue Router &middot; Tailwind CSS &middot; Axios |
| **数据库** | MySQL 8.0（aiomysql 异步驱动） |
| **实时通道** | WebSocket（FastAPI 原生支持） |
| **AI 能力** | DeepSeek API（兼容 OpenAI SDK） |
| **运维部署** | Docker Compose &middot; Nginx 反向代理 &middot; 多阶段镜像构建 |
| **测试** | pytest &middot; pytest-asyncio &middot; httpx &middot; 18+ 测试用例 |
| **代码规范** | Ruff（lint + format）&middot; mypy |

---

## 功能特性

<table>
<tr>
<td width="50%">

**用户系统**
- 三角色模型：用户 / 代练 / 管理员
- JWT 双 token 认证（access + refresh）
- 代练申请 → 管理员审核 → 额度分配

**订单系统**
- 状态机：PENDING → LOCKED → COMPLETED
- 支付模拟（UNPAID → PAID → REFUNDED）
- AI 自然语言需求解析
- 管理员争议介入与解决

**评价系统**
- 双向评价：用户 ↔ 代练
- 1-5 星评分 + 文字评价
- 可编辑已提交的评价

</td>
<td width="50%">

**服务卡市场**
- 代练发布服务卡片（定价/描述/标签）
- 用户按游戏、类型、价格筛选
- 从卡片一键下单

**实时聊天**
- REST + WebSocket 双通道
- 文本 & 图片消息
- 输入状态指示、已读回执、未读计数
- 订单关联会话、管理员介入

**管理后台**
- 代练申请审核
- 订单干预（取消/争议/完结/退款）
- 游戏目录上下架

</td>
</tr>
</table>

---

## 系统架构

```
                 ┌──────────────┐
                 │   Nginx :80  │  ← 静态文件 + 反向代理
                 └──────┬───────┘
                        │
          ┌─────────────┴─────────────┐
          │                           │
  ┌───────▼───────┐          ┌────────▼────────┐
  │  Vue 3 SPA    │          │  FastAPI :8000   │
  │  Vite + Pinia │          │  异步 + WS       │
  └───────────────┘          └────────┬─────────┘
                                      │
                          ┌───────────┴───────────┐
                          │                       │
                  ┌───────▼───────┐      ┌────────▼────────┐
                  │  MySQL 8.0    │      │  DeepSeek API   │
                  │  aiomysql     │      │  （AI 解析）     │
                  └───────────────┘      └─────────────────┘
```

---

## 快速开始

### 环境要求

- [Docker](https://docs.docker.com/get-docker/) 与 Docker Compose v2
- （可选）[Make](https://www.gnu.org/software/make/) — 用于执行快捷命令

### 1. 克隆与配置

```bash
git clone https://github.com/Mikeaaaa14/game-boosing-platform.git
cd game-boosting-platform
cp .env.local .env
# 编辑 .env 填入 DEEPSEEK_API_KEY 等配置
```

### 2. 启动服务

```bash
# 一键启动（构建镜像 + 启动容器）
docker compose up -d --build

# 等待 MySQL 就绪后执行数据库迁移
docker compose exec backend alembic upgrade head
```

> 首次启动时 MySQL 初始化约需 30 秒，后端 health check 会自动等待。

### 3. 验证运行

```bash
# 查看容器状态
docker compose ps

# 健康检查
curl http://localhost:8000/health
```

### 访问地址

| 服务 | 地址 |
|------|------|
| 前端页面 | http://localhost |
| 后端 API | http://localhost:8000 |
| Swagger 文档 | http://localhost:8000/api/v1/docs |
| MySQL | `localhost:3306` |

### 开发模式

```bash
# 启动带热重载的开发环境
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build
```

开发模式下前端运行在 `http://localhost:3000`（Vite HMR），后端自动重载。

### 停止与清理

```bash
docker compose down          # 停止容器
docker compose down -v       # 停止并清除数据卷
```

---

## 运行测试

```bash
# 安装测试依赖并运行
docker compose exec backend pip install -r requirements-dev.txt
docker compose exec backend pytest tests/ -v
```

测试覆盖范围：认证流程、订单生命周期、支付模拟、评价系统、健康检查（18+ 用例）。

---

## 项目结构

```
game-boosting-platform/
├── backend/
│   ├── app/
│   │   ├── api/endpoints/      # 9 个路由模块（auth、orders、reviews、chat 等）
│   │   ├── core/               # 配置、数据库会话、安全工具
│   │   ├── models/             # SQLAlchemy ORM 模型
│   │   ├── schemas/            # Pydantic v2 请求/响应模型
│   │   └── services/           # 业务逻辑层
│   ├── alembic/versions/       # 7 份数据库迁移脚本
│   ├── tests/                  # pytest 异步测试集
│   ├── Dockerfile              # 多阶段镜像构建
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── views/              # 16 个页面组件
│   │   ├── components/         # 通用 UI 组件
│   │   ├── stores/             # 7 个 Pinia store
│   │   ├── data/               # 游戏图片与静态数据
│   │   ├── utils/              # 辅助函数
│   │   └── assets/             # 样式与图片资源
│   ├── Dockerfile              # 多阶段镜像构建
│   └── nginx.conf              # 反向代理配置
├── docker/                     # MySQL 初始化脚本与配置
├── docker-compose.yml          # 生产环境编排
├── docker-compose.dev.yml      # 开发模式覆盖配置
└── Makefile                    # 快捷命令入口
```

---

## API 接口

| 前缀 | 模块 | 说明 |
|------|------|------|
| `/api/v1/auth` | 认证 | 注册、登录、刷新令牌 |
| `/api/v1/users` | 用户 | 个人资料、修改密码、代练申请 |
| `/api/v1/orders` | 订单 | 增删改查、状态流转、支付、退款 |
| `/api/v1/games` | 游戏 | 目录、分类、搜索 |
| `/api/v1/services` | 服务卡 | 代练服务卡片市场 |
| `/api/v1/chat` | 聊天 | REST 接口 + WebSocket |
| `/api/v1/search` | 搜索 | 跨实体全文搜索 |
| `/api/v1/admin` | 后台 | 用户审核、订单干预 |
| `/api/v1/.../reviews` | 评价 | 双向评价系统 |

> 后端启动后可通过 `/api/v1/docs` 访问交互式 API 文档（Swagger UI）。

---

## 数据库迁移

| 版本 | 说明 |
|------|------|
| 001 | 用户与订单表 |
| 002 | 代练申请与管理员字段 |
| 003 | 聊天会话与消息 |
| 004 | 游戏目录（59 款游戏种子数据） |
| 005 | 订单扩展字段 |
| 006 | 代练服务卡 |
| 007 | 支付状态与评价 |

```bash
docker compose exec backend alembic upgrade head    # 升级到最新版本
docker compose exec backend alembic downgrade -1     # 回退一个版本
```

---

## Makefile 命令

```bash
make help           # 查看所有命令
make up             # 启动生产环境
make dev            # 启动开发环境（带 HMR）
make down           # 停止所有服务
make logs           # 实时查看所有日志
make logs-backend   # 实时查看后端日志
make migrate        # 执行数据库迁移
make status         # 查看容器状态
make health         # 健康检查
make shell          # 进入后端容器
make mysql          # 进入 MySQL 命令行
```

---

## 前端路由

| 路径 | 页面 | 权限 |
|------|------|------|
| `/` | 首页 | 公开 |
| `/login` | 登录 | 未登录 |
| `/register` | 注册 | 未登录 |
| `/games` | 游戏列表 | 公开 |
| `/games/:id` | 游戏详情 | 公开 |
| `/services` | 服务市场 | 公开 |
| `/services/:id` | 服务详情 | 公开 |
| `/search` | 搜索结果 | 公开 |
| `/orders` | 订单列表 | 需登录 |
| `/orders/create` | 创建订单 | 需登录 |
| `/orders/:id` | 订单详情 | 需登录 |
| `/chat` | 会话列表 | 需登录 |
| `/chat/:id` | 聊天室 | 需登录 |
| `/profile` | 个人中心 | 需登录 |
| `/admin` | 管理后台 | 管理员 |

---

## 代码规范

```bash
cd backend
ruff check app/         # 静态检查
ruff check --fix app/   # 自动修复
ruff format app/        # 格式化
```

Ruff 配置位于 [`backend/pyproject.toml`](backend/pyproject.toml)，启用规则集：E/W/F/I/N/UP/B/SIM/T20/RUF，行宽 120。

---

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `MYSQL_ROOT_PASSWORD` | MySQL 管理员密码 | `rootpassword` |
| `MYSQL_DATABASE` | 数据库名 | `game_boosting` |
| `MYSQL_USER` | 数据库用户名 | `boosting_user` |
| `MYSQL_PASSWORD` | 数据库密码 | `boosting_password` |
| `DEEPSEEK_API_KEY` | DeepSeek AI 密钥 | — |
| `SECRET_KEY` | JWT 签名密钥 | — |
| `BACKEND_CORS_ORIGINS` | 允许的跨域来源 | `http://localhost,...` |

完整模板见 [`.env.local`](.env.local)。

---

## 开源协议

[MIT](LICENSE)
