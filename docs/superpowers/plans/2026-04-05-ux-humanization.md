# UX 人性化改造 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 通过纯展示层改动（文案 / CSS / 条件渲染），让游戏代练平台从"系统感"转向"服务感"，不破坏任何现有功能或 API 调用。

**Architecture:** 新增 `humanCopy.js` 工具函数集中管理所有人性化文案逻辑；扩展 `order.js` 的状态元数据支持服务类型感知；逐文件修改 HomeView、ServiceListView、OrderCreate、OrderDetail 的模板文案和 CSS 交互。

**Tech Stack:** Vue 3 Composition API, Tailwind CSS, Vite, Vitest（仅用于工具函数单元测试）

**约束：** 只改展示层。不改后端接口、不改 store 核心逻辑、不改路由、不改数据结构。

---

## Task 1: 添加 Vitest 并创建 humanCopy.js 工具函数

**Files:**
- Modify: `frontend/package.json`
- Modify: `frontend/vite.config.js`
- Create: `frontend/src/utils/humanCopy.js`
- Create: `frontend/src/utils/__tests__/humanCopy.test.js`

- [ ] **Step 1: 安装 Vitest**

```bash
cd frontend && npm install --save-dev vitest
```

Expected: `vitest` 出现在 `package.json` devDependencies 中。

- [ ] **Step 2: 在 package.json 中添加 test 脚本**

在 `frontend/package.json` 的 `scripts` 中添加：

```json
"test": "vitest run"
```

最终 scripts 区域：

```json
"scripts": {
  "dev": "vite",
  "build": "vite build",
  "preview": "vite preview",
  "lint": "eslint . --ext .vue,.js,.jsx,.cjs,.mjs --fix",
  "test": "vitest run"
}
```

- [ ] **Step 3: 在 vite.config.js 中加入 test 配置**

完整替换 `frontend/vite.config.js`：

```js
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

const proxyTarget = process.env.VITE_PROXY_TARGET || 'http://localhost:8000'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    port: 3000,
    proxy: {
      '/api/v1/chat/ws': {
        target: proxyTarget,
        changeOrigin: true,
        ws: true
      },
      '/api': {
        target: proxyTarget,
        changeOrigin: true
      },
      '/uploads': {
        target: proxyTarget,
        changeOrigin: true
      }
    }
  },
  test: {
    environment: 'node',
  },
})
```

- [ ] **Step 4: 先写测试（TDD）**

创建 `frontend/src/utils/__tests__/humanCopy.test.js`：

