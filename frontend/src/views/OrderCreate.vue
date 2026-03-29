<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useOrdersStore } from '@/stores/orders'
import { formatPrice } from '@/utils/display'

const router = useRouter()
const ordersStore = useOrdersStore()

const step = ref('input')
const description = ref('')
const errorMessage = ref('')
const successMessage = ref('')

const formData = ref({
  game_name: '',
  current_rank: '',
  target_rank: '',
  price: '',
  server: '',
  role: '',
  priority: 3,
  game_account: '',
  game_password: '',
  notes: '',
})

const isAnalyzing = computed(() => ordersStore.analyzing)
const isSubmitting = computed(() => ordersStore.loading)
const analysisResult = computed(() => ordersStore.analysisResult)
const isRisky = computed(() => analysisResult.value?.is_risky ?? false)

const popularGames = ['王者荣耀', '英雄联盟', '和平精英', '原神', '永劫无间', '穿越火线']
const promptExamples = [
  '王者荣耀，微信区，星耀三上王者，预算 80 元，希望今晚开始。',
  '英雄联盟，艾欧尼亚，铂金二上钻石，擅长中野优先，预算 180 元。',
  '和平精英，皇冠五到王牌，希望双排并支持语音沟通。',
]
const priorityOptions = [
  { value: 1, label: '普通', hint: '按常规顺序处理' },
  { value: 5, label: '加急', hint: '希望更快开始' },
  { value: 8, label: '高优先级', hint: '更强调时效与排期' },
]

const isFormValid = computed(() => {
  return (
    formData.value.game_name.trim() !== '' &&
    formData.value.current_rank.trim() !== '' &&
    formData.value.target_rank.trim() !== '' &&
    formData.value.price &&
    parseFloat(formData.value.price) > 0
  )
})

const previewItems = computed(() => [
  { label: '游戏名称', value: formData.value.game_name || '待填写' },
  { label: '段位目标', value: formData.value.current_rank && formData.value.target_rank ? `${formData.value.current_rank} → ${formData.value.target_rank}` : '待填写' },
  { label: '预算金额', value: formData.value.price ? formatPrice(formData.value.price) : '待填写' },
  { label: '区服 / 位置', value: [formData.value.server, formData.value.role].filter(Boolean).join(' / ') || '可选信息' },
])

watch(analysisResult, (result) => {
  if (!result) {
    return
  }

  formData.value = {
    ...formData.value,
    game_name: result.game_name || '',
    current_rank: result.current_rank || '',
    target_rank: result.target_rank || '',
    price: result.price ? String(result.price) : '',
    server: result.server || '',
    role: result.role || '',
  }
  step.value = 'form'
})

async function handleAnalyze() {
  if (!description.value.trim()) {
    errorMessage.value = '请先写下你的代练需求描述。'
    return
  }

  errorMessage.value = ''
  successMessage.value = ''

  const result = await ordersStore.analyzeRequirement(description.value)
  if (!result.success) {
    errorMessage.value = result.error
  }
}

async function handleSubmit() {
  if (!isFormValid.value) {
    errorMessage.value = '请补全必填项后再发布订单。'
    return
  }

  errorMessage.value = ''
  const orderData = {
    ...formData.value,
    price: parseFloat(formData.value.price),
    description_raw: description.value,
  }

  const result = await ordersStore.createOrder(orderData)
  if (result.success) {
    successMessage.value = '订单创建成功，正在跳转到订单大厅。'
    setTimeout(() => {
      router.push('/orders')
    }, 1400)
    return
  }

  errorMessage.value = result.error
}

function handleBack() {
  step.value = 'input'
  ordersStore.clearAnalysisResult()
}

function handleSkipAI() {
  step.value = 'form'
}

function usePrompt(prompt) {
  description.value = prompt
}

function appendGame(game) {
  description.value += `${description.value ? '，' : ''}${game}`
}

onMounted(() => {
  ordersStore.clearAnalysisResult()
})
</script>

