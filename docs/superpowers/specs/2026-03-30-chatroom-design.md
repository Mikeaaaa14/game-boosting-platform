# 聊天系统设计文档

> **For agentic workers:** 本文档是聊天系统的完整技术设计。实现前请通读全文，遵循数据模型和 API 规范。如遇歧义，以本文档为准。

**目标：** 为 Game Boosting Platform 添加一对一私聊功能，支持用户与代练之间的即时通讯，可选关联订单，管理员可按需介入。

**架构模型：** 对话模型（参考闲鱼），一个全局 WebSocket 连接 + REST 写操作。

---

## 1. 核心设计决策

| 决策项 | 结论 |
|--------|------|
| 聊天模型 | 一对一私聊，可选关联订单（非订单绑定房间） |
| 多代练与同一用户聊同一订单 | 各自独立对话（方案A，类闲鱼） |
| 管理员介入 | 按需加入已有对话，变三人聊天，可见完整历史 |
| 消息类型 | TEXT、IMAGE、SYSTEM |
| 消息撤回 | 发送后 2 分钟内可撤回，双方可见撤回提示 |
| 消息删除 | 仅对自己隐藏，对方和管理员仍可见 |
| 已读回执 | 支持，显示"已读"标记 |
| 订单取消后 | 双方仍可继续聊天 |
| 未读角标 | 顶部导航栏全局显示 |
| V1 聊天入口 | 仅通过订单发起（订单详情页"联系发单人"） |
| 代练市场 | 不在本 spec 范围，独立 spec 后续设计 |
| 实时方案 | REST 写 + WebSocket 推，单实例内存连接管理 |

---

## 2. 数据模型

### 2.1 `conversations` — 对话主表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT PK AUTO_INCREMENT | 主键 |
| type | ENUM('PRIVATE', 'ORDER') | 对话类型 |
| order_id | INT FK → orders.id, nullable | 关联订单，ORDER 类型时使用 |
| created_at | DATETIME, server default | 创建时间 |
| updated_at | DATETIME, on update | 更新时间 |
| last_message_at | DATETIME, nullable | 最后消息时间，对话列表排序依据 |
| last_message_preview | VARCHAR(100), nullable | 最后一条消息预览文本 |

**注意：** `order_id` 不设唯一约束，因为同一订单可有多个对话（不同代练分别与用户聊）。

### 2.2 `conversation_participants` — 参与者表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT PK AUTO_INCREMENT | 主键 |
| conversation_id | INT FK → conversations.id | 所属对话 |
| user_id | INT FK → users.id | 参与者 |
| role_snapshot | VARCHAR(20) | 加入时角色快照（USER/BOOSTER/ADMIN） |
| joined_at | DATETIME, server default | 加入时间 |
| last_read_message_id | INT, nullable | 已读到的消息 ID |
| last_read_at | DATETIME, nullable | 最后已读时间 |

约束：UNIQUE(conversation_id, user_id)

### 2.3 `messages` — 消息表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT PK AUTO_INCREMENT | 主键 |
| conversation_id | INT FK → conversations.id | 所属对话 |
| sender_id | INT FK → users.id, nullable | 发送者，SYSTEM 消息为 null |
| message_type | ENUM('TEXT', 'IMAGE', 'SYSTEM') | 消息类型 |
| content | TEXT | 文本内容或图片路径 |
| created_at | DATETIME, server default | 发送时间 |
| recalled_at | DATETIME, nullable | 撤回时间，非空表示已撤回 |
| meta_json | JSON, nullable | 系统消息附加数据 |

### 2.4 `message_deletions` — 消息删除记录（软删除）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT PK AUTO_INCREMENT | 主键 |
| message_id | INT FK → messages.id | 被删除的消息 |
| user_id | INT FK → users.id | 执行删除的用户 |
| deleted_at | DATETIME, server default | 删除时间 |

约束：UNIQUE(message_id, user_id)

### 2.5 索引

- `conversations(order_id)` — 通过订单找对话
- `conversations(last_message_at)` — 对话列表排序
- `conversation_participants(conversation_id, user_id)` — 唯一约束即索引
- `conversation_participants(user_id)` — 查某用户的所有对话
- `messages(conversation_id, created_at)` — 消息时间线
- `messages(conversation_id, id)` — 游标分页
- `message_deletions(message_id, user_id)` — 唯一约束即索引

---

## 3. 后端 API

所有端点前缀：`/api/v1/chat`