```js
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import {
  getTimeGreeting,
  getServiceTypeLabel,
  getServiceTypeCTA,
  getPublishButtonLabel,
  getOrderStatusCopy,
} from '../humanCopy.js'

describe('getTimeGreeting', () => {
  function mockHour(hour) {
    vi.setSystemTime(new Date(2026, 0, 1, hour, 0, 0))
  }

  beforeEach(() => vi.useFakeTimers())
  afterEach(() => vi.useRealTimers())

  it('早上 6–10 点返回早上问候', () => {
    mockHour(8)
    expect(getTimeGreeting()).toBe('早上好，今天先冲一把？')
  })

  it('下午 11–17 点返回下午问候', () => {
    mockHour(14)
    expect(getTimeGreeting()).toBe('下午了，找个代练上分？')
  })

  it('晚上 18–23 点返回晚上问候', () => {
    mockHour(20)
    expect(getTimeGreeting()).toBe('今晚要上分还是陪玩？')
  })

  it('凌晨 0–5 点返回凌晨问候', () => {
    mockHour(2)
    expect(getTimeGreeting()).toBe('还没睡？来一把放松一下')
  })
})

describe('getServiceTypeLabel', () => {
  it('代练 返回 帮你上号代打', () => {
    expect(getServiceTypeLabel('代练')).toBe('帮你上号代打')
  })

  it('陪玩 返回 组队一起玩', () => {
    expect(getServiceTypeLabel('陪玩')).toBe('组队一起玩')
  })

  it('教学 返回 教学陪玩', () => {
    expect(getServiceTypeLabel('教学')).toBe('教学陪玩')
  })

  it('未知类型原样返回', () => {
    expect(getServiceTypeLabel('其他')).toBe('其他')
  })
})

describe('getServiceTypeCTA', () => {
  it('代练 返回 找代练上分', () => {
    expect(getServiceTypeCTA('代练')).toBe('找代练上分')
  })

  it('陪玩 返回 找陪玩搭子', () => {
    expect(getServiceTypeCTA('陪玩')).toBe('找陪玩搭子')
  })

  it('教学 返回 找教学陪玩', () => {
    expect(getServiceTypeCTA('教学')).toBe('找教学陪玩')
  })

  it('未知类型返回默认 CTA', () => {
    expect(getServiceTypeCTA('未知')).toBe('立即下单')
  })
})

describe('getPublishButtonLabel', () => {
  it('代练 返回 发布代练需求', () => {
    expect(getPublishButtonLabel('代练')).toBe('发布代练需求')
  })

  it('陪玩 返回 发布陪玩需求', () => {
    expect(getPublishButtonLabel('陪玩')).toBe('发布陪玩需求')
  })

  it('教学 返回 发布教学需求', () => {
    expect(getPublishButtonLabel('教学')).toBe('发布教学需求')
  })

  it('空类型返回默认', () => {
    expect(getPublishButtonLabel('')).toBe('发布需求')
  })
})

describe('getOrderStatusCopy', () => {
  it('PENDING + 代练', () => {
    const { label, subtitle } = getOrderStatusCopy('PENDING', '代练')
    expect(label).toBe('等待代练接单')
    expect(subtitle).toBe('需求已发出，代练们正在看')
  })

  it('PENDING + 陪玩', () => {
    const { label } = getOrderStatusCopy('PENDING', '陪玩')
    expect(label).toBe('等待陪玩接单')
  })

  it('LOCKED + 代练', () => {
    const { label, subtitle } = getOrderStatusCopy('LOCKED', '代练')
    expect(label).toBe('代练上号中')
    expect(subtitle).toBe('代练正在使用你的账号上分')
  })

  it('LOCKED + 陪玩', () => {
    const { label, subtitle } = getOrderStatusCopy('LOCKED', '陪玩')
    expect(label).toBe('陪玩进行中')
    expect(subtitle).toBe('陪玩已就位，一起开黑吧')
  })

  it('COMPLETED + 代练', () => {
    const { label } = getOrderStatusCopy('COMPLETED', '代练')
    expect(label).toBe('代练完成了！')
  })

  it('COMPLETED + 陪玩', () => {
    const { label } = getOrderStatusCopy('COMPLETED', '陪玩')
    expect(label).toBe('这局打完了！')
  })

  it('CANCELLED 不区分类型', () => {
    const { label } = getOrderStatusCopy('CANCELLED', '代练')
    expect(label).toBe('订单已取消')
  })
})
```

- [ ] **Step 5: 运行测试，确认全部失败（函数尚未创建）**

```bash
cd frontend && npm test
```

Expected: 多条 FAIL，提示 `humanCopy.js` 不存在。

- [ ] **Step 6: 创建 humanCopy.js 使测试通过**

创建 `frontend/src/utils/humanCopy.js`：

```js
/**
 * 人性化文案工具函数
 * 纯函数，无副作用，可单独测试。
 */

export function getTimeGreeting() {
  const hour = new Date().getHours()
  if (hour >= 6 && hour < 11) return '早上好，今天先冲一把？'
  if (hour >= 11 && hour < 18) return '下午了，找个代练上分？'
  if (hour >= 18) return '今晚要上分还是陪玩？'
  return '还没睡？来一把放松一下'
}

const SERVICE_TYPE_LABELS = {
  '代练': '帮你上号代打',
  '陪玩': '组队一起玩',
  '教学': '教学陪玩',
}

const SERVICE_TYPE_CTA = {
  '代练': '找代练上分',
  '陪玩': '找陪玩搭子',
  '教学': '找教学陪玩',
}

const PUBLISH_BUTTON_LABELS = {
  '代练': '发布代练需求',
  '陪玩': '发布陪玩需求',
  '教学': '发布教学需求',
}

export function getServiceTypeLabel(serviceType) {
  return SERVICE_TYPE_LABELS[serviceType] ?? serviceType
}

export function getServiceTypeCTA(serviceType) {
  return SERVICE_TYPE_CTA[serviceType] ?? '立即下单'
}

export function getPublishButtonLabel(serviceType) {
  return PUBLISH_BUTTON_LABELS[serviceType] ?? '发布需求'
}

export function getOrderStatusCopy(status, serviceType) {
  const isBoost = serviceType === '代练'

  const labels = {
    PENDING: isBoost ? '等待代练接单' : '等待陪玩接单',
    LOCKED: isBoost ? '代练上号中' : '陪玩进行中',
    COMPLETED: isBoost ? '代练完成了！' : '这局打完了！',
    DISPUTED: '订单争议中',
    CANCELLED: '订单已取消',
  }

  const subtitles = {
    PENDING: '需求已发出，代练们正在看',
    LOCKED: isBoost ? '代练正在使用你的账号上分' : '陪玩已就位，一起开黑吧',
    COMPLETED: '记得说说这次体验',
    DISPUTED: '平台正在介入处理',
    CANCELLED: '需要重新找吗？',
  }

  return {
    label: labels[status] ?? status,
    subtitle: subtitles[status] ?? '',
  }
}
```