<template>
  <div class="page-shell space-y-8">
    <section class="hero-panel p-6 sm:p-8 lg:p-10">
      <div class="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
        <div class="space-y-4">
          <p class="eyebrow">发布需求</p>
          <h1 class="section-title !text-4xl sm:!text-5xl">
            先把目标说清楚，再发布更容易被接下的订单。
          </h1>
          <p class="section-copy max-w-3xl">
            把游戏、段位、预算、区服和时段偏好写清楚，系统会帮你整理成更容易理解的订单信息。
          </p>
        </div>

        <div class="flex flex-wrap gap-3">
          <div class="stat-card min-w-[140px]">
            <p class="text-sm text-slate-400">当前步骤</p>
            <p class="mt-2 text-xl font-semibold text-white">{{ step === 'input' ? '需求描述' : '确认发布' }}</p>
          </div>
          <div class="stat-card min-w-[140px]">
            <p class="text-sm text-slate-400">填写方式</p>
            <p class="mt-2 text-xl font-semibold text-white">{{ step === 'input' ? '智能识别' : '手动微调' }}</p>
          </div>
        </div>
      </div>
    </section>

    <div v-if="errorMessage" class="message-error">
      {{ errorMessage }}
    </div>

    <div v-if="successMessage" class="message-success">
      {{ successMessage }}
    </div>

    <div class="grid gap-8 lg:grid-cols-[1.02fr_0.98fr]">
      <section class="space-y-6">
        <div class="surface-card p-5 sm:p-6">
          <div class="flex items-center gap-4">
            <div class="flex items-center gap-3">
              <div class="flex h-10 w-10 items-center justify-center rounded-2xl text-sm font-semibold" :class="step === 'input' ? 'bg-primary-300 text-slate-950' : 'bg-emerald-400 text-slate-950'">
                {{ step === 'input' ? '1' : '✓' }}
              </div>
              <div>
                <p class="text-sm font-medium text-white">描述需求</p>
                <p class="text-xs text-slate-400">输入自然语言，让系统辅助拆解信息</p>
              </div>
            </div>
            <div class="h-px flex-1 bg-white/10"></div>
            <div class="flex items-center gap-3">
              <div class="flex h-10 w-10 items-center justify-center rounded-2xl text-sm font-semibold" :class="step === 'form' ? 'bg-primary-300 text-slate-950' : 'bg-white/5 text-slate-400'">
                2
              </div>
              <div>
                <p class="text-sm font-medium text-white">确认发布</p>
                <p class="text-xs text-slate-400">补全字段并确认下单</p>
              </div>
            </div>
          </div>
        </div>

        <section v-if="step === 'input'" class="surface-card p-6 sm:p-8">
          <div class="space-y-6">
            <div>
              <label for="description" class="label">需求描述</label>
              <textarea
                id="description"
                v-model="description"
                rows="7"
                class="input resize-none"
                placeholder="例如：王者荣耀，微信区，星耀三上王者，预算 80 元，希望今晚开始。"
              ></textarea>
              <p class="helper-text">建议包含：游戏名称、当前段位、目标段位、预算、区服和偏好说明。</p>
            </div>

            <div>
              <p class="label">热门游戏快捷填充</p>
              <div class="flex flex-wrap gap-2">
                <button
                  v-for="game in popularGames"
                  :key="game"
                  type="button"
                  class="tag hover:border-primary-300/40 hover:text-white"
                  @click="appendGame(game)"
                >
                  {{ game }}
                </button>
              </div>
            </div>

            <div>
              <p class="label">推荐描述模板</p>
              <div class="grid gap-3">
                <button
                  v-for="prompt in promptExamples"
                  :key="prompt"
                  type="button"
                  class="rounded-3xl border border-white/10 bg-white/5 p-4 text-left text-sm leading-7 text-slate-300 transition hover:border-primary-300/40 hover:text-white"
                  @click="usePrompt(prompt)"
                >
                  {{ prompt }}
                </button>
              </div>
            </div>

            <div class="flex flex-col gap-3 sm:flex-row">
              <button
                class="btn-primary flex-1 py-3"
                :disabled="isAnalyzing || !description.trim()"
                @click="handleAnalyze"
              >
                <svg
                  v-if="isAnalyzing"
                  class="h-5 w-5 animate-spin"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                {{ isAnalyzing ? '智能识别中...' : '交给系统拆解需求' }}
              </button>
              <button class="btn-secondary py-3" @click="handleSkipAI">
                直接手动填写
              </button>
            </div>
          </div>
        </section>

        <section v-else class="surface-card p-6 sm:p-8">
          <form class="space-y-6" @submit.prevent="handleSubmit">
            <div v-if="analysisResult" class="message-info">
              系统已经根据你的描述预填了部分字段，请继续核对。{{ isRisky ? '当前描述可能包含高风险内容，建议再次确认。' : '' }}
            </div>

            <div class="grid gap-5 sm:grid-cols-2">
              <div>
                <label for="game-name" class="label">游戏名称</label>
                <input id="game-name" v-model="formData.game_name" type="text" class="input" placeholder="例如：王者荣耀" required />
              </div>
              <div>
                <label for="server" class="label">区服</label>
                <input id="server" v-model="formData.server" type="text" class="input" placeholder="例如：微信区、QQ 区、艾欧尼亚" />
              </div>
              <div>
                <label for="current-rank" class="label">当前段位</label>
                <input id="current-rank" v-model="formData.current_rank" type="text" class="input" placeholder="例如：星耀三" required />
              </div>
              <div>
                <label for="target-rank" class="label">目标段位</label>
                <input id="target-rank" v-model="formData.target_rank" type="text" class="input" placeholder="例如：王者" required />
              </div>
              <div>
                <label for="role" class="label">偏好位置 / 角色</label>
                <input id="role" v-model="formData.role" type="text" class="input" placeholder="例如：打野、中单、双排指挥" />
              </div>
              <div>
                <label for="price" class="label">预算金额</label>
                <input id="price" v-model="formData.price" type="number" min="1" step="0.01" class="input" placeholder="例如：88" required />
              </div>
            </div>

            <div>
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

            <div class="border-t border-white/10 pt-6">
              <h2 class="text-lg font-semibold text-white">账号与备注</h2>
              <p class="mt-2 text-sm text-slate-400">账号信息为可选项，建议仅在确认可信流程后再填写完整内容。</p>

              <div class="mt-5 grid gap-5 sm:grid-cols-2">
                <div>
                  <label for="game-account" class="label">游戏账号</label>
                  <input id="game-account" v-model="formData.game_account" type="text" class="input" placeholder="请输入游戏账号" />
                </div>
                <div>
                  <label for="game-password" class="label">游戏密码</label>
                  <input id="game-password" v-model="formData.game_password" type="password" class="input" placeholder="请输入游戏密码" />
                </div>
              </div>

              <div class="mt-5">
                <label for="notes" class="label">补充说明</label>
                <textarea
                  id="notes"
                  v-model="formData.notes"
                  rows="4"
                  class="input resize-none"
                  placeholder="例如：只在晚上 7 点后可接单，希望优先使用语音沟通。"
                ></textarea>
              </div>
            </div>

            <div class="flex flex-col gap-3 sm:flex-row">
              <button type="button" class="btn-secondary py-3" @click="handleBack">返回修改描述</button>
              <button type="submit" class="btn-success flex-1 py-3" :disabled="isSubmitting || !isFormValid">
                <svg
                  v-if="isSubmitting"
                  class="h-5 w-5 animate-spin"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                {{ isSubmitting ? '发布中...' : '确认发布订单' }}
              </button>
            </div>
          </form>
        </section>
      </section>

      <aside class="space-y-6 lg:sticky lg:top-28 lg:self-start">
        <section class="surface-card p-6">
          <p class="text-sm font-medium text-primary-100">订单预览</p>
          <h2 class="mt-2 text-2xl font-semibold text-white">你正在创建的服务卡片</h2>

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

          <div class="mt-6 rounded-3xl border border-white/10 bg-primary-500/10 p-4">
            <p class="text-sm font-medium text-primary-100">原始需求描述</p>
            <p class="mt-2 text-sm leading-7 text-slate-300">
              {{ description || '你输入的自然语言需求会显示在这里，便于随时对照。' }}
            </p>
          </div>
        </section>

        <section class="surface-card p-6">
          <p class="text-sm font-medium text-primary-100">填写建议</p>
          <ul class="mt-4 space-y-3 text-sm leading-7 text-slate-300">
            <li class="flex items-start gap-3">
              <span class="mt-2 h-2 w-2 rounded-full bg-primary-300"></span>
              <span>优先把游戏、段位和预算写清楚，系统才更容易给出可靠结果。</span>
            </li>
            <li class="flex items-start gap-3">
              <span class="mt-2 h-2 w-2 rounded-full bg-primary-300"></span>
              <span>如果涉及账号安全内容，建议先确认流程后再补充敏感信息。</span>
            </li>
            <li class="flex items-start gap-3">
              <span class="mt-2 h-2 w-2 rounded-full bg-primary-300"></span>
              <span>补充清楚时间偏好、沟通方式和角色要求，可以减少反复沟通。</span>
            </li>
          </ul>
        </section>
      </aside>
    </div>
  </div>
</template>
