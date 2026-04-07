<script setup>
import { computed, onMounted, ref } from 'vue'

import { useGamesStore } from '@/stores/games'
import api from '@/utils/api'
import { formatDateTime, formatPrice } from '@/utils/display'
import {
  getApplicationStatusMeta,
  getOrderStatusBadgeClass,
  getOrderStatusLabel,
  getUserRoleLabel,
} from '@/utils/order'
import { getGameCategoryMeta, getGamePlatformLabel } from '@/utils/gameCatalog'

const gamesStore = useGamesStore()

const activeTab = ref('applications')
const applicationStatus = ref('PENDING')
const applications = ref([])
const orders = ref([])
const loadingApplications = ref(false)
const loadingOrders = ref(false)
const loadingGames = computed(() => gamesStore.loading)
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
  { label: '申请', value: applications.value.length },
  { label: '订单', value: orders.value.length },
  { label: '游戏', value: gamesStore.catalogGames.length },
])

function messageClass(type) {
  if (type === 'success') return 'message-success'
  if (type === 'error') return 'message-error'
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
    message.value = { type: 'error', text: error.message || '加载失败' }
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
    message.value = { type: 'error', text: error.message || '加载失败' }
  } finally {
    loadingOrders.value = false
  }
}

async function fetchGames() {
  await gamesStore.fetchGames('', '', { pageSize: 100 })
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
  submittingKey.value = `review-${userId}`
  try {
    await api.put(`/admin/users/${userId}/review`, reviewState(userId))
    message.value = { type: 'success', text: '审核已提交' }
    await fetchApplications()
  } catch (error) {
    message.value = { type: 'error', text: error.message || '提交失败' }
  } finally {
    submittingKey.value = ''
  }
}

function paymentLabel(status) {
  if (status === 'PAID') return '已支付'
  if (status === 'REFUNDED') return '已退款'
  return '待支付'
}

function paymentBadgeClass(status) {
  return {
    tag: true,
    '!bg-yellow-500/20 !text-yellow-300 !border-yellow-500/30': status === 'UNPAID',
    '!bg-green-500/20 !text-green-300 !border-green-500/30': status === 'PAID',
    '!bg-slate-500/20 !text-slate-300 !border-slate-500/30': status === 'REFUNDED',
  }
}

