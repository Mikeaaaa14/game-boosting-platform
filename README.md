# 游戏代练平台 (Game Boosting Platform)

基于 `FastAPI + Vue 3 + MySQL + Docker` 的代练平台，支持：
- 用户认证与权限管理
- 订单创建/接单/完单/取消/争议
- AI 需求解析（DeepSeek）
- Docker 一键部署

---

## 已落地优化

1. 注册权限收敛  
- 公开注册强制创建 `USER`，不允许直接注册 `BOOSTER/ADMIN`。

2. 敏感信息加密  
- `game_password` 创建/更新时加密入库（非明文）。

3. 并发接单一致性  
- 接单流程使用数据库行锁（`FOR UPDATE`），避免重复接单。

4. CORS 白名单配置化  
- 使用 `BACKEND_CORS_ORIGINS`，不再硬编码 `*`。

5. 前端 API 基址配置化  
- 使用 `VITE_API_BASE_URL`，移除硬编码 `/api/v1`。

---

## 环境变量

复制：

```bash
cp .env.example .env
```

关键变量（后端）：

```env
DEEPSEEK_API_KEY=your_actual_api_key
SECRET_KEY=your_strong_secret_key
MYSQL_ROOT_PASSWORD=your_root_password
MYSQL_PASSWORD=your_user_password
BACKEND_CORS_ORIGINS=http://localhost,http://127.0.0.1,http://localhost:3000,http://127.0.0.1:3000
```

前端开发变量（`docker-compose.dev.yml` 已内置）：

```env
VITE_API_BASE_URL=/api/v1
VITE_PROXY_TARGET=http://backend:8000
```

说明：
- `VITE_API_BASE_URL`：前端 axios 基址
- `VITE_PROXY_TARGET`：Vite dev server 反向代理目标

---

## 启动方式

### 生产模式

```bash
make up
```

访问：
- Frontend: `http://localhost:80`
- Backend: `http://localhost:8000`
- Swagger: `http://localhost:8000/api/v1/docs`

### 开发模式（热更新）

```bash
make dev
```

访问：
- Frontend (Vite): `http://localhost:3000`
- Backend (Reload): `http://localhost:8000`

---

## API 路由

认证：`/api/v1/auth`
- `POST /register`
- `POST /login`
- `POST /refresh`
- `GET /me`
- `PUT /me`
- `POST /change-password`

订单：`/api/v1/orders`
- `POST /analyze`
- `POST /create`
- `GET /`
- `GET /{id}`
- `PUT /{id}`
- `PUT /{id}/accept`
- `PUT /{id}/complete`
- `PUT /{id}/cancel`
- `PUT /{id}/dispute`
- `DELETE /{id}`

---

## 常用命令

```bash
make help
make up
make down
make logs
make migrate
make dev
make clean
```

---

## 项目结构

```text
game-boosting-platform/
├─ backend/
├─ frontend/
├─ docker/
├─ docker-compose.yml
├─ docker-compose.dev.yml
├─ Makefile
└─ .env.example
```

---

## 注意事项

1. 历史数据里的旧 `game_password` 可能仍是明文；新写入数据已加密。  
2. 生产环境请使用强 `SECRET_KEY`，并收紧 `BACKEND_CORS_ORIGINS`。  
3. 若更换 `SECRET_KEY`，需配套做历史密文迁移策略。  

---

## License

MIT
