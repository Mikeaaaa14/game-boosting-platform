# 业务扩展设计规格书

> 日期: 2026-03-31
> 范围: 游戏目录系统、陪玩服务市场、搜索功能、全站视觉精简

---

## 一、概述

本次扩展涵盖四个核心模块：

1. **游戏目录系统** — 数据库驱动，50-60 款中国热门游戏，10 大分类
2. **陪玩服务市场** — 代练发布服务卡片，用户浏览下单
3. **统一搜索** — 全局搜索框，订单+服务双 tab 筛选
4. **全站视觉精简** — 少字多图，简洁高雅，视觉驱动设计

---

## 二、兼容性约束

> **核心原则：未修改的模块在改造后必须正常运行。**

### 2.1 不可破坏的模块

| 模块 | 约束 |
|------|------|
| 认证系统 (auth) | JWT 流程、登录/注册/刷新 token 接口签名不变 |
| 聊天系统 (chat) | WebSocket 连接、消息模型、会话模型完全保留 |
| 管理后台 (admin) | 代练审核、订单干预接口保留，新增游戏管理入口 |
| 用户模型 (User) | 字段只增不删，现有字段含义不变 |
| Docker 部署 | docker-compose.yml 结构保持兼容 |

### 2.2 Order 模型迁移策略

现有 Order 表改动需要数据迁移：

```
变更项:
- 新增 game_id (FK → Game) — 可空，旧订单通过 game_name 文本匹配回填
- 新增 ai_tags (JSON) — 可空，旧订单不受影响
- 新增 service_id (FK → BoosterService, 可空) — 仅陪玩订单关联
- 保留 game_name — 作为冗余字段保留，确保旧数据可读
- 保留 current_rank / target_rank — 标记为 deprecated，旧订单仍可展示
- 保留 description_raw / description_ai — 继续使用

迁移脚本:
1. 创建 Game 表，写入游戏种子数据
2. ALTER Order 表新增字段（均可空）
3. UPDATE 旧订单：根据 game_name LIKE 匹配回填 game_id
4. 新订单要求 game_id 非空
```

### 2.3 API 兼容

- 所有现有 API 端点保留，不改变签名
- 新增端点使用新路径前缀（`/games`, `/services`, `/search`）
- `POST /orders/create` 兼容旧字段，同时支持新字段
- `POST /orders/analyze` AI 分析接口升级为返回 `ai_tags` 格式，同时保留旧字段

---

## 三、游戏目录系统

### 3.1 Game 数据模型

```python
class Game(Base):
    __tablename__ = "games"

    id: int                    # PK
    name: str                  # 游戏中文名，如 "王者荣耀"
    english_name: str | None   # 英文名，如 "Honor of Kings"
    category: GameCategory     # 枚举：MOBA/FPS/RPG/RACING/CARD/SPORTS/STRATEGY/FIGHTING/SURVIVAL/RHYTHM
    platform: GamePlatform     # 枚举：MOBILE/PC/BOTH
    icon_url: str | None       # 游戏图标 URL
    cover_url: str | None      # 封面大图 URL
    color_theme: str | None    # 主题色 hex，如 "#ff6b2b"
    service_template: JSON     # 该游戏可选的服务类型列表
    description: str | None    # 一句话简介（≤50字）
    is_active: bool            # 是否上架
    sort_order: int            # 排序权重
    created_at: datetime
    updated_at: datetime
```

### 3.2 GameCategory 枚举

```python
class GameCategory(str, Enum):
    MOBA = "MOBA"           # 多人在线竞技
    FPS = "FPS"             # 第一人称射击
    RPG = "RPG"             # 角色扮演
    RACING = "RACING"       # 竞速
    CARD = "CARD"           # 卡牌
    SPORTS = "SPORTS"       # 体育/棋牌
    STRATEGY = "STRATEGY"   # 策略/SLG
    FIGHTING = "FIGHTING"   # 格斗/动作
    SURVIVAL = "SURVIVAL"   # 生存
    RHYTHM = "RHYTHM"       # 音乐节奏
```

### 3.3 service_template 结构示例

每款游戏的 `service_template` 定义该游戏可用的服务类型：