### 3.1 REST 端点

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| POST | `/conversations` | 创建或获取对话 | 登录用户 |
| GET | `/conversations` | 当前用户的对话列表 | 登录用户 |
| GET | `/conversations/{id}` | 对话详情 | 对话参与者 |
| GET | `/conversations/{id}/messages` | 消息历史（游标分页） | 对话参与者 |
| POST | `/conversations/{id}/messages` | 发送文本消息 | 对话参与者 |
| POST | `/conversations/{id}/upload` | 发送图片消息 | 对话参与者 |
| POST | `/conversations/{id}/read` | 标记已读 | 对话参与者 |
| POST | `/messages/{id}/recall` | 撤回消息 | 消息发送者 |
| DELETE | `/messages/{id}` | 删除消息（仅自己不可见） | 消息可见者 |
| POST | `/conversations/{id}/invite-admin` | 邀请管理员介入 | 对话参与者（非管理员） |
| GET | `/unread-summary` | 未读汇总 | 登录用户 |

### 3.2 端点详细逻辑

#### `POST /conversations`

```
输入: { target_user_id: int, order_id?: int }
逻辑:
  1. 校验 target_user_id ≠ 当前用户
  2. 校验目标用户存在且活跃
  3. 如果有 order_id:
     - 校验当前用户是 order.user_id 或 order.booster_id
     - 查找当前用户和目标用户关于该订单的已有对话
     - 存在则返回，不存在则创建 type=ORDER 的对话
  4. 如果没有 order_id:
     - 查找两人之间的 PRIVATE 类型对话
     - 存在则返回，不存在则创建
  5. 创建时自动添加双方为参与者
返回: conversation 对象
```

#### `GET /conversations`

```
查询参数: page, page_size (默认 20)
逻辑:
  1. 查当前用户参与的所有对话
  2. 按 last_message_at 降序排列
  3. 附带每个对话的未读数、对方用户信息、关联订单摘要
返回: 分页对话列表
```

#### `GET /conversations/{id}/messages`

```
查询参数: before_id (可选), limit (默认 30)
逻辑:
  1. 校验当前用户是对话参与者
  2. 查询消息，排除当前用户已删除的消息
  3. 已撤回的消息返回 recalled_at 字段，content 不返回
  4. before_id 存在时返回该 ID 之前的消息（向上翻页）
返回: 消息列表
```

#### `POST /conversations/{id}/messages`

```
输入: { content: string }
逻辑:
  1. 校验参与者权限
  2. 校验 content 非空、长度 ≤ 2000
  3. 创建 TEXT 消息
  4. 更新 conversation.last_message_at 和 last_message_preview
  5. 通过 ConnectionManager 推送 new_message 给其他在线参与者
返回: 消息对象
```

#### `POST /conversations/{id}/upload`

```
输入: multipart/form-data, file 字段
逻辑:
  1. 校验参与者权限
  2. 校验文件类型（jpg/png/gif/webp）、大小 ≤ 5MB
  3. 存储到 uploads/chat/ 目录，文件名用 UUID
  4. 创建 IMAGE 消息，content = 图片路径
  5. 更新 conversation.last_message_at，preview = "[图片]"
  6. WS 广播
返回: 消息对象
```

#### `POST /messages/{id}/recall`

```
逻辑:
  1. 校验当前用户是消息发送者
  2. 校验消息发送时间在 2 分钟内
  3. 设置 recalled_at = now()
  4. WS 广播 message_recalled 事件
返回: 成功状态
```

#### `POST /conversations/{id}/invite-admin`

```
逻辑:
  1. 校验当前用户是对话参与者
  2. 校验对话中尚无 ADMIN 参与者
  3. 选取一个活跃管理员加入（V1 取第一个活跃管理员）
  4. 添加为参与者，role_snapshot = ADMIN
  5. 发送 SYSTEM 消息："XX 请求客服介入"
  6. WS 广播 admin_joined 事件
返回: 成功状态 + 管理员信息
```

### 3.3 WebSocket 端点

```
WS /api/v1/chat/ws?token=<jwt_access_token>
```

**连接模型：** 一个用户一个全局连接，覆盖所有对话。

**服务端职责：**
1. 验证 JWT token
2. 注册到 ConnectionManager
3. 维持心跳（客户端 30s ping，服务端 pong，60s 超时断开）
4. 接收并忽略客户端文本帧（V1 不处理上行业务消息）

**下行事件：**

| event | 触发时机 | data |
|-------|----------|------|
| `new_message` | 新消息创建 | conversation_id, message 对象 |
| `message_recalled` | 消息被撤回 | conversation_id, message_id, recalled_by |
| `message_read` | 对方标记已读 | conversation_id, user_id, last_read_message_id |
| `admin_joined` | 管理员加入对话 | conversation_id, admin 信息 |

---

## 4. 后端模块

### 4.1 新增文件