- [ ] **Step 7: 再次运行测试，确认全部通过**

```bash
cd frontend && npm test
```

Expected: 所有测试 PASS。

- [ ] **Step 8: Commit**

```bash
cd frontend && git add src/utils/humanCopy.js src/utils/__tests__/humanCopy.test.js package.json vite.config.js && git commit -m "feat(frontend): add humanCopy utilities with vitest"
```

---

## Task 2: 扩展 order.js 支持服务类型感知的状态文案

**Files:**
- Modify: `frontend/src/utils/order.js`

- [ ] **Step 1: 在 order.js 末尾添加两个函数**

打开 `frontend/src/utils/order.js`，在文件末尾追加：

```js
/**
 * 返回人性化的状态标签，区分代练和陪玩场景。
 * serviceType: '代练' | '陪玩' | '教学' | 其他
 */
export function getHumanStatusLabel(status, serviceType) {
  const isBoost = serviceType === '代练'
  const map = {
    PENDING: isBoost ? '等待代练接单' : '等待陪玩接单',
    LOCKED: isBoost ? '代练上号中' : '陪玩进行中',
    COMPLETED: isBoost ? '代练完成了！' : '这局打完了！',
    DISPUTED: '订单争议中',
    CANCELLED: '订单已取消',
  }
  return map[status] ?? getOrderStatusLabel(status)
}

/**
 * 返回状态对应的副标题，区分代练和陪玩场景。
 */
export function getHumanStatusSubtitle(status, serviceType) {
  const isBoost = serviceType === '代练'
  const map = {
    PENDING: '需求已发出，代练们正在看',
    LOCKED: isBoost ? '代练正在使用你的账号上分' : '陪玩已就位，一起开黑吧',
    COMPLETED: '记得说说这次体验',
    DISPUTED: '平台正在介入处理',
    CANCELLED: '需要重新找吗？',
  }
  return map[status] ?? ''
}
```

- [ ] **Step 2: 运行测试确认 Task 1 仍然通过**

```bash
cd frontend && npm test
```

Expected: 所有测试 PASS（order.js 修改不影响 humanCopy 测试）。

- [ ] **Step 3: Commit**

```bash
cd frontend && git add src/utils/order.js && git commit -m "feat(frontend): extend order.js with service-type-aware status copy"
```

---

## Task 3: 添加 CSS 动画到 main.css

**Files:**
- Modify: `frontend/src/assets/main.css`

- [ ] **Step 1: 在 main.css 末尾追加动画样式**

在 `frontend/src/assets/main.css` 文件末尾追加以下内容：

```css
/* ── 人性化交互动画 ── */

/* 在线绿点脉冲 */
@keyframes onlinePulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.6; transform: scale(1.35); }
}

.online-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #4ade80;
  animation: onlinePulse 2s ease-in-out infinite;
  flex-shrink: 0;
}

/* PENDING 状态扫光（shimmer） */
@keyframes shimmerSweep {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}

.shimmer-pending {
  background: linear-gradient(
    90deg,
    rgba(255, 255, 255, 0) 0%,
    rgba(255, 255, 255, 0.06) 50%,
    rgba(255, 255, 255, 0) 100%
  );
  background-size: 200% 100%;
  animation: shimmerSweep 2.4s linear infinite;
}

/* 顶部滑入通知条 */
@keyframes slideDown {
  from { transform: translateY(-100%); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

.notice-slide-in {
  animation: slideDown 0.3s ease-out both;
}

/* 确认按钮成功状态过渡 */
.btn-confirm-success {
  transition: background-color 0.3s ease, color 0.3s ease;
  background-color: #22c55e !important;
  color: white !important;
}

/* 游戏卡片切换淡入 */
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

.game-mode-enter {
  animation: fadeInUp 0.25s ease-out both;
}
```

