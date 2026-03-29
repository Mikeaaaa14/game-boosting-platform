<script setup>
import { computed, onMounted, ref } from 'vue'
import api from '@/utils/api'
import { formatDateTime, formatPrice } from '@/utils/display'
import {
  getApplicationStatusMeta,
  getOrderStatusBadgeClass,
  getOrderStatusLabel,
  getUserRoleLabel,
} from '@/utils/order'

const applicationStatus = ref('PENDING')
const applications = ref([])
const orders = ref([])
const loadingApplications = ref(false)
const loadingOrders = ref(false)
const message = ref({ type: '', text: '' })
const submittingKey = ref('')

const reviewForm = ref({})
const orderAction = ref({})

const applicationStatusOptions = [
  { value: 'PENDING', label: '待审核' },
  { value: 'APPROVED', label: '已通过' },
  { value: 'REJECTED', label: '已拒绝' },
  { value: '', label: '全部状态' },
]

const dashboardStats = computed(() => [
  {
    label: '当前申请数',
    value: applications.value.length,
    hint: applicationStatus.value ? `筛选状态：${applicationStatusOptions.find((item) => item.value === applicationStatus.value)?.label}` : '展示全部申请',
  },
  {
    label: '待处理订单',
    value: orders.value.filter((item) => ['PENDING', 'LOCKED'].includes(item.status)).length,
    hint: '优先关注进行中与待接单订单',
  },
  {
    label: '争议 / 取消',
    value: orders.value.filter((item) => ['DISPUTED', 'CANCELLED'].includes(item.status)).length,
    hint: '需要管理员介入的订单会在这里体现',
  },
])

function messageClass(type) {
  if (type === 'success') {
    return 'message-success'
  }

  if (type === 'error') {
    return 'message-error'
  }

  return 'message-info'
}

function applicationMeta(status) {
  return getApplicationStatusMeta(status)
}

async function fetchApplications() {
  loadingApplications.value = true

  try {
    const res = await api.get('/admin/users/applications', {
      params: { status: applicationStatus.value || undefined },
    })
    applications.value = res.data
  } catch (error) {
    message.value = { type: 'error', text: error.message || '加载申请列表失败。' }
  } finally {
    loadingApplications.value = false
  }
}

async function fetchOrders() {
  loadingOrders.value = true

  try {
    const res = await api.get('/admin/orders', { params: { page: 1, page_size: 50 } })
    orders.value = res.data.items
  } catch (error) {
    message.value = { type: 'error', text: error.message || '加载订单列表失败。' }
  } finally {
    loadingOrders.value = false
  }
}

function initReview(userId) {
  if (!reviewForm.value[userId]) {
    reviewForm.value[userId] = { approve: true, booster_quota: 1, review_note: '' }
  }
}

function reviewState(userId) {
  initReview(userId)
  return reviewForm.value[userId]
}

async function submitReview(userId) {
  const payload = reviewState(userId)
  submittingKey.value = `review-${userId}`

  try {
    await api.put(`/admin/users/${userId}/review`, payload)
    message.value = { type: 'success', text: '审核结果已提交。' }
    await fetchApplications()
  } catch (error) {
    message.value = { type: 'error', text: error.message || '提交审核失败。' }
  } finally {
    submittingKey.value = ''
  }
}

function initOrderAction(orderId) {
  if (!orderAction.value[orderId]) {
    orderAction.value[orderId] = { action: 'DISPUTED', reason: '' }
  }
}

function actionState(orderId) {
  initOrderAction(orderId)
  return orderAction.value[orderId]
}

async function interveneOrder(orderId) {
  const payload = actionState(orderId)
  submittingKey.value = `order-${orderId}`

  try {
    await api.put(`/admin/orders/${orderId}/intervene`, payload)
    message.value = { type: 'success', text: '订单处理结果已生效。' }
    await fetchOrders()
  } catch (error) {
    message.value = { type: 'error', text: error.message || '处理订单失败。' }
  } finally {
    submittingKey.value = ''
  }
}

async function refreshDashboard() {
  await Promise.all([fetchApplications(), fetchOrders()])
}

onMounted(async () => {
  await refreshDashboard()
})
</script>