```json
// 王者荣耀
{
  "service_types": ["代练上分", "陪玩", "教学"],
  "has_rank_system": true,
  "rank_tiers": ["青铜", "白银", "黄金", "铂金", "钻石", "星耀", "王者"],
  "servers": ["微信区", "QQ区"],
  "roles": ["中单", "打野", "辅助", "射手", "对抗路"]
}

// 原神
{
  "service_types": ["代刷材料", "代打深渊", "代做任务", "陪玩"],
  "has_rank_system": false,
  "custom_fields": ["冒险等级", "世界等级"],
  "servers": ["官服", "B服"]
}

// CS2
{
  "service_types": ["代练上分", "陪玩", "教学"],
  "has_rank_system": true,
  "rank_tiers": ["白银", "黄金新星", "AK", "双AK", "徽章", "老鹰", "大地球", "全球精英"],
  "servers": ["国服(完美)", "国际服"]
}

// Phigros
{
  "service_types": ["代打谱面", "陪玩"],
  "has_rank_system": false,
  "custom_fields": ["RKS等级"]
}
```

### 3.4 游戏种子数据（50-60 款）

以下为各分类游戏列表，基于网络搜索结果整理：

#### MOBA（多人在线竞技）— 6 款
| 游戏 | 平台 | 服务类型 |
|------|------|----------|
| 王者荣耀 | 手游 | 代练上分、陪玩、教学 |
| 英雄联盟 | 端游 | 代练上分、陪玩、教学 |
| 英雄联盟手游 | 手游 | 代练上分、陪玩、教学 |
| DOTA2 | 端游 | 代练上分、陪玩、教学 |
| 曙光英雄 | 手游 | 代练上分、陪玩 |
| 决战！平安京 | 双端 | 代练上分、陪玩 |

#### FPS（射击）— 7 款
| 游戏 | 平台 | 服务类型 |
|------|------|----------|
| 和平精英 | 手游 | 代练上分、陪玩、教学 |
| CS2 | 端游 | 代练上分、陪玩、教学 |
| 穿越火线 | 端游 | 代练上分、陪玩 |
| 穿越火线手游 | 手游 | 代练上分、陪玩 |
| 三角洲行动 | 双端 | 代练上分、陪玩、教学 |
| 无畏契约 (VALORANT) | 端游 | 代练上分、陪玩、教学 |
| 暗区突围 | 手游 | 代练通关、陪玩 |

#### RPG（角色扮演）— 7 款
| 游戏 | 平台 | 服务类型 |
|------|------|----------|
| 原神 | 双端 | 代刷材料、代打深渊、代做任务、陪玩 |
| 崩坏：星穹铁道 | 双端 | 代刷材料、代打关卡、代做任务 |
| 绝区零 | 双端 | 代刷材料、代打关卡、陪玩 |
| 鸣潮 | 双端 | 代刷材料、代打关卡、陪玩 |
| 梦幻西游 | 双端 | 代练等级、代刷副本、跑环、陪玩 |
| 逆水寒 | 双端 | 代练等级、代刷副本、陪玩 |
| 燕云十六声 | 端游 | 代练等级、代做任务、陪玩 |

#### RACING（竞速）— 5 款
| 游戏 | 平台 | 服务类型 |
|------|------|----------|
| QQ飞车手游 | 手游 | 代练上分、陪玩、教学 |
| 跑跑卡丁车手游 | 手游 | 代练上分、陪玩 |
| 极品飞车：集结 | 手游 | 代练上分、陪玩 |
| 巅峰极速 | 手游 | 代练上分、陪玩 |
| 王牌竞速 | 手游 | 代练上分、陪玩 |

#### CARD（卡牌）— 6 款
| 游戏 | 平台 | 服务类型 |
|------|------|----------|
| 金铲铲之战 | 手游 | 代练上分、陪玩、教学 |
| 炉石传说 | 双端 | 代练上分、陪玩 |
| 阴阳师 | 双端 | 代刷副本、代肝活动、陪玩 |
| 三国杀 | 双端 | 代练上分、陪玩 |
| 游戏王：决斗链接 | 手游 | 代练上分、陪玩 |
| 龙息：神寂 | 手游 | 代练上分、代刷副本 |

