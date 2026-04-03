<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'

import { useGamesStore } from '@/stores/games'
import { useOrdersStore } from '@/stores/orders'
import { formatPrice } from '@/utils/display'
import {
  buildAccentStyle,
  buildGameSurfaceStyle,
  getGameCategoryMeta,
  getGamePlatformLabel,
  getGameServiceTypes,
} from '@/utils/gameCatalog'

const router = useRouter()
const gamesStore = useGamesStore()
const ordersStore = useOrdersStore()

const step = ref('select')
const selectedCategory = ref('')
const selectedGameId = ref(null)
const description = ref('')
const errorMessage = ref('')
const successMessage = ref('')

const formData = ref({
  game_id: null,
  game_name: '',
  current_rank: '',
  target_rank: '',
  price: '',
  server: '',
  role: '',
  service_type: '',
  priority: 3,
  notes: '',
  game_account: '',
  game_password: '',
  ai_tags: null,
})

const priorityOptions = [
  { value: 1, label: '普通', hint: '按标准节奏排队处理' },
  { value: 5, label: '加急', hint: '希望尽快开始推进' },
  { value: 8, label: '高优先级', hint: '更强调时效和连续处理' },
]

const categories = computed(() => gamesStore.categories.filter((item) => item.count > 0))
const currentCategory = computed(() => {
  return selectedCategory.value || categories.value[0]?.value || ''
})
const visibleGames = computed(() => {
  return (gamesStore.gamesByCategory[currentCategory.value] || []).slice().sort((a, b) => a.sort_order - b.sort_order)
})
const selectedGame = computed(() => {
  return selectedGameId.value ? gamesStore.getGameById(Number(selectedGameId.value)) : null
})
const selectedGameServiceTypes = computed(() => getGameServiceTypes(selectedGame.value))
const analysisResult = computed(() => ordersStore.analysisResult)
const isAnalyzing = computed(() => ordersStore.analyzing)
const isSubmitting = computed(() => ordersStore.loading)

const aiSummaryCards = computed(() => {
  if (!analysisResult.value) {
    return []
  }

  return [
    { label: '游戏', value: analysisResult.value.game_name || selectedGame.value?.name || '未识别' },
    { label: '服务类型', value: analysisResult.value.service_type || formData.value.service_type || '待确认' },
    { label: '区服', value: analysisResult.value.server || formData.value.server || '待确认' },
    { label: '当前段位', value: analysisResult.value.current_rank || formData.value.current_rank || '待确认' },
    { label: '目标段位', value: analysisResult.value.target_rank || formData.value.target_rank || '待确认' },
    { label: '预算', value: analysisResult.value.price ? formatPrice(analysisResult.value.price) : (formData.value.price ? formatPrice(formData.value.price) : '待确认') },
  ]
})

const previewItems = computed(() => [
  { label: '游戏', value: selectedGame.value?.name || '未选择' },
  { label: '服务类型', value: formData.value.service_type || '待确认' },
  { label: '目标', value: formData.value.current_rank || formData.value.target_rank ? `${formData.value.current_rank || '未填'} → ${formData.value.target_rank || '未填'}` : '等待 AI 或手动补充' },
  { label: '预算', value: formData.value.price ? formatPrice(formData.value.price) : '待填写' },
  { label: '区服 / 角色', value: [formData.value.server, formData.value.role].filter(Boolean).join(' / ') || '可选项' },
])

const selectedGameStyle = computed(() => buildGameSurfaceStyle(selectedGame.value))
const selectedGameBadgeStyle = computed(() => buildAccentStyle(selectedGame.value))

const canGoToDescribe = computed(() => !!selectedGame.value)
const canPublish = computed(() => {
  return Boolean(selectedGame.value && description.value.trim() && Number(formData.value.price) > 0)
})