<template>
  <div class="page-shell space-y-8">
    <section class="hero-panel p-6 sm:p-8 lg:p-10">
      <div class="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
        <div class="space-y-4">
          <p class="eyebrow">运营面板</p>
          <h1 class="section-title !text-4xl sm:!text-5xl">
            集中处理代练申请、异常订单和争议介入。
          </h1>
          <p class="section-copy max-w-3xl">
            优先关注待审核申请、进行中订单和争议单，减少漏审与处理延迟。
          </p>
        </div>

        <button class="btn-primary px-6 py-3" @click="refreshDashboard">
          刷新面板数据
        </button>
      </div>

      <div class="mt-8 grid gap-4 sm:grid-cols-3">
        <article
          v-for="item in dashboardStats"
          :key="item.label"
          class="stat-card"
        >
          <p class="text-3xl font-semibold text-white">{{ item.value }}</p>
          <p class="mt-2 text-sm font-medium text-slate-200">{{ item.label }}</p>
          <p class="mt-2 text-xs leading-6 text-slate-400">{{ item.hint }}</p>
        </article>
      </div>
    </section>

    <div v-if="message.text" :class="messageClass(message.type)">
      {{ message.text }}
    </div>

    <section class="surface-card p-6 sm:p-8">
      <div class="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <h2 class="text-2xl font-semibold text-white">代练师申请审核</h2>
          <p class="mt-2 text-sm leading-7 text-slate-400">
            从这里快速查看申请人的游戏、段位和截图信息，并直接给出审核结论。
          </p>
        </div>

        <div class="flex gap-3">
          <select v-model="applicationStatus" class="input min-w-[160px]" @change="fetchApplications">
            <option
              v-for="option in applicationStatusOptions"
              :key="option.value"
              :value="option.value"
            >
              {{ option.label }}
            </option>
          </select>
          <button class="btn-secondary px-5 py-3" @click="fetchApplications">刷新申请</button>
        </div>
      </div>

      <div v-if="loadingApplications" class="flex items-center justify-center py-16">
        <svg class="h-8 w-8 animate-spin text-primary-300" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
        </svg>
      </div>

      <div v-else-if="!applications.length" class="empty-panel mt-6">
        当前没有符合筛选条件的申请。
      </div>

      <div v-else class="mt-6 grid gap-5 xl:grid-cols-2">
        <article
          v-for="item in applications"
          :key="item.user_id"
          class="rounded-[28px] border border-white/10 bg-white/5 p-5"
        >
          <div class="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
            <div class="space-y-2">
              <div class="flex flex-wrap items-center gap-2">
                <h3 class="text-xl font-semibold text-white">{{ item.username }}</h3>
                <span :class="applicationMeta(item.status).badgeClass">{{ applicationMeta(item.status).label }}</span>
              </div>
              <p class="text-sm text-slate-400">{{ item.email }}</p>
              <p class="text-sm text-slate-300">角色：{{ getUserRoleLabel(item.role) }}</p>
            </div>

            <a
              v-if="item.proof_url"
              :href="item.proof_url"
              target="_blank"
              rel="noreferrer"
              class="btn-secondary !px-4 !py-2"
            >
              查看截图
            </a>
          </div>

          <div class="mt-5 grid gap-3 sm:grid-cols-2">
            <div class="rounded-2xl border border-white/10 bg-slate-950/40 p-4">
              <p class="text-xs uppercase tracking-[0.18em] text-slate-500">擅长游戏</p>
              <p class="mt-2 text-sm font-medium text-white">{{ item.game_name || '未填写' }}</p>
            </div>
            <div class="rounded-2xl border border-white/10 bg-slate-950/40 p-4">
              <p class="text-xs uppercase tracking-[0.18em] text-slate-500">目标区间</p>
              <p class="mt-2 text-sm font-medium text-white">{{ item.current_rank || '-' }} → {{ item.target_rank || '-' }}</p>
            </div>
          </div>

          <div class="mt-5 rounded-2xl border border-white/10 bg-slate-950/40 p-4">
            <p class="text-xs uppercase tracking-[0.18em] text-slate-500">申请说明</p>
            <p class="mt-2 text-sm leading-7 text-slate-300">{{ item.note || '未填写补充说明。' }}</p>
          </div>

          <div v-if="item.review_note" class="mt-4 rounded-2xl border border-amber-400/20 bg-amber-400/10 p-4">
            <p class="text-sm font-medium text-amber-100">历史审核备注</p>
            <p class="mt-2 text-sm leading-7 text-amber-50">{{ item.review_note }}</p>
          </div>

          <div class="mt-5 grid gap-3">
            <div class="grid gap-3 sm:grid-cols-3">
              <select class="input" v-model="reviewState(item.user_id).approve">
                <option :value="true">通过</option>
                <option :value="false">拒绝</option>
              </select>
              <input
                v-model.number="reviewState(item.user_id).booster_quota"
                type="number"
                min="0"
                max="50"
                class="input"
                placeholder="代练名额"
              />
              <input
                v-model="reviewState(item.user_id).review_note"
                class="input"
                placeholder="审核备注"
              />
            </div>

            <div class="flex items-center justify-between">
              <p class="text-xs text-slate-500">
                {{ item.reviewed_at ? `最近审核：${formatDateTime(item.reviewed_at)}` : '尚未审核' }}
              </p>
              <button
                class="btn-primary !px-4 !py-2"
                :disabled="submittingKey === `review-${item.user_id}`"
                @click="submitReview(item.user_id)"
              >
                {{ submittingKey === `review-${item.user_id}` ? '提交中...' : '提交审核' }}
              </button>
            </div>
          </div>
        </article>
      </div>
    </section>

    <section class="surface-card p-6 sm:p-8">
      <div class="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <h2 class="text-2xl font-semibold text-white">订单管理</h2>
          <p class="mt-2 text-sm leading-7 text-slate-400">
            对高风险、争议或需要终止的订单进行状态介入，并记录处理原因。
          </p>
        </div>

        <button class="btn-secondary px-5 py-3" @click="fetchOrders">
          刷新订单
        </button>
      </div>

      <div v-if="loadingOrders" class="flex items-center justify-center py-16">
        <svg class="h-8 w-8 animate-spin text-primary-300" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
        </svg>
      </div>

      <div v-else-if="!orders.length" class="empty-panel mt-6">
        当前没有需要展示的订单。
      </div>

      <div v-else class="mt-6 grid gap-5 xl:grid-cols-2">
        <article
          v-for="order in orders"
          :key="order.id"
          class="rounded-[28px] border border-white/10 bg-white/5 p-5"
        >
          <div class="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
            <div>
              <div class="flex flex-wrap items-center gap-2">
                <h3 class="text-xl font-semibold text-white">#{{ order.id }} {{ order.game_name }}</h3>
                <span :class="getOrderStatusBadgeClass(order.status)">{{ getOrderStatusLabel(order.status) }}</span>
              </div>
              <p class="mt-2 text-sm text-slate-300">{{ order.current_rank }} → {{ order.target_rank }}</p>
            </div>

            <div class="text-left sm:text-right">
              <p class="text-sm text-slate-400">订单金额</p>
              <p class="mt-2 text-xl font-semibold text-accent-300">{{ formatPrice(order.price) }}</p>
            </div>
          </div>

          <div class="mt-5 grid gap-3 sm:grid-cols-2">
            <div class="rounded-2xl border border-white/10 bg-slate-950/40 p-4">
              <p class="text-xs uppercase tracking-[0.18em] text-slate-500">发布用户</p>
              <p class="mt-2 text-sm font-medium text-white">{{ order.user?.username || '未公开' }}</p>
            </div>
            <div class="rounded-2xl border border-white/10 bg-slate-950/40 p-4">
              <p class="text-xs uppercase tracking-[0.18em] text-slate-500">当前代练师</p>
              <p class="mt-2 text-sm font-medium text-white">{{ order.booster?.username || '尚未接单' }}</p>
            </div>
          </div>

          <div class="mt-5 rounded-2xl border border-white/10 bg-slate-950/40 p-4">
            <p class="text-xs uppercase tracking-[0.18em] text-slate-500">需求描述</p>
            <p class="mt-2 text-sm leading-7 text-slate-300">{{ order.description_raw || '暂无详细描述。' }}</p>
          </div>

          <div class="mt-5 grid gap-3 sm:grid-cols-3">
            <select class="input" v-model="actionState(order.id).action">
              <option value="DISPUTED">标记争议</option>
              <option value="CANCELLED">取消订单</option>
            </select>
            <input
              v-model="actionState(order.id).reason"
              class="input sm:col-span-2"
              placeholder="请输入处理原因"
            />
          </div>

          <div class="mt-5 flex items-center justify-between">
            <p class="text-xs text-slate-500">创建于 {{ formatDateTime(order.created_at) }}</p>
            <button
              class="btn-danger !px-4 !py-2"
              :disabled="submittingKey === `order-${order.id}`"
              @click="interveneOrder(order.id)"
            >
              {{ submittingKey === `order-${order.id}` ? '处理中...' : '执行处理' }}
            </button>
          </div>
        </article>
      </div>
    </section>
  </div>
</template>