#### SPORTS（体育/棋牌）— 5 款
| 游戏 | 平台 | 服务类型 |
|------|------|----------|
| FIFA Online 4 | 端游 | 代练上分、陪玩 |
| 实况足球手游 | 手游 | 代练上分、陪玩 |
| NBA2K Online 2 | 端游 | 代练上分、陪玩 |
| 欢乐斗地主 | 双端 | 代练上分、陪玩 |
| 欢乐麻将 | 手游 | 陪玩 |

#### STRATEGY（策略/SLG）— 6 款
| 游戏 | 平台 | 服务类型 |
|------|------|----------|
| 率土之滨 | 手游 | 代练发展、代管账号、陪玩 |
| 三国志战略版 | 手游 | 代练发展、代管账号 |
| 三国志・战棋版 | 手游 | 代打关卡、代练发展 |
| 文明与征服 | 手游 | 代练发展、代管账号 |
| 万国觉醒 | 手游 | 代练发展、代管账号 |
| 重返帝国 | 手游 | 代练发展、代管账号 |

#### FIGHTING（格斗/动作）— 6 款
| 游戏 | 平台 | 服务类型 |
|------|------|----------|
| 地下城与勇士 | 端游 | 代刷副本、代练等级、搬砖 |
| 地下城与勇士：起源 | 手游 | 代刷副本、代练等级 |
| 拳皇命运 | 手游 | 代练上分、代刷副本 |
| 街霸：对决 | 手游 | 代练上分、陪玩 |
| 火影忍者手游 | 手游 | 代练上分、代刷副本、陪玩 |
| 鬼泣：巅峰之战 | 手游 | 代打关卡、代练等级 |

#### SURVIVAL（生存）— 6 款
| 游戏 | 平台 | 服务类型 |
|------|------|----------|
| 蛋仔派对 | 手游 | 陪玩、代练上分 |
| 明日之后 | 双端 | 代练等级、代刷材料、陪玩 |
| 永劫无间 | 双端 | 代练上分、陪玩、教学 |
| 香肠派对 | 手游 | 陪玩、代练上分 |
| 方舟：生存进化 | 双端 | 代练等级、代刷材料 |
| 黎明觉醒 | 手游 | 代练等级、代刷材料 |

#### RHYTHM（音乐节奏）— 5 款
| 游戏 | 平台 | 服务类型 |
|------|------|----------|
| Phigros | 手游 | 代打谱面、陪玩 |
| 节奏大师 | 手游 | 代打关卡、陪玩 |
| 世界计划缤纷舞台 | 手游 | 代打活动、代肝 |
| Arcaea | 手游 | 代打谱面 |
| 喵斯快跑 | 手游 | 代打谱面、陪玩 |

**总计：59 款游戏**

---

## 四、订单系统改造

### 4.1 新的订单创建流程

```
用户选择游戏（从 Game 目录中选）
    ↓
自然语言描述需求（自由文本输入）
    例: "帮我王者荣耀微信区打上王者，现在钻石3，要求连胜"
    ↓
POST /api/v1/orders/analyze（AI 提取标签）
    ↓
AI 返回结构化 ai_tags:
{
  "game_id": 1,
  "server": "微信区",
  "service_type": "代练上分",
  "detail": {
    "current_rank": "钻石3",
    "target_rank": "王者",
    "requirements": ["连胜"]
  }
}
    ↓
用户确认标签 + 设定价格
    ↓
POST /api/v1/orders/create（创建订单）
    ↓
订单进入 PENDING 状态，可通过聊天协商改价
```

### 4.2 Order 模型变更

```python
class Order(Base):
    # === 保留字段（兼容旧数据）===
    id: int
    user_id: int               # FK → User
    booster_id: int | None     # FK → User
    game_name: str             # 保留，旧订单可读
    current_rank: str | None   # deprecated，旧订单保留
    target_rank: str | None    # deprecated，旧订单保留
    price: Decimal
    status: OrderStatus
    description_raw: str | None
    description_ai: str | None
    game_account: str | None
    game_password: str | None  # AES 加密
    priority: int
    notes: str | None
    created_at: datetime
    updated_at: datetime
    locked_at: datetime | None
    completed_at: datetime | None

    # === 新增字段 ===
    game_id: int | None        # FK → Game，新订单必填
    ai_tags: JSON | None       # AI 提取的结构化标签
    service_type: str | None   # 服务类型（来自 Game.service_template）
    server: str | None         # 区服
    service_id: int | None     # FK → BoosterService，陪玩订单关联
```