function syncSelectedGame(game) {
  if (!game) {
    return
  }

  selectedGameId.value = game.id
  formData.value.game_id = game.id
  formData.value.game_name = game.name

  if (!selectedGameServiceTypes.value.includes(formData.value.service_type)) {
    formData.value.service_type = getGameServiceTypes(game)[0] || ''
  }
}

function pickGame(game) {
  syncSelectedGame(game)
}

function nextFromSelect() {
  if (!selectedGame.value) {
    errorMessage.value = '请先选择一个游戏。'
    return
  }

  errorMessage.value = ''
  step.value = 'describe'
}

function backToSelect() {
  step.value = 'select'
}

function backToDescribe() {
  step.value = 'describe'
}

function applyPrompt(prompt) {
  description.value = prompt
}

function appendServiceType(serviceType) {
  description.value += `${description.value ? '，' : ''}${serviceType}`
}

async function analyzeRequirement() {
  if (!description.value.trim()) {
    errorMessage.value = '请先写下你的需求描述。'
    return
  }

  errorMessage.value = ''
  successMessage.value = ''

  const result = await ordersStore.analyzeRequirement(description.value)
  if (!result.success) {
    errorMessage.value = result.error
    return
  }

  const recognizedGame = result.data?.game_id ? gamesStore.getGameById(result.data.game_id) : selectedGame.value
  if (recognizedGame) {
    syncSelectedGame(recognizedGame)
  }

  formData.value = {
    ...formData.value,
    game_id: result.data?.game_id || formData.value.game_id,
    game_name: result.data?.game_name || formData.value.game_name,
    current_rank: result.data?.current_rank || formData.value.current_rank,
    target_rank: result.data?.target_rank || formData.value.target_rank,
    price: result.data?.price ? String(result.data.price) : formData.value.price,
    server: result.data?.server || formData.value.server,
    role: result.data?.role || formData.value.role,
    service_type: result.data?.service_type || formData.value.service_type || selectedGameServiceTypes.value[0] || '',
    ai_tags: result.data?.ai_tags || formData.value.ai_tags,
  }

  step.value = 'ai'
}

function continueToConfirm() {
  if (!selectedGame.value) {
    errorMessage.value = '请先选择游戏。'
    step.value = 'select'
    return
  }

  errorMessage.value = ''
  step.value = 'confirm'
}

function skipAIAndConfirm() {
  if (!selectedGame.value) {
    errorMessage.value = '请先选择游戏。'
    step.value = 'select'
    return
  }

  formData.value.ai_tags = formData.value.ai_tags || {
    game_id: selectedGame.value.id,
    service_type: formData.value.service_type || selectedGameServiceTypes.value[0] || '',
    server: formData.value.server || null,
    detail: {
      current_rank: formData.value.current_rank || '',
      target_rank: formData.value.target_rank || '',
      role: formData.value.role || '',
      requirements: [],
    },
  }

  step.value = 'confirm'
}

async function publishOrder() {
  if (!canPublish.value) {
    errorMessage.value = '请至少确认游戏、需求描述和预算金额。'
    return
  }

  errorMessage.value = ''
  successMessage.value = ''

  const payload = {
    ...formData.value,
    game_id: selectedGame.value.id,
    game_name: selectedGame.value.name,
    price: Number(formData.value.price),
    description_raw: description.value.trim(),
    ai_tags: formData.value.ai_tags,
    service_type: formData.value.service_type || selectedGameServiceTypes.value[0] || '',
  }

  const result = await ordersStore.createOrder(payload)
  if (!result.success) {
    errorMessage.value = result.error
    return
  }

  successMessage.value = '订单已发布，正在跳转到订单大厅。'
  window.setTimeout(() => {
    router.push({ name: 'orders' })
  }, 900)
}

watch(
  selectedGame,
  (game) => {
    if (!game) {
      return
    }
    formData.value.game_id = game.id
    formData.value.game_name = game.name
    if (!selectedGameServiceTypes.value.includes(formData.value.service_type)) {
      formData.value.service_type = selectedGameServiceTypes.value[0] || ''
    }
  }
)