```
backend/app/models/chat.py              — Conversation, ConversationParticipant, Message, MessageDeletion
backend/app/schemas/chat.py             — 请求/响应 Pydantic 模型
backend/app/services/chat_service.py    — 聊天业务逻辑
backend/app/services/connection_manager.py — WebSocket 连接管理
backend/app/api/endpoints/chat.py       — REST + WS 端点
backend/alembic/versions/003_add_chat_tables.py — 数据库迁移
```

### 4.2 修改文件

```
backend/app/api/router.py              — 注册 chat router
backend/app/api/endpoints/orders.py    — 订单状态变更后调用 ChatService 发系统消息
backend/app/api/endpoints/admin.py     — 管理员干预后发系统消息
frontend/nginx.conf                    — 添加 WebSocket 代理
frontend/vite.config.js                — 添加 WS 开发代理
```

### 4.3 ChatService 方法

```python
class ChatService:
    # 对话管理
    create_or_get_conversation(user_id, target_user_id, order_id?) -> Conversation
    get_user_conversations(user_id, page, limit) -> list[Conversation]
    get_conversation_with_access_check(conversation_id, user_id) -> Conversation

    # 消息操作
    list_messages(conversation_id, user_id, before_id?, limit=30) -> list[Message]
    send_message(conversation_id, sender_id, content) -> Message
    send_image_message(conversation_id, sender_id, file) -> Message
    send_system_message(conversation_id, content, meta?) -> Message
    recall_message(message_id, user_id) -> None
    delete_message_for_user(message_id, user_id) -> None

    # 已读与未读
    mark_read(conversation_id, user_id, last_read_message_id) -> None
    get_unread_summary(user_id) -> UnreadSummary

    # 管理员
    invite_admin(conversation_id, requesting_user_id) -> User
```

### 4.4 ConnectionManager

```python
class ConnectionManager:
    connections: dict[int, WebSocket]  # user_id → websocket

    connect(user_id, websocket) -> None
    disconnect(user_id) -> None
    send_to_user(user_id, data: dict) -> None
    send_to_conversation(conversation_id, data: dict, exclude_user_id?) -> None
```

V1 单实例，内存 dict。后续多实例时引入 Redis pub/sub。

### 4.5 与 OrderService 集成

在 API endpoint 层（非 service 内部）集成，避免循环依赖：

```
订单状态变更 → endpoint 调用 OrderService → 成功后 →
  查找该订单关联的所有对话 →
  通过 ChatService.send_system_message() 发送系统消息
```

系统消息映射：
| 订单事件 | 系统消息内容 |
|----------|-------------|
| 订单创建 | "订单已创建" |
| 代练接单 | "代练 XX 已接单" |
| 订单完成 | "订单已完成" |
| 订单取消 | "订单已取消" |
| 发起纠纷 | "XX 发起了纠纷" |
| 管理员干预 | "管理员已介入：{原因}" |

---

## 5. 前端架构

### 5.1 新增 Pinia Store

**`frontend/src/stores/chat.js`**

```
State:
  conversations[]              — 对话列表
  activeConversationId         — 当前打开的对话
  messagesByConversation       — { [convId]: Message[] }
  unreadTotal                  — 全局未读总数
  unreadByConversation         — { [convId]: number }
  socket                       — WebSocket 实例
  socketStatus                 — 'disconnected' | 'connecting' | 'connected'
  loading                      — 加载状态
  hasMore                      — { [convId]: boolean }

Actions:
  fetchConversations()
  fetchMessages(convId, beforeId?)
  sendMessage(convId, content)
  sendImage(convId, file)
  startConversation(targetUserId, orderId?)
  markRead(convId, messageId)
  recallMessage(messageId)
  deleteMessage(messageId)
  inviteAdmin(convId)
  fetchUnreadSummary()
  connectWebSocket()
  disconnectWebSocket()
  handleWsMessage(event)
```

### 5.2 WebSocket 生命周期

```
连接时机: 登录成功 / 页面刷新恢复登录态后（在 App.vue 或 auth store 中触发）
断开时机: 退出登录
重连策略: 断线后指数退避 1s → 2s → 4s → 8s → ... → 最大 30s
心跳: 客户端每 30s 发送 ping
```

### 5.3 新增组件

```
frontend/src/components/chat/
  ├── ChatPanel.vue              — 聊天面板容器
  ├── ChatMessageList.vue        — 消息列表（滚动加载历史、自动滚底）
  ├── ChatMessageBubble.vue      — 单条消息气泡
  ├── ChatComposer.vue           — 输入框 + 发送按钮 + 图片选择
  ├── ChatConversationList.vue   — 对话列表页
  └── ChatUnreadBadge.vue        — 未读角标（导航栏用）
```

### 5.4 新增路由

```
/chat            — 对话列表页
/chat/:id        — 对话详情页
```

路由 meta：`requiresAuth: true`