- [ ] **Step 2: 在浏览器中验证 CSS 加载正常**

```bash
cd frontend && npm run dev
```

打开 http://localhost:3000，确认页面无样式错误，控制台无报错。

- [ ] **Step 3: Commit**

```bash
cd frontend && git add src/assets/main.css && git commit -m "feat(frontend): add humanization CSS animations"
```

---

## Task 4: HomeView.vue — 问候语 + 服务模式文案

**Files:**
- Modify: `frontend/src/views/HomeView.vue`

- [ ] **Step 1: 引入 getTimeGreeting 和 getServiceTypeCTA**

在 `frontend/src/views/HomeView.vue` 的 `<script setup>` 顶部 import 区域末尾追加：

```js
import { getTimeGreeting, getServiceTypeCTA } from '@/utils/humanCopy'
```

- [ ] **Step 2: 添加 greeting computed 和 modeCards 更新**

在 `<script setup>` 中，在现有 `const slideshowHero = ref(null)` 之前添加：

```js
const greeting = computed(() => getTimeGreeting())
```

找到现有的 `const copy = { ... }` 对象，将其中以下字段修改：

```js
// 修改前
modeButton: '\u9009\u62e9\u670d\u52a1\u6a21\u5f0f',
boostLabel: '\u4ee3\u7ec3\u4e0a\u5206',
playLabel: '\u966a\u73a9',
coachLabel: '\u6559\u5b66',
openModePrefix: '\u8fdb\u5165',
searchButton: '\u7cbe\u786e\u641c\u7d22',
searchPrefix: '\u5728 ',
searchSuffix: ' \u4e2d\u641c\u7d22\u9700\u6c42\u3001\u6807\u7b7e\u6216\u670d\u52a1',

// 修改后（直接替换对应的 Unicode 为明文，值如下）
modeButton: '我要…',
boostLabel: '帮我上分',
playLabel: '一起玩',
coachLabel: '带我学',
openModePrefix: '去找',
searchButton: '搜一下',
searchPrefix: '在 ',
searchSuffix: ' 里搜游戏或服务',
```

**注意：** copy 对象中其他字段保持不变，只改上面列出的 8 个字段。

- [ ] **Step 3: 在模板中添加问候语**

在 `<template>` 中找到英雄区（`hero-panel` 或 `HomeHeroCanvas` 组件所在区域），找到显示 `copy.fallbackHeroTitle` 或英雄标题的父容器，在其上方添加：

```html
<p class="text-sm font-medium text-primary-200 mb-2 tracking-wide">
  {{ greeting }}
</p>
```

- [ ] **Step 4: 更新服务模式卡片的进入按钮文案**

在模板中找到模式选择区的进入按钮（通常形如 `copy.openModePrefix + modeCard.label` 或类似拼接），确认其渲染逻辑使用了 `copy.openModePrefix`。若已有该引用则跳过；若按钮文案是写死的，改为：

```html
{{ copy.openModePrefix }}{{ activeModeCard?.label || '代练' }}
```

- [ ] **Step 5: 更新搜索框占位文字**

在模板中找到搜索框 input/textarea 元素，将其 `placeholder` 属性改为：

```html
:placeholder="`${copy.searchPrefix}${activeGame?.name || '全部游戏'}${copy.searchSuffix}`"
```

（copy 对象中 searchPrefix 和 searchSuffix 已在 Step 2 更新。）

- [ ] **Step 6: 在有服务的游戏卡片上添加在线绿点**

在模板中找到渲染游戏卡片的 `v-for` 循环（在 carousel/rail 区域），找到显示游戏名称的区域，在名称旁追加：

```html
<span
  v-if="game.service_count > 0"
  class="online-dot ml-2 inline-flex align-middle"
  title="有代练在线"
></span>
```

**注意：** `game.service_count` 是现有字段，只读，无需新增数据。若字段名不同（检查游戏对象结构），换成对应的数量字段 > 0 的条件即可。

- [ ] **Step 7: 验证首页显示正常**

```bash
cd frontend && npm run dev
```

- 打开 http://localhost:3000
- 确认顶部出现时段问候语
- 确认搜索框 placeholder 更新
- 游戏卡片有服务时出现绿点