### 4.3 ai_tags JSON 结构

```json
{
  "server": "微信区",
  "service_type": "代练上分",
  "detail": {
    "current_rank": "钻石3",
    "target_rank": "王者",
    "requirements": ["连胜", "不掉星"]
  }
}
```

AI 分析接口的 prompt 将根据 `Game.service_template` 动态生成，确保提取的标签与该游戏的服务类型匹配。

---

## 五、陪玩服务市场

### 5.1 BoosterService 数据模型

```python
class BoosterService(Base):
    __tablename__ = "booster_services"

    id: int                    # PK
    booster_id: int            # FK → User（必须是 BOOSTER 角色）
    game_id: int               # FK → Game
    title: str                 # 服务标题，如 "王者荣耀50星大神陪玩"
    description: str | None    # 服务详细描述
    service_type: str          # 服务类型（来自 Game.service_template）
    price_per_hour: Decimal    # 每小时价格
    tags: JSON | None          # 自定义标签，如 ["国服百强", "语音开黑"]
    is_available: bool         # 是否上架
    rating: Decimal | None     # 平均评分（未来扩展）
    order_count: int           # 已完成订单数
    created_at: datetime
    updated_at: datetime
```

### 5.2 API 端点

```
POST   /api/v1/services/create          # 代练发布服务（需 BOOSTER 角色）
GET    /api/v1/services/                 # 浏览服务列表（支持筛选）
GET    /api/v1/services/{id}            # 服务详情
PUT    /api/v1/services/{id}            # 更新服务
DELETE /api/v1/services/{id}            # 下架服务
POST   /api/v1/services/{id}/order      # 用户从服务卡片下单
GET    /api/v1/services/my              # 代练查看自己的服务列表
```

### 5.3 用户从服务卡片下单流程

```
用户浏览服务列表 → 点击服务卡片 → 查看详情
    ↓
点击"立即下单" → 填写需求描述 + 确认价格
    ↓
POST /api/v1/services/{id}/order
    ↓
后端自动创建 Order:
  - user_id = 当前用户
  - booster_id = 服务发布者
  - game_id = 服务关联游戏
  - service_id = 当前服务
  - status = LOCKED（已匹配代练）
  - price = service.price_per_hour × 预估时长（或用户自定义）
    ↓
自动创建聊天会话（复用现有聊天系统）
    ↓
双方通过聊天协商细节和最终价格
```

---

## 六、统一搜索系统

### 6.1 API 端点

```
GET /api/v1/search?q=关键词&type=orders|services|all
    &game_id=1
    &category=MOBA
    &platform=MOBILE
    &price_min=10
    &price_max=500
    &service_type=陪玩
    &page=1
    &page_size=20
```

### 6.2 搜索逻辑

```python
# 搜索范围
if type == "orders" or type == "all":
    # 搜索 Order 表
    # WHERE (game_name LIKE %q% OR description_raw LIKE %q% OR ai_tags::text LIKE %q%)
    # AND game_id = ? AND price BETWEEN ? AND ?
    # AND status = PENDING (只展示待接单的订单)

if type == "services" or type == "all":
    # 搜索 BoosterService 表
    # WHERE (title LIKE %q% OR description LIKE %q% OR tags::text LIKE %q%)
    # AND game_id = ? AND price_per_hour BETWEEN ? AND ?
    # AND is_available = true
```

### 6.3 前端搜索交互

- 顶部导航栏集成全局搜索框
- 搜索结果页分两个 tab：「代练订单」|「陪玩服务」
- 左侧/顶部筛选栏：游戏、分类、平台、价格区间、服务类型
- 搜索结果卡片式布局，展示关键信息

---

## 七、全站视觉精简

### 7.1 设计原则

- **少字多图**：用游戏封面和图标代替文字描述
- **简洁高雅**：去掉广告式宣传语，保留关键信息
- **视觉驱动**：大图背景、毛玻璃效果、适度留白
- **信息层级**：一眼看到核心信息，细节按需展开