### 5.5 UI 嵌入点

**导航栏** (App.vue)：
- 新增"消息"导航项 + `ChatUnreadBadge` 角标
- 登录后通过 WS 实时更新，WS 断线时降级轮询 `fetchUnreadSummary()`

**订单详情页** (OrderDetail.vue)：
- 代练查看订单时显示"联系发单人"按钮
- 点击调用 `startConversation(order.user_id, order.id)`，跳转到 `/chat/:id`

**订单列表页** (OrderList.vue)：
- 订单卡片显示未读小角标（如有关联对话且未读 > 0）

### 5.6 消息气泡样式规则

| 消息类型 | 样式 |
|----------|------|
| 自己的 TEXT | 右对齐，主题色气泡 |
| 对方的 TEXT | 左对齐，浅色气泡 |
| 管理员的 TEXT | 左对齐 + 管理员角标 |
| IMAGE | 气泡内渲染缩略图，点击放大 |
| SYSTEM | 居中，灰色小字，无气泡 |
| 已撤回 | 居中灰色文字："XX 撤回了一条消息" |
| 已删除 | 前端过滤不显示 |

**已读回执显示：**
- 一对一：发送者在最后一条对方已读到的消息旁显示"已读"
- 三人（含管理员）：显示"已读"，不细分

**撤回操作：**
- 自己发的消息 2 分钟内，长按/右键显示"撤回"选项

### 5.7 敏感信息提示

聊天输入框上方固定提示：`"请勿在聊天中发送账号密码等敏感信息"`

---

## 6. 代理配置

### 6.1 Nginx (frontend/nginx.conf)

新增 WebSocket 代理：

```nginx
location /api/v1/chat/ws {
    proxy_pass http://backend:8000;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_read_timeout 86400s;
}
```

### 6.2 Vite 开发代理 (frontend/vite.config.js)

新增 WS 代理：

```javascript
'/api/v1/chat/ws': {
    target: proxyTarget,
    ws: true
}
```

---

## 7. 安全约束

### 7.1 认证

- REST：复用现有 JWT Bearer token（deps.py 中的 get_current_active_user）
- WebSocket：`?token=` 查询参数传递 JWT，连接时验证

### 7.2 权限校验（后端必须校验，不信任前端）

- 查看/发送消息：必须是对话参与者
- 创建对话：不能和自己聊天，目标用户必须存在且活跃
- 订单关联对话：当前用户必须是 order.user_id 或 order.booster_id
- 撤回消息：必须是发送者 + 2 分钟内
- 邀请管理员：必须是参与者且对话中尚无 ADMIN
- 图片上传：文件类型白名单 + 大小限制

### 7.3 内容限制

- 文本消息最大 2000 字符
- 拒绝纯空白消息
- 图片最大 5MB，仅允许 jpg/png/gif/webp
- SYSTEM 消息仅服务端可生成

---

## 8. 实现分期

### Phase 1：数据层与核心 API

- [ ] Chat 模型（4 张表：conversations, conversation_participants, messages, message_deletions）
- [ ] Alembic 迁移 003_add_chat_tables
- [ ] Pydantic Schemas（请求/响应）
- [ ] ChatService 核心方法
- [ ] REST 端点（对话 CRUD、消息收发、图片上传、撤回、删除、已读、未读汇总）
- [ ] 订单状态变更时发送系统消息（endpoint 层集成）

### Phase 2：实时通信

- [ ] ConnectionManager（内存连接管理）
- [ ] WebSocket 端点（认证、心跳、下行推送）
- [ ] 新消息广播、撤回广播、已读广播、管理员加入广播
- [ ] Nginx WebSocket 代理配置
- [ ] Vite 开发 WS 代理配置

### Phase 3：前端核心

- [ ] Chat Pinia store（含 WS 连接管理、重连）
- [ ] 聊天组件（Panel、MessageList、Bubble、Composer）
- [ ] 对话列表页 /chat
- [ ] 对话详情页 /chat/:id
- [ ] 订单详情页"联系发单人"按钮
- [ ] 图片选择与展示
- [ ] 撤回操作 UI
- [ ] 已读回执展示

### Phase 4：体验完善

- [ ] 导航栏"消息"入口 + 未读角标
- [ ] 订单列表未读角标
- [ ] 邀请管理员介入 UI
- [ ] WS 断线重连（指数退避）
- [ ] 消息历史滚动加载
- [ ] 空状态提示
- [ ] 敏感信息提示文案

---

## 9. 不在 V1 范围

- 消息编辑
- 输入中提示（typing indicator）
- 消息全文搜索
- Push 通知
- Redis pub/sub 多实例
- 代练市场（独立 spec）
- 文件/视频发送（仅图片）