async function handleRefund(orderId) {
  submittingKey.value = `refund-${orderId}`
  try {
    await api.put(`/orders/${orderId}/refund`)
    message.value = { type: 'success', text: '退款成功' }
    await fetchOrders()
  } catch (error) {
    message.value = { type: 'error', text: error.message || '退款失败' }
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
  submittingKey.value = `order-${orderId}`
  try {
    await api.put(`/admin/orders/${orderId}/intervene`, actionState(orderId))
    message.value = { type: 'success', text: '订单已处理' }
    await fetchOrders()
  } catch (error) {
    message.value = { type: 'error', text: error.message || '处理失败' }
  } finally {
    submittingKey.value = ''
  }
}

async function toggleGameStatus(game) {
  submittingKey.value = `game-${game.id}`
  const result = await gamesStore.updateGame(game.id, { is_active: !game.is_active })
  if (result.success) {
    message.value = { type: 'success', text: game.is_active ? '已下架' : '已上架' }
  } else {
    message.value = { type: 'error', text: result.error }
  }
  submittingKey.value = ''
}

async function refreshDashboard() {
  await Promise.all([fetchApplications(), fetchOrders(), fetchGames()])
}

onMounted(async () => {
  await refreshDashboard()
})
</script>

<template>
  <div class="page-shell space-y-6">
    <section class="hero-panel scanline-overlay p-6 sm:p-8">
      <div class="flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
        <div class="space-y-4">
          <p class="eyebrow">管理后台</p>
          <h1 class="section-title neon-text !text-4xl sm:!text-5xl">申请、订单、游戏</h1>
        </div>

        <div class="grid gap-4 sm:grid-cols-3">
          <article v-for="item in dashboardStats" :key="item.label" class="stat-card">
            <p class="text-sm text-slate-400">{{ item.label }}</p>
            <p class="mt-2 text-3xl font-semibold text-white">{{ item.value }}</p>
          </article>
        </div>
      </div>
    </section>

    <div v-if="message.text" :class="messageClass(message.type)">{{ message.text }}</div>

    <section class="surface-card p-5 sm:p-6">
      <div class="flex flex-wrap gap-3">
        <button type="button" :class="activeTab === 'applications' ? 'tab-pill-active' : 'tab-pill'" @click="activeTab = 'applications'">代练审核</button>
        <button type="button" :class="activeTab === 'orders' ? 'tab-pill-active' : 'tab-pill'" @click="activeTab = 'orders'">订单管理</button>
        <button type="button" :class="activeTab === 'games' ? 'tab-pill-active' : 'tab-pill'" @click="activeTab = 'games'">游戏管理</button>
        <button class="btn-secondary ml-auto !px-4 !py-2" @click="refreshDashboard">刷新</button>
      </div>
    </section>

    <section v-if="activeTab === 'applications'" class="surface-card p-6 sm:p-8">
      <div class="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <h2 class="text-2xl font-semibold text-white">代练审核</h2>
        <div class="flex gap-3">
          <select v-model="applicationStatus" class="input min-w-[160px]" @change="fetchApplications">
            <option v-for="option in applicationStatusOptions" :key="option.value" :value="option.value">{{ option.label }}</option>
          </select>
        </div>
      </div>

      <div v-if="loadingApplications" class="flex items-center justify-center py-16">
        <svg class="h-8 w-8 animate-spin text-primary-300" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
        </svg>
      </div>

      <div v-else-if="!applications.length" class="empty-panel mt-6">暂无申请</div>

      <div v-else class="mt-6 grid gap-4 xl:grid-cols-2">
        <article v-for="item in applications" :key="item.user_id" class="catalog-card cyber-corner">
          <div class="flex items-start justify-between gap-4">
            <div>
              <div class="flex flex-wrap items-center gap-2">
                <h3 class="text-xl font-semibold text-white">{{ item.username }}</h3>
                <span :class="applicationMeta(item.status).badgeClass">{{ applicationMeta(item.status).label }}</span>
              </div>
              <p class="mt-2 text-sm text-slate-400">{{ item.email }}</p>
              <p class="mt-2 text-sm text-slate-300">{{ item.game_name || '未填游戏' }} · {{ item.current_rank || '-' }} → {{ item.target_rank || '-' }}</p>
            </div>
            <a v-if="item.proof_url" :href="item.proof_url" target="_blank" rel="noreferrer" class="btn-secondary !px-4 !py-2">截图</a>
          </div>

          <div class="mt-5 grid gap-3 sm:grid-cols-3">
            <select class="input" v-model="reviewState(item.user_id).approve">
              <option :value="true">通过</option>
              <option :value="false">拒绝</option>
            </select>
            <input v-model.number="reviewState(item.user_id).booster_quota" type="number" min="0" max="50" class="input" placeholder="名额" />
            <input v-model="reviewState(item.user_id).review_note" class="input" placeholder="备注" />
          </div>

          <div class="mt-5 flex items-center justify-between">
            <p class="text-xs text-slate-500">{{ getUserRoleLabel(item.role) }}</p>
            <button class="btn-primary !px-4 !py-2" :disabled="submittingKey === `review-${item.user_id}`" @click="submitReview(item.user_id)">
              {{ submittingKey === `review-${item.user_id}` ? '提交中...' : '提交' }}
            </button>
          </div>
        </article>
      </div>
    </section>

    <section v-else-if="activeTab === 'orders'" class="surface-card p-6 sm:p-8">
      <h2 class="text-2xl font-semibold text-white">订单管理</h2>

      <div v-if="loadingOrders" class="flex items-center justify-center py-16">
        <svg class="h-8 w-8 animate-spin text-primary-300" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
        </svg>
      </div>

      <div v-else-if="!orders.length" class="empty-panel mt-6">暂无订单</div>

      <div v-else class="mt-6 grid gap-4 xl:grid-cols-2">
        <article v-for="order in orders" :key="order.id" class="catalog-card cyber-corner">
          <div class="flex items-start justify-between gap-4">
            <div>
              <div class="flex flex-wrap items-center gap-2">
                <h3 class="text-xl font-semibold text-white">#{{ order.id }} {{ order.game_name }}</h3>
                <span :class="getOrderStatusBadgeClass(order.status)">{{ getOrderStatusLabel(order.status) }}</span>
                <span v-if="order.payment_status" :class="paymentBadgeClass(order.payment_status)">{{ paymentLabel(order.payment_status) }}</span>
              </div>
              <p class="mt-2 text-sm text-slate-300">{{ order.current_rank }} → {{ order.target_rank }}</p>
            </div>
            <p class="text-lg font-semibold text-accent-300">{{ formatPrice(order.price) }}</p>
          </div>

          <div class="mt-5 grid gap-3 sm:grid-cols-3">
            <select class="input" v-model="actionState(order.id).action">
              <option value="DISPUTED">争议</option>
              <option value="CANCELLED">取消</option>
              <option value="COMPLETED">完结（解决争议）</option>
            </select>
            <input v-model="actionState(order.id).reason" class="input sm:col-span-2" placeholder="原因" />
          </div>

          <div class="mt-5 flex items-center justify-between">
            <p class="text-xs text-slate-500">{{ formatDateTime(order.created_at) }}</p>
            <div class="flex gap-2">
              <button
                v-if="order.payment_status === 'PAID' && ['CANCELLED', 'DISPUTED'].includes(order.status)"
                class="btn-secondary !px-4 !py-2"
                :disabled="submittingKey === `refund-${order.id}`"
                @click="handleRefund(order.id)"
              >
                {{ submittingKey === `refund-${order.id}` ? '退款中...' : '退款' }}
              </button>
              <button class="btn-danger !px-4 !py-2" :disabled="submittingKey === `order-${order.id}`" @click="interveneOrder(order.id)">
                {{ submittingKey === `order-${order.id}` ? '处理中...' : '执行' }}
              </button>
            </div>
          </div>
        </article>
      </div>
    </section>

    <section v-else class="surface-card p-6 sm:p-8">
      <h2 class="text-2xl font-semibold text-white">游戏管理</h2>

      <div v-if="loadingGames" class="flex items-center justify-center py-16">
        <svg class="h-8 w-8 animate-spin text-primary-300" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
        </svg>
      </div>

      <div v-else class="mt-6 grid gap-4 xl:grid-cols-2">
        <article v-for="game in gamesStore.catalogGames" :key="game.id" class="catalog-card cyber-corner">
          <div class="flex items-start justify-between gap-4">
            <div>
              <div class="flex flex-wrap items-center gap-2">
                <h3 class="text-xl font-semibold text-white">{{ game.name }}</h3>
                <span :class="game.is_active ? 'badge-approved' : 'badge-cancelled'">{{ game.is_active ? '上架' : '下架' }}</span>
              </div>
              <p class="mt-2 text-sm text-slate-300">{{ getGameCategoryMeta(game.category).label }} · {{ getGamePlatformLabel(game.platform) }}</p>
            </div>
            <button class="btn-secondary !px-4 !py-2" :disabled="submittingKey === `game-${game.id}`" @click="toggleGameStatus(game)">
              {{ submittingKey === `game-${game.id}` ? '处理中...' : (game.is_active ? '下架' : '上架') }}
            </button>
          </div>
        </article>
      </div>
    </section>
  </div>
</template>