- [ ] **Step 8: Commit**

```bash
cd frontend && git add src/views/HomeView.vue && git commit -m "feat(frontend): humanize HomeView greeting and mode copy"
```

---

## Task 5: ServiceListView.vue — 筛选栏 + 发布区文案

**Files:**
- Modify: `frontend/src/views/ServiceListView.vue`

- [ ] **Step 1: 引入 getServiceTypeCTA 和 getServiceTypeLabel**

在 `frontend/src/views/ServiceListView.vue` 的 `<script setup>` import 区域末尾追加：

```js
import { getServiceTypeCTA, getServiceTypeLabel } from '@/utils/humanCopy'
```

- [ ] **Step 2: 更新筛选栏 label 文案**

在 `<template>` 中找到筛选区域的三个 `<label>` 元素，修改其文字内容：

```html
<!-- 游戏筛选 label -->
<label class="label" for="service-filter-game">打哪个</label>

<!-- 服务类型筛选 label -->
<label class="label" for="service-filter-type">我想要</label>

<!-- 价格区间（最低价/最高价保持，只改组标题若有的话） -->
<!-- 若有独立标题如"价格区间"，改为"我的预算" -->
```

- [ ] **Step 3: 更新统计卡片文案**

找到 hero section 中的三个 `<article class="stat-card">` 卡片，将描述文字更新：

```html
<!-- 第一个卡片 -->
<p class="mt-2 text-sm text-slate-300">现在可看服务</p>

<!-- 第二个卡片 -->
<p class="mt-2 text-sm text-slate-300">覆盖游戏</p>

<!-- 第三个卡片（isBooster 条件渲染，保持逻辑不变，只改文字） -->
<p class="mt-2 text-sm text-slate-300">{{ isBooster ? '我发布的' : '实时更新' }}</p>
```

- [ ] **Step 4: 更新发布区（代练师视角）的文案**

找到 `v-if="isBooster"` 的发布服务区块，修改标题和说明：

```html
<!-- 修改前 -->
<p class="eyebrow">发布服务</p>
<h2 class="section-title mt-4">把你会打的内容挂出来</h2>
<p class="section-copy mt-3">标题、价格、标签写清楚就够了。</p>

<!-- 修改后：文案已足够好，只微调一处 -->
<p class="eyebrow">发布服务</p>
<h2 class="section-title mt-4">把你会打的内容挂出来</h2>
<p class="section-copy mt-3">写清楚你擅长什么，老板自己会找来。</p>
```

- [ ] **Step 5: 更新服务卡片 CTA 按钮文案（使用 getServiceTypeCTA）**

在模板中找到服务卡片的"查看详情"或"下单"按钮区域（通常在 `v-for` 渲染服务卡片的循环内），将按钮文案改为：

```html
<!-- 原来写死的"查看详情"或"立即下单" -->
<router-link
  :to="{ name: 'service-detail', params: { id: service.id } }"
  class="btn-primary w-full text-center"
>
  {{ getServiceTypeCTA(service.service_type) }}
</router-link>
```

**注意：** `service.service_type` 是现有字段，只读。只改按钮文字，不改路由跳转逻辑。

- [ ] **Step 6: 筛选后结果提示文案（若模板中有结果数量展示）**

若模板中有类似 "共 N 条服务" 的提示，改为：

```html
<p class="text-sm text-slate-400">
  找到 {{ pagination.total }} 位，现在可接单
</p>
```

- [ ] **Step 7: 验证服务列表页**

```bash
cd frontend && npm run dev
```

打开陪玩服务页，确认筛选栏 label 已更新，统计卡片文案已变更，服务卡片 CTA 按钮文案随服务类型变化，功能正常。

- [ ] **Step 8: Commit**

```bash
cd frontend && git add src/views/ServiceListView.vue && git commit -m "feat(frontend): humanize ServiceListView filter labels, copy and CTA buttons"
```

---

## Task 6: OrderCreate.vue — 下单流程文案

**Files:**
- Modify: `frontend/src/views/OrderCreate.vue`

- [ ] **Step 1: 引入 getPublishButtonLabel**

在 `frontend/src/views/OrderCreate.vue` 的 `<script setup>` import 区末尾追加：

```js
import { getPublishButtonLabel } from '@/utils/humanCopy'
```

- [ ] **Step 2: 添加发布按钮文案 computed**

