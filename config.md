## 项目启动（固定环境文件）

### 首次启动或代码有改动（需要重建镜像）
```powershell
cd E:\game-boosting-platform
docker-compose --env-file .env.local up -d --build
docker-compose --env-file .env.local ps
```

### 开机后启动（不重建）
```powershell
cd E:\game-boosting-platform
docker-compose --env-file .env.local up -d --no-build
docker-compose --env-file .env.local ps
```

### 停止容器
```powershell
cd E:\game-boosting-platform
docker-compose --env-file .env.local down
```

## 注意事项

1. 不要用 `.env.example` 覆盖 `.env.local`。
2. 日常不要执行 `down -v`，否则会清空数据库卷。
3. 数据库账号以 `.env.local` 为准（当前是 `xuao / xuao20050906`）。