watch(
  categories,
  (value) => {
    if (!selectedCategory.value && value.length) {
      selectedCategory.value = value[0].value
    }
  },
  { immediate: true }
)

onMounted(async () => {
  ordersStore.clearAnalysisResult()
  await gamesStore.ensureCatalog()
})
</script>

<template>
  <div class="page-shell space-y-8">
    <section class="hero-panel scanline-overlay p-6 sm:p-8 lg:p-10">
      <div class="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
        <div class="space-y-4">
          <p class="eyebrow">发布订单</p>
          <h1 class="section-title neon-text !text-4xl sm:!text-5xl">
            选游戏，写需求，直接发。
          </h1>
          <p class="section-copy max-w-3xl">
            四步走完，不绕路。
          </p>
        </div>

        <div class="grid gap-4 sm:grid-cols-4">
          <article class="stat-card cyber-corner">
            <p class="text-sm text-slate-400">第 1 步</p>
            <p class="mt-2 text-xl font-semibold text-white">选游戏</p>
          </article>
          <article class="stat-card cyber-corner">
            <p class="text-sm text-slate-400">第 2 步</p>
            <p class="mt-2 text-xl font-semibold text-white">写需求</p>
          </article>
          <article class="stat-card cyber-corner">
            <p class="text-sm text-slate-400">第 3 步</p>
            <p class="mt-2 text-xl font-semibold text-white">AI 提取</p>
          </article>
          <article class="stat-card cyber-corner">
            <p class="text-sm text-slate-400">第 4 步</p>
            <p class="mt-2 text-xl font-semibold text-white">确认发布</p>
          </article>
        </div>
      </div>
    </section>

    <div v-if="errorMessage" class="message-error">{{ errorMessage }}</div>
    <div v-if="successMessage" class="message-success">{{ successMessage }}</div>

    <div class="grid gap-8 xl:grid-cols-[1.04fr_0.96fr]">
      <section class="space-y-6">
        <div class="surface-card p-5 sm:p-6">
          <div class="flex flex-wrap items-center gap-3">
            <button type="button" :class="step === 'select' ? 'tab-pill-active' : 'tab-pill'" @click="step = 'select'">1. 选游戏</button>
            <button type="button" :class="step === 'describe' ? 'tab-pill-active' : 'tab-pill'" :disabled="!canGoToDescribe" @click="step = 'describe'">2. 写需求</button>
            <button type="button" :class="step === 'ai' ? 'tab-pill-active' : 'tab-pill'" :disabled="!analysisResult" @click="step = 'ai'">3. AI 提取</button>
            <button type="button" :class="step === 'confirm' ? 'tab-pill-active' : 'tab-pill'" :disabled="!selectedGame" @click="step = 'confirm'">4. 确认价格</button>
          </div>
        </div>

        <section v-if="step === 'select'" class="surface-card p-6 sm:p-8">
          <div class="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
            <div>
              <p class="text-sm font-medium text-primary-100">第 1 步 / 共 4 步</p>
              <h2 class="mt-2 text-2xl font-semibold text-white">选择你这次要发布需求的游戏</h2>
            </div>

            <div class="flex flex-wrap gap-2">
              <button
                v-for="category in categories"
                :key="category.value"
                type="button"
                :class="currentCategory === category.value ? 'filter-pill-active' : 'filter-pill'"
                @click="selectedCategory = category.value"
              >
                {{ getGameCategoryMeta(category.value).label }}
              </button>
            </div>
          </div>

          <div class="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            <button
              v-for="game in visibleGames"
              :key="game.id"
              type="button"
              :class="selectedGameId === game.id ? 'catalog-card-active cyber-corner text-left' : 'catalog-card cyber-corner text-left'"
              @click="pickGame(game)"
            >
              <div class="cover-card p-5" :style="buildGameSurfaceStyle(game)">
                <div class="relative z-10 flex h-full flex-col justify-between">
                  <div class="flex items-center justify-between gap-4">
                    <span class="tag">{{ getGamePlatformLabel(game.platform) }}</span>
                    <div
                      class="flex h-11 w-11 items-center justify-center rounded-[18px] border text-sm font-semibold text-white"
                      :style="buildAccentStyle(game)"
                    >
                      {{ game.name.slice(0, 1) }}
                    </div>
                  </div>

                  <div class="space-y-3">
                    <h3 class="text-2xl font-semibold text-white">{{ game.name }}</h3>
                    <p class="text-sm text-slate-300">{{ game.english_name || '热门专区' }}</p>
                    <p class="text-sm leading-6 text-slate-300">{{ game.description }}</p>
                  </div>
                </div>
              </div>

              <div class="mt-4 flex flex-wrap gap-2">
                <span
                  v-for="serviceType in getGameServiceTypes(game).slice(0, 3)"
                  :key="`${game.id}-${serviceType}`"
                  class="tag"
                >
                  {{ serviceType }}
                </span>
              </div>
            </button>
          </div>

          <div class="mt-6 flex justify-end">
            <button class="btn-primary" :disabled="!canGoToDescribe" @click="nextFromSelect">
              下一步：写需求
            </button>
          </div>
        </section>

        <section v-else-if="step === 'describe'" class="surface-card p-6 sm:p-8">
          <p class="text-sm font-medium text-primary-100">第 2 步 / 共 4 步</p>
          <h2 class="mt-2 text-2xl font-semibold text-white">用自然语言写下你的需求</h2>
          <p class="mt-3 text-sm leading-7 text-slate-400">
            建议把区服、目标段位、时段和偏好一起写进去，AI 会帮你整理成结构化标签。
          </p>

          <div class="mt-6 rounded-[26px] border border-white/10 p-5" :style="selectedGameStyle">
            <div class="relative z-10 flex flex-wrap items-center justify-between gap-4">
              <div class="flex items-center gap-4">
                <div
                  class="flex h-12 w-12 items-center justify-center rounded-[18px] border text-sm font-semibold text-white"
                  :style="selectedGameBadgeStyle"
                >
                  {{ selectedGame?.name?.slice(0, 1) || 'G' }}
                </div>
                <div>
                  <p class="text-lg font-semibold text-white">{{ selectedGame?.name }}</p>
                  <p class="mt-2 text-sm text-slate-300">{{ selectedGame?.description }}</p>
                </div>
              </div>

              <div class="flex flex-wrap gap-2">
                <button
                  v-for="serviceType in selectedGameServiceTypes"
                  :key="serviceType"
                  type="button"
                  class="filter-pill"
                  @click="appendServiceType(serviceType)"
                >
                  {{ serviceType }}
                </button>
              </div>
            </div>
          </div>

          <div class="mt-6">
            <label class="label" for="order-description">需求描述</label>
            <textarea
              id="order-description"
              v-model="description"
              rows="7"
              class="input resize-none"
              placeholder="例如：王者荣耀，微信区，星耀三上王者，希望晚上开打，要求打野位，预算 88 元。"
            ></textarea>
          </div>

          <div class="mt-6 flex flex-col gap-3 sm:flex-row">
            <button class="btn-secondary" @click="backToSelect">返回改游戏</button>
            <button class="btn-secondary" @click="skipAIAndConfirm">跳过识别，直接填写</button>
            <button class="btn-primary flex-1" :disabled="isAnalyzing" @click="analyzeRequirement">
              {{ isAnalyzing ? 'AI 正在拆解需求...' : '下一步：让 AI 提取标签' }}
            </button>
          </div>
        </section>

        <section v-else-if="step === 'ai'" class="surface-card p-6 sm:p-8">
          <p class="text-sm font-medium text-primary-100">第 3 步 / 共 4 步</p>
          <h2 class="mt-2 text-2xl font-semibold text-white">AI 已经把你的需求拆成结构化标签</h2>
          <p class="mt-3 text-sm leading-7 text-slate-400">
            这里会保留旧字段展示，同时也给你新的 `ai_tags` 结构，确认后进入价格和发布阶段。
          </p>

          <div class="mt-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
            <article
              v-for="item in aiSummaryCards"
              :key="item.label"
              class="rounded-3xl border border-white/10 bg-white/5 p-4"
            >
              <p class="text-xs uppercase tracking-[0.18em] text-slate-500">{{ item.label }}</p>
              <p class="mt-2 text-sm font-medium text-white">{{ item.value }}</p>
            </article>
          </div>

          <div class="mt-6 rounded-3xl border border-white/10 bg-white/5 p-5">
            <p class="text-sm font-medium text-primary-100">AI Tags 预览</p>
            <pre class="mt-3 overflow-x-auto text-xs leading-6 text-slate-300">{{ JSON.stringify(formData.ai_tags, null, 2) }}</pre>
          </div>

          <div class="mt-6 flex flex-col gap-3 sm:flex-row">
            <button class="btn-secondary" @click="backToDescribe">返回改描述</button>
            <button class="btn-secondary" :disabled="isAnalyzing" @click="analyzeRequirement">重新识别</button>
            <button class="btn-primary flex-1" @click="continueToConfirm">下一步：确认价格并发布</button>
          </div>
        </section>

        <section v-else class="surface-card p-6 sm:p-8">
          <p class="text-sm font-medium text-primary-100">第 4 步 / 共 4 步</p>
          <h2 class="mt-2 text-2xl font-semibold text-white">确认价格与最终字段</h2>
          <p class="mt-3 text-sm leading-7 text-slate-400">
            AI 结果可以继续微调。你只需要把价格和最后的偏好确认好，就能发布订单。
          </p>

          <div class="mt-6 grid gap-5 sm:grid-cols-2">
            <div>
              <label class="label" for="confirm-service-type">服务类型</label>
              <select id="confirm-service-type" v-model="formData.service_type" class="input">
                <option
                  v-for="serviceType in selectedGameServiceTypes"
                  :key="serviceType"
                  :value="serviceType"
                >
                  {{ serviceType }}
                </option>
              </select>
            </div>
            <div>
              <label class="label" for="confirm-server">区服</label>
              <input id="confirm-server" v-model="formData.server" type="text" class="input" placeholder="例如：微信区 / 艾欧尼亚" />
            </div>
            <div>
              <label class="label" for="confirm-current-rank">当前段位</label>
              <input id="confirm-current-rank" v-model="formData.current_rank" type="text" class="input" placeholder="例如：星耀三" />
            </div>
            <div>
              <label class="label" for="confirm-target-rank">目标段位</label>
              <input id="confirm-target-rank" v-model="formData.target_rank" type="text" class="input" placeholder="例如：王者" />
            </div>
            <div>
              <label class="label" for="confirm-role">位置 / 角色偏好</label>
              <input id="confirm-role" v-model="formData.role" type="text" class="input" placeholder="例如：打野 / 中单 / 指挥" />
            </div>
            <div>
              <label class="label" for="confirm-price">预算金额</label>
              <input id="confirm-price" v-model="formData.price" type="number" min="1" step="0.01" class="input" placeholder="例如：88" />
            </div>
          </div>

          <div class="mt-6">
            <p class="label">优先级</p>
            <div class="grid gap-3 sm:grid-cols-3">
              <button
                v-for="option in priorityOptions"
                :key="option.value"
                type="button"
                class="rounded-3xl border p-4 text-left transition"
                :class="formData.priority === option.value ? 'border-primary-300/40 bg-primary-500/10' : 'border-white/10 bg-white/5 hover:border-white/20'"
                @click="formData.priority = option.value"
              >
                <p class="text-sm font-semibold text-white">{{ option.label }}</p>
                <p class="mt-2 text-xs leading-6 text-slate-400">{{ option.hint }}</p>
              </button>
            </div>
          </div>

          <div class="mt-6 grid gap-5 sm:grid-cols-2">
            <div>
              <label class="label" for="confirm-account">游戏账号</label>
              <input id="confirm-account" v-model="formData.game_account" type="text" class="input" placeholder="可选填写" />
            </div>
            <div>
              <label class="label" for="confirm-password">游戏密码</label>
              <input id="confirm-password" v-model="formData.game_password" type="password" class="input" placeholder="可选填写" />
            </div>
          </div>

          <div class="mt-6">
            <label class="label" for="confirm-notes">补充说明</label>
            <textarea id="confirm-notes" v-model="formData.notes" rows="4" class="input resize-none" placeholder="例如：希望晚上 8 点后开打，全程语音沟通。"></textarea>
          </div>

          <div class="mt-6 flex flex-col gap-3 sm:flex-row">
            <button class="btn-secondary" @click="analysisResult ? (step = 'ai') : (step = 'describe')">
              返回上一步
            </button>
            <button class="btn-primary flex-1" :disabled="isSubmitting || !canPublish" @click="publishOrder">
              {{ isSubmitting ? '正在发布订单...' : '确认发布订单' }}
            </button>
          </div>
        </section>
      </section>

      <aside class="space-y-6 xl:sticky xl:top-28 xl:self-start">
        <section class="surface-card cyber-corner p-6">
          <p class="text-sm font-medium text-primary-100">实时预览</p>
          <h2 class="mt-2 text-2xl font-semibold text-white">这条订单准备怎么展示</h2>

          <div class="mt-6 cover-card p-5" :style="selectedGameStyle">
            <div class="relative z-10 flex h-full flex-col justify-between">
              <div class="flex items-center justify-between gap-4">
                <span class="tag">{{ selectedGame?.name || '待选择游戏' }}</span>
                <div
                  class="flex h-11 w-11 items-center justify-center rounded-[18px] border text-sm font-semibold text-white"
                  :style="selectedGameBadgeStyle"
                >
                  {{ selectedGame?.name?.slice(0, 1) || 'G' }}
                </div>
              </div>

              <div class="space-y-3">
                <h3 class="text-2xl font-semibold text-white">{{ formData.current_rank || '当前段位' }} <span class="text-primary-100">→</span> {{ formData.target_rank || '目标段位' }}</h3>
                <p class="text-sm leading-6 text-slate-300">{{ description || '你输入的自然语言需求会显示在这里。' }}</p>
              </div>
            </div>
          </div>

          <div class="mt-6 space-y-3">
            <div
              v-for="item in previewItems"
              :key="item.label"
              class="rounded-3xl border border-white/10 bg-white/5 p-4"
            >
              <p class="text-xs uppercase tracking-[0.18em] text-slate-500">{{ item.label }}</p>
              <p class="mt-2 text-sm font-medium text-white">{{ item.value }}</p>
            </div>
          </div>
        </section>

        <section class="surface-card p-6">
          <p class="text-sm font-medium text-primary-100">当前步骤建议</p>
          <ul class="mt-4 space-y-3 text-sm leading-7 text-slate-300">
            <li class="flex items-start gap-3">
              <span class="mt-2 h-2 w-2 rounded-full bg-primary-300"></span>
              <span>先把游戏选准，专区模板和 AI 识别会更稳定。</span>
            </li>
            <li class="flex items-start gap-3">
              <span class="mt-2 h-2 w-2 rounded-full bg-primary-300"></span>
              <span>描述里尽量带上区服、目标、预算和时间要求，减少来回沟通。</span>
            </li>
            <li class="flex items-start gap-3">
              <span class="mt-2 h-2 w-2 rounded-full bg-primary-300"></span>
              <span>确认发布前，可以手动微调 AI 给出的服务类型和价格。</span>
            </li>
          </ul>
        </section>
      </aside>
    </div>
  </div>
</template>