在 `<script setup>` 中，在 `const canPublish = computed(...)` 之后添加：

```js
const publishButtonLabel = computed(() => {
  if (isSubmitting.value) return '正在发布...'
  return getPublishButtonLabel(formData.value.service_type)
})
```

- [ ] **Step 3: 更新 Hero 区标题文案**

在 `<template>` 中找到 Hero 区（`hero-panel`）的标题：

```html
<!-- 修改前 -->
<h1 class="section-title neon-text !text-4xl sm:!text-5xl">
  选游戏，写需求，直接发。
</h1>
<p class="section-copy max-w-3xl">
  四步走完，不绕路。
</p>

<!-- 修改后 -->
<h1 class="section-title neon-text !text-4xl sm:!text-5xl">
  找代练，就这几步。
</h1>
<p class="section-copy max-w-3xl">
  选游戏 → 写需求 → 确认发布，搞定。
</p>
```

- [ ] **Step 4: 更新各步骤内的引导文案**

**Step 1（选游戏区块）：**

```html
<!-- 修改前 -->
<h2 class="mt-2 text-2xl font-semibold text-white">选择你这次要发布需求的游戏</h2>

<!-- 修改后 -->
<h2 class="mt-2 text-2xl font-semibold text-white">打哪个游戏？</h2>
```

```html
<!-- 下一步按钮 修改前 -->
下一步：写需求

<!-- 修改后 -->
选好了，写需求 →
```

**Step 2（写需求区块）：**

```html
<!-- 修改前 -->
<h2 class="mt-2 text-2xl font-semibold text-white">用自然语言写下你的需求</h2>
<p class="mt-3 text-sm leading-7 text-slate-400">建议把区服、目标段位、时段和偏好一起写进去，AI 会帮你整理成结构化标签。</p>

<!-- 修改后 -->
<h2 class="mt-2 text-2xl font-semibold text-white">告诉我们你想打什么</h2>
<p class="mt-3 text-sm leading-7 text-slate-400">区服、目标段位、时间偏好都写上，代练更容易理解你的需求。</p>
```

```html
<!-- 需求描述 label 修改前 -->
<label class="label" for="order-description">需求描述</label>

<!-- 修改后 -->
<label class="label" for="order-description">你的需求</label>
```

```html
<!-- 跳过 AI 按钮 修改前 -->
跳过识别，直接填写

<!-- 修改后 -->
跳过，我自己填
```

```html
<!-- AI 分析按钮 修改前 -->
{{ isAnalyzing ? 'AI 正在拆解需求...' : '下一步：让 AI 提取标签' }}

<!-- 修改后 -->
{{ isAnalyzing ? 'AI 识别中...' : 'AI 帮我整理一下 →' }}
```

**Step 3（AI 结果区块）：**

```html
<!-- 修改前 -->
<h2 class="mt-2 text-2xl font-semibold text-white">AI 已经把你的需求拆成结构化标签</h2>
<p class="mt-3 text-sm leading-7 text-slate-400">这里会保留旧字段展示，同时也给你新的 `ai_tags` 结构，确认后进入价格和发布阶段。</p>

<!-- 修改后 -->
<h2 class="mt-2 text-2xl font-semibold text-white">AI 帮你整理好了</h2>
<p class="mt-3 text-sm leading-7 text-slate-400">看看这些信息对不对，有问题可以返回改，没问题就继续。</p>
```

```html
<!-- 继续按钮 修改前 -->
下一步：确认价格并发布

<!-- 修改后 -->
信息没问题，去确认价格 →
```

**Step 4（确认区块）：**

```html
<!-- 修改前 -->
<h2 class="mt-2 text-2xl font-semibold text-white">确认价格与最终字段</h2>
<p class="mt-3 text-sm leading-7 text-slate-400">AI 结果可以继续微调。你只需要把价格和最后的偏好确认好，就能发布订单。</p>

<!-- 修改后 -->
<h2 class="mt-2 text-2xl font-semibold text-white">最后确认一下</h2>
<p class="mt-3 text-sm leading-7 text-slate-400">确认价格和偏好，发布后代练会直接看到你的需求。</p>
```

```html
<!-- 字段 label 修改（只改 label 文字，input 的 v-model 和 id 不变） -->
<label class="label" for="confirm-current-rank">现在几段</label>
<label class="label" for="confirm-target-rank">想冲到哪</label>
<label class="label" for="confirm-role">位置 / 角色偏好</label>
<label class="label" for="confirm-notes">还有什么想说的</label>
```