### 7.2 各页面改造方案

#### 登录页 / 注册页
- 全屏随机游戏封面背景（从 Game 表 cover_url 随机取）
- 居中毛玻璃登录卡片
- 一句 slogan，如："你的游戏，交给专业的人"
- 去掉所有多余文案

#### 首页
- 顶部：全局搜索框 + 简短标语
- 主体：游戏分类网格（10 大分类），每个分类卡片展示分类图标 + 分类名 + 游戏数量
- 点击分类 → 该分类下的游戏列表（封面图 + 游戏名 + 在线订单数）
- 去掉现有的大段游戏介绍文字
- 底部：热门服务推荐（3-4 张陪玩服务卡片）

#### 游戏专区页（新页面）
- 顶部：游戏封面 banner + 游戏名 + 一句话简介
- 两个 tab：「代练订单」|「陪玩服务」
- 订单/服务卡片列表，带筛选

#### 订单列表页
- 精简顶部文案，用图标代替文字说明
- 卡片布局：游戏图标 + 游戏名 + 需求摘要 + 价格 + 状态标签
- 支持按游戏/分类/价格筛选

#### 订单创建页
- 步骤简化：选游戏 → 写需求 → AI 提取 → 确认价格 → 发布
- 游戏选择用网格卡片（图标+名称），不用下拉框
- 去掉冗余表单标签，用 placeholder 引导

#### 订单详情页
- 保留现有时间线和状态展示
- 精简文案，关键信息图标化

#### 个人中心
- 保留现有功能
- 精简文案和标签

#### 管理后台
- 新增「游戏管理」tab：游戏的增删改查、上下架
- 保留现有代练审核和订单管理

---

## 八、前端路由变更

```javascript
// 新增路由
{ path: '/games',           component: GameCategoryView }    // 游戏分类页
{ path: '/games/:id',       component: GameZoneView }        // 游戏专区页
{ path: '/services',        component: ServiceListView }     // 陪玩服务列表
{ path: '/services/:id',    component: ServiceDetailView }   // 服务详情
{ path: '/search',          component: SearchResultView }    // 搜索结果页

// 保留路由（不变）
{ path: '/',                component: HomeView }            // 首页（改造内容）
{ path: '/login',           component: LoginView }           // 登录（改造视觉）
{ path: '/register',        component: RegisterView }        // 注册（改造视觉）
{ path: '/orders',          component: OrderList }           // 订单列表（改造视觉）
{ path: '/orders/create',   component: OrderCreate }         // 创建订单（改造流程）
{ path: '/orders/:id',      component: OrderDetail }         // 订单详情（精简文案）
{ path: '/chat',            component: ChatListView }        // 聊天列表（不变）
{ path: '/chat/:id',        component: ChatDetailView }      // 聊天详情（不变）
{ path: '/profile',         component: ProfileView }         // 个人中心（精简文案）
{ path: '/admin',           component: AdminView }           // 管理后台（新增游戏管理）
```

---

## 九、数据库迁移计划

### 迁移顺序（Alembic）

```
004_create_game_table.py
  - 创建 games 表
  - 写入 59 款游戏种子数据

005_add_order_game_id.py
  - Order 表新增 game_id, ai_tags, service_type, server, service_id 字段（均可空）
  - 根据 game_name 回填 game_id

006_create_booster_service_table.py
  - 创建 booster_services 表
```

---

## 十、Pinia Store 变更

```javascript
// 新增 stores
stores/games.js        // 游戏列表、分类、当前游戏
stores/services.js     // 陪玩服务列表、发布、管理
stores/search.js       // 搜索状态、筛选条件、结果

// 修改 stores
stores/orders.js       // 适配新的订单创建流程（game_id, ai_tags）

// 不变 stores
stores/auth.js         // 认证（不变）
stores/chat.js         // 聊天（不变）
```

---

## 十一、不在范围内

以下功能明确不在本次迭代中：

- 支付/结算系统
- 评分/评价系统（BoosterService.rating 预留字段但不实现）
- 推荐算法
- Elasticsearch 全文搜索（当前数据量用 SQL LIKE 足够）
- 游戏封面图片上传（使用外部 URL）
- 自动化测试