```html
<!-- 账号密码区域添加代练说明（仅在 service_type === '代练' 时显示） -->
<p
  v-if="formData.service_type === '代练'"
  class="text-xs text-slate-400 mt-1 col-span-2"
>
  代练会用你填写的账号上号，请确认信息准确。
</p>
```

**注意：** 此处 `v-if` 是纯展示层条件，不影响后端提交逻辑。

- [ ] **Step 5: 更新发布按钮文案**

找到最终发布按钮：

```html
<!-- 修改前 -->
{{ isSubmitting ? '正在发布订单...' : '确认发布订单' }}

<!-- 修改后，使用 computed -->
{{ publishButtonLabel }}
```

- [ ] **Step 6: 更新成功提示**

找到 `successMessage` 的赋值位置（在 `publishOrder` 函数中）：

```js
// 修改前
successMessage.value = '订单已发布，正在跳转到订单大厅。'

// 修改后
successMessage.value = `需求发出去了，等${formData.value.service_type || '代练'}接单。`
```

- [ ] **Step 7: 更新错误提示文案**

找到以下错误赋值，逐一更新：

```js
// nextFromSelect 中
// 修改前
errorMessage.value = '请先选择一个游戏。'
// 修改后
errorMessage.value = '还没选游戏，先选一个吧。'

// analyzeRequirement 中
// 修改前
errorMessage.value = '请先写下你的需求描述。'
// 修改后
errorMessage.value = '需求还没写，简单描述一下你想要什么。'

// publishOrder 中
// 修改前
errorMessage.value = '请至少确认游戏、需求描述和预算金额。'
// 修改后
errorMessage.value = '还差一步 — 游戏、需求描述和预算都填一下。'
```

- [ ] **Step 8: 验证下单流程**

```bash
cd frontend && npm run dev
```

完整走一遍下单流程（选游戏 → 写需求 → AI → 确认），确认：
- 文案已更新
- 代练场景下账号区域有说明文字
- 提交按钮文案随 service_type 变化
- 功能正常（AI 分析、最终提交均可正常调用）

- [ ] **Step 9: Commit**

```bash
cd frontend && git add src/views/OrderCreate.vue && git commit -m "feat(frontend): humanize OrderCreate step copy and submit labels"
```

---

## Task 7: OrderDetail.vue — 状态文案 + 动效

**Files:**
- Modify: `frontend/src/views/OrderDetail.vue`

- [ ] **Step 1: 引入新函数**

在 `frontend/src/views/OrderDetail.vue` 的 import 区，在原有 `order.js` import 行追加两个函数：

```js
import {
  getOrderStatusBadgeClass,
  getOrderStatusLabel,
  getOrderStatusMeta,
  getHumanStatusLabel,
  getHumanStatusSubtitle,
} from '@/utils/order'
```

- [ ] **Step 2: 添加人性化状态 computed**

在 `<script setup>` 中，在 `const statusMeta = computed(...)` 之后添加：

```js
const humanStatusLabel = computed(() =>
  getHumanStatusLabel(order.value?.status, order.value?.service_type)
)

const humanStatusSubtitle = computed(() =>
  getHumanStatusSubtitle(order.value?.status, order.value?.service_type)
)

const isPending = computed(() => order.value?.status === 'PENDING')
const isLocked = computed(() => order.value?.status === 'LOCKED')
const isBoostOrder = computed(() => order.value?.service_type === '代练')
```

- [ ] **Step 3: 更新 Hero 区状态 badge 文字**

在 `<template>` 中找到显示状态 badge 的行：

```html
<!-- 修改前 -->
<span :class="getOrderStatusBadgeClass(order.status)">{{ getOrderStatusLabel(order.status) }}</span>

<!-- 修改后 -->
<span :class="getOrderStatusBadgeClass(order.status)">{{ humanStatusLabel }}</span>
```

- [ ] **Step 4: 在 Hero 区添加状态副标题**

在状态 badge 行下方添加：

```html
<p v-if="humanStatusSubtitle" class="mt-2 text-sm text-slate-400">
  {{ humanStatusSubtitle }}
</p>
```

- [ ] **Step 5: 给 PENDING 状态的时间线区域添加 shimmer**

找到渲染时间线的 `<article>` 元素（包含 `h2` 文字"时间线"的区块），给该 `article` 添加条件 class：

```html
<article
  class="surface-card p-6 sm:p-8"
  :class="{ 'shimmer-pending': isPending }"
>
```

- [ ] **Step 6: 更新时间线节点文案**

找到 `const timeline = computed(...)` 中各节点的 `title` 字段，修改：

```js
const timeline = computed(() => {
  if (!order.value) {
    return []
  }

  return [
    {
      title: '需求已发出',
      time: formatDateTime(order.value.created_at),
      active: true,
    },
    {
      title: isBoostOrder.value ? '代练已接单' : '陪玩已接单',
      time: order.value.locked_at ? formatDateTime(order.value.locked_at) : '等待中…',
      active: ['LOCKED', 'COMPLETED', 'DISPUTED'].includes(order.value.status),
    },
    {
      title: isBoostOrder.value ? '代练完成' : '陪玩结束',
      time: order.value.completed_at ? formatDateTime(order.value.completed_at) : '未完成',
      active: order.value.status === 'COMPLETED',
    },
  ]
})
```

- [ ] **Step 7: 更新聊天按钮文案**

找到联系 / 发起对话按钮。若存在 `canContactOrderOwner` 条件渲染的区域：

```html
<!-- 修改前 -->
联系代练师

<!-- 修改后 -->
{{ isBoostOrder ? '联系代练' : '联系陪玩' }}
```

若存在"问问进度"副文案的位置，改为该文案：

```html
<span class="text-xs text-slate-400">问问进度</span>
```

- [ ] **Step 8: 更新确认完成按钮文案**

找到"确认完成"按钮（通常在操作区域，仅 isOwner && isLocked 时显示）：

```html
<!-- 修改前 -->
确认完成

<!-- 修改后 -->
{{ isBoostOrder ? '确认，代练完成了' : '确认，这局打完了' }}
```

- [ ] **Step 9: 更新评价区文案**

找到评价提交按钮：

```html
<!-- 修改前 -->
提交评价

<!-- 修改后 -->
说说这次体验
```

找到提交后的 `successMessage` 赋值（在 `submitReview` 函数中）：

```js
// 修改前
successMessage.value = isEditing ? '评价已更新' : '评价已提交'

// 修改后
successMessage.value = isEditing ? '评价更新了' : '谢谢，你的反馈会帮助更多人找到靠谱的代练'
```

- [ ] **Step 10: 验证订单详情页**

```bash
cd frontend && npm run dev
```

打开一个 PENDING 状态的订单，确认：
- Badge 文字已人性化
- 副标题显示"需求已发出，代练们正在看"
- 时间线区域有 shimmer 效果
- 打开一个 LOCKED 状态的代练订单，确认副标题显示"代练正在使用你的账号上分"
- 评价按钮文案已更新

- [ ] **Step 11: Commit**

```bash
cd frontend && git add src/views/OrderDetail.vue && git commit -m "feat(frontend): humanize OrderDetail status copy and add shimmer animation"
```

---

## Task 8: 验证整体功能完整性

- [ ] **Step 1: 运行所有单元测试**

```bash
cd frontend && npm test
```

Expected: 所有测试 PASS。

- [ ] **Step 2: 完整功能冒烟测试**

启动前端：

```bash
cd frontend && npm run dev
```

按以下清单逐一验证，每项确认功能可用且文案已更新：

| 页面 | 验证点 |
|------|--------|
| 首页 | 问候语显示正确时段文案 |
| 首页 | 游戏卡片有服务时显示绿点 |
| 首页 | 搜索框 placeholder 已更新 |
| 服务列表 | 筛选栏 label 文案更新，筛选功能正常 |
| 下单 | 四步流程全部可走通，最终订单正常发布 |
| 下单 | 代练场景显示账号说明，陪玩场景不显示 |
| 订单详情 | PENDING 状态 shimmer 效果可见 |
| 订单详情 | 状态 badge 文案人性化 |
| 订单详情 | 时间线节点文案更新 |
| 订单详情 | 评价提交功能正常 |

- [ ] **Step 3: 构建检查**

```bash
cd frontend && npm run build
```

Expected: build 成功，无报错。

- [ ] **Step 4: 最终 commit**

```bash
cd frontend && git add -A && git commit -m "feat(frontend): complete UX humanization - copy, animations, service-type-aware labels"
```
