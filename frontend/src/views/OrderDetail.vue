<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import { useAuthStore } from '@/stores/auth'
import { useChatStore } from '@/stores/chat'
import { useOrdersStore } from '@/stores/orders'
import { getGameImage } from '@/data/gameImages'
import api from '@/utils/api'
import { formatDateTime, formatPrice } from '@/utils/display'
import { getOrderStatusBadgeClass, getOrderStatusLabel, getOrderStatusMeta, getHumanStatusLabel, getHumanStatusSubtitle } from '@/utils/order'

const props = defineProps({
  id: {
    type: [String, Number],
    required: true,
  },
})

const router = useRouter()
const authStore = useAuthStore()
const chatStore = useChatStore()
const ordersStore = useOrdersStore()

const errorMessage = ref('')
const successMessage = ref('')
const actionLoading = ref(false)
const chatLoading = ref(false)
const reviews = ref([])
const reviewForm = ref({ rating: 5, content: '' })
const editingReview = ref(false)
const confirmSuccess = ref(false)

const order = computed(() => ordersStore.currentOrder)
const loading = computed(() => ordersStore.loading)
const currentUser = computed(() => authStore.user)
const isBooster = computed(() => authStore.isBooster)
const isAdmin = computed(() => authStore.isAdmin)
const isOwner = computed(() => order.value?.user_id === currentUser.value?.id)
const isAssignedBooster = computed(() => order.value?.booster_id === currentUser.value?.id)
const chatTargetUserId = computed(() => {
  if (!order.value || !currentUser.value) {
    return null
  }
  if (isOwner.value) {
    return order.value.booster_id || null
  }
  if (isAssignedBooster.value) {
    return order.value.user_id || null
  }
  // 代练在 PENDING 状态下也可以和老板聊（接单前沟通）
  if (isBooster.value && !isOwner.value && order.value.status === 'PENDING') {
    return order.value.user_id || null
  }
  return null
})
const canStartChat = computed(() => chatTargetUserId.value != null)
const statusMeta = computed(() => getOrderStatusMeta(order.value?.status))
const viewRole = computed(() => isAssignedBooster.value || (isBooster.value && !isOwner.value) ? 'booster' : 'owner')
const humanStatusLabel = computed(() => getHumanStatusLabel(order.value?.status, order.value?.service_type, viewRole.value))
const humanStatusSubtitle = computed(() => getHumanStatusSubtitle(order.value?.status, order.value?.service_type, viewRole.value))
const isPending = computed(() => order.value?.status === 'PENDING')
const isLocked = computed(() => order.value?.status === 'LOCKED')
const isDelivered = computed(() => order.value?.status === 'DELIVERED')
const isBoostOrder = computed(() => order.value?.service_type === '代练')
const heroStyle = computed(() => {
  const visual = getGameImage(order.value?.game_name)
  return {
    backgroundImage: visual.hero
      ? `linear-gradient(115deg, rgba(10,10,15,0.94), rgba(18,18,26,0.82)), url('${visual.hero}')`
      : 'linear-gradient(135deg, rgba(10,10,15,0.96), rgba(18,18,26,0.88))',
    backgroundPosition: 'center',
    backgroundSize: 'cover',
  }
})

const detailCards = computed(() => {
  if (!order.value) {
    return []
  }

  return [
    { icon: 'S', label: '服务', value: order.value.service_type || '未指定' },
    { icon: 'R', label: '区服', value: order.value.server || '未指定' },
    { icon: '$', label: '金额', value: formatPrice(order.value.price) },
    { icon: 'T', label: '发布时间', value: formatDateTime(order.value.created_at) },
  ]
})

const timeline = computed(() => {
  if (!order.value) {
    return []
  }

  return [
    { title: '需求已发出', time: formatDateTime(order.value.created_at), active: true },
    {
      title: isBoostOrder.value ? '代练已接单' : '陪玩已接单',
      time: order.value.locked_at ? formatDateTime(order.value.locked_at) : '等待中…',
      active: ['LOCKED', 'DELIVERED', 'COMPLETED', 'DISPUTED'].includes(order.value.status),
    },
    {
      title: isBoostOrder.value ? '代练已提交完成' : '陪玩已结束',
      time: order.value.delivered_at ? formatDateTime(order.value.delivered_at) : '未提交',
      active: ['DELIVERED', 'COMPLETED'].includes(order.value.status),
    },
    {
      title: '客户已确认',
      time: order.value.completed_at ? formatDateTime(order.value.completed_at) : '待确认',
      active: order.value.status === 'COMPLETED',
    },
  ]
})

const canReview = computed(() => {
  if (!order.value || !currentUser.value) {
    return false
  }
  return order.value.user_id === currentUser.value.id || order.value.booster_id === currentUser.value.id
})

const hasReviewed = computed(() => {
  return reviews.value.some((review) => review.reviewer_id === currentUser.value?.id)
})

function compactSummary() {
  const detail = order.value?.ai_tags?.detail || {}
  const requirements = Array.isArray(detail.requirements) ? detail.requirements.filter(Boolean) : []
  const items = [
    detail.role,
    requirements[0],
    order.value?.description_raw,
  ].filter(Boolean)

  const summary = items[0] || '未补充需求'
  return summary.length > 36 ? `${summary.slice(0, 36)}...` : summary
}

function paymentLabel(paymentStatus) {
  if (paymentStatus === 'PAID') {
    return '已支付'
  }
  if (paymentStatus === 'REFUNDED') {
    return '已退款'
  }
  return '待支付'
}

function paymentBadgeClass(paymentStatus) {
  return {
    tag: true,
    '!bg-yellow-500/20 !text-yellow-300 !border-yellow-500/30': paymentStatus === 'UNPAID',
    '!bg-green-500/20 !text-green-300 !border-green-500/30': paymentStatus === 'PAID',
    '!bg-slate-500/20 !text-slate-300 !border-slate-500/30': paymentStatus === 'REFUNDED',
  }
}

async function handleAccept() {
  actionLoading.value = true
  errorMessage.value = ''
  successMessage.value = ''
  const result = await ordersStore.acceptOrder(order.value.id)
  if (result.success) {
    successMessage.value = '接下来了，准备开冲'
  } else {
    errorMessage.value = result.error
  }
  actionLoading.value = false
}

async function handleDeliver() {
  actionLoading.value = true
  errorMessage.value = ''
  successMessage.value = ''
  const result = await ordersStore.deliverOrder(order.value.id)
  if (result.success) {
    successMessage.value = '已提交完成，等待老板确认'
  } else {
    errorMessage.value = result.error
  }
  actionLoading.value = false
}

async function handleConfirm() {
  actionLoading.value = true
  errorMessage.value = ''
  successMessage.value = ''
  const result = await ordersStore.confirmOrder(order.value.id)
  if (result.success) {
    successMessage.value = '已确认完成！'
    confirmSuccess.value = true
    window.setTimeout(() => { confirmSuccess.value = false }, 1500)
    await fetchReviews()
  } else {
    errorMessage.value = result.error
  }
  actionLoading.value = false
}

async function handleDispute() {
  const reason = window.prompt('请输入争议原因（可选）：')
  if (reason === null) {
    return
  }
  actionLoading.value = true
  errorMessage.value = ''
  successMessage.value = ''
  const result = await ordersStore.disputeOrder(order.value.id, reason)
  if (result.success) {
    successMessage.value = '已发起争议，平台将介入处理'
  } else {
    errorMessage.value = result.error
  }
  actionLoading.value = false
}

async function handleCancel() {
  if (!window.confirm('确定取消这条订单吗？')) {
    return
  }
  actionLoading.value = true
  errorMessage.value = ''
  successMessage.value = ''
  const result = await ordersStore.cancelOrder(order.value.id)
  if (result.success) {
    successMessage.value = '已取消'
  } else {
    errorMessage.value = result.error
  }
  actionLoading.value = false
}

async function handlePay() {
  actionLoading.value = true
  errorMessage.value = ''
  successMessage.value = ''
  const result = await ordersStore.payOrder(order.value.id)
  if (result.success) {
    successMessage.value = '支付成功'
  } else {
    errorMessage.value = result.error
  }
  actionLoading.value = false
}

async function handleRefund() {
  actionLoading.value = true
  errorMessage.value = ''
  successMessage.value = ''
  const result = await ordersStore.refundOrder(order.value.id)
  if (result.success) {
    successMessage.value = '退款成功'
  } else {
    errorMessage.value = result.error
  }
  actionLoading.value = false
}

async function handleStartConversation() {
  if (!chatTargetUserId.value) {
    return
  }

  chatLoading.value = true
  errorMessage.value = ''
  const result = await chatStore.startConversation(chatTargetUserId.value, order.value.id)
  if (result.success) {
    router.push({ name: 'chat-detail', params: { id: result.data.id } })
  } else {
    errorMessage.value = result.error
  }
  chatLoading.value = false
}

async function fetchReviews() {
  if (!order.value || order.value.status !== 'COMPLETED') {
    reviews.value = []
    return
  }

  try {
    const resp = await api.get(`/orders/${order.value.id}/reviews`)
    reviews.value = resp.data.items || []
  } catch {
    reviews.value = []
  }
}

function startEditReview(review) {
  reviewForm.value = { rating: review.rating, content: review.content || '' }
  editingReview.value = true
}

async function submitReview() {
  errorMessage.value = ''
  successMessage.value = ''
  const isEditing = editingReview.value

  try {
    if (isEditing) {
      await api.put(`/orders/${order.value.id}/reviews`, reviewForm.value)
    } else {
      await api.post(`/orders/${order.value.id}/reviews`, reviewForm.value)
    }
    editingReview.value = false
    reviewForm.value = { rating: 5, content: '' }
    successMessage.value = isEditing ? '评价更新了' : isAssignedBooster.value ? '评价已提交' : '谢谢，你的反馈会帮助更多人找到靠谱的代练'
    await fetchReviews()
  } catch (err) {
    errorMessage.value = err.message || '评价失败'
  }
}

onMounted(async () => {
  const result = await ordersStore.fetchOrder(props.id)
  if (result.success) {
    await fetchReviews()
  }
})
</script>

<template>
  <div class="page-shell space-y-6">
    <button class="btn-ghost self-start !px-0 text-sm" @click="router.back()">返回</button>

    <div v-if="loading" class="surface-card flex items-center justify-center py-20">
      <svg class="h-10 w-10 animate-spin text-primary-300" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
      </svg>
    </div>

    <template v-else-if="order">
      <div v-if="errorMessage" class="message-error">{{ errorMessage }}</div>
      <div v-if="successMessage" class="message-success">{{ successMessage }}</div>

      <section class="hero-panel scanline-overlay p-6 sm:p-8 lg:p-10" :style="heroStyle">
        <div class="absolute inset-0 bg-gradient-to-r from-slate-950/92 via-slate-950/82 to-slate-950/64"></div>

        <div class="relative z-10 flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
          <div class="space-y-4">
            <div class="flex flex-wrap items-center gap-3">
              <span class="tag">{{ order.game_name }}</span>
              <span :class="getOrderStatusBadgeClass(order.status)">{{ humanStatusLabel }}</span>
              <span v-if="order.payment_status" :class="paymentBadgeClass(order.payment_status)">
                {{ paymentLabel(order.payment_status) }}
              </span>
            </div>
            <p v-if="humanStatusSubtitle" class="mt-2 text-sm text-slate-400">{{ humanStatusSubtitle }}</p>
            <h1 class="section-title neon-text !text-4xl sm:!text-5xl">{{ order.current_rank }} -> {{ order.target_rank }}</h1>
            <p class="text-sm text-slate-300">{{ compactSummary() }}</p>
          </div>

          <div class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <article
              v-for="item in detailCards"
              :key="item.label"
              class="stat-card flex items-center gap-4"
            >
              <div class="flex h-11 w-11 items-center justify-center rounded-[18px] border border-primary-300/35 bg-primary-500/10 text-lg font-semibold text-primary-100">
                {{ item.icon }}
              </div>
              <div>
                <p class="text-xs uppercase tracking-[0.18em] text-slate-500">{{ item.label }}</p>
                <p class="mt-2 text-sm font-medium text-white">{{ item.value }}</p>
              </div>
            </article>
          </div>
        </div>
      </section>

      <div class="grid gap-6 xl:grid-cols-[1.02fr_0.98fr]">
        <section class="space-y-6">
          <article class="surface-card p-6 sm:p-8" :class="{ 'shimmer-pending': isPending }">
            <h2 class="text-2xl font-semibold text-white">时间线</h2>
            <div class="mt-6 space-y-4">
              <div v-for="(item, index) in timeline" :key="item.title" class="flex gap-4">
                <div class="flex flex-col items-center">
                  <div
                    class="flex h-10 w-10 items-center justify-center rounded-2xl border text-sm font-semibold"
                    :class="item.active ? 'text-cyan-100' : 'text-slate-400'"
                    :style="item.active
                      ? 'border-color: rgba(0, 240, 255, 0.5); background: rgba(0, 240, 255, 0.08); box-shadow: 0 0 8px rgba(0, 240, 255, 0.3);'
                      : 'border-color: rgba(148, 163, 184, 0.18); background: rgba(15, 23, 42, 0.45);'"
                  >
                    {{ index + 1 }}
                  </div>
                  <div
                    v-if="index !== timeline.length - 1"
                    class="mt-2 h-12 w-px rounded-full"
                    :style="item.active
                      ? 'background: linear-gradient(180deg, #00f0ff, #b829dd);'
                      : 'background: rgba(255, 255, 255, 0.08);'"
                  ></div>
                </div>
                <div class="flex-1 rounded-3xl border border-white/10 bg-white/5 p-4">
                  <p class="text-sm font-semibold text-white">{{ item.title }}</p>
                  <p class="mt-2 text-sm text-slate-400">{{ item.time }}</p>
                </div>
              </div>
            </div>
          </article>

          <article class="surface-card p-6 sm:p-8">
            <h2 class="text-2xl font-semibold text-white">关键信息</h2>
            <div class="mt-6 grid gap-4 sm:grid-cols-2">
              <div class="rounded-3xl border border-white/10 bg-white/5 p-4">
                <p class="text-xs uppercase tracking-[0.18em] text-slate-500">需求</p>
                <p class="mt-2 text-sm font-medium text-white">{{ order.description_raw || '未补充' }}</p>
              </div>
              <div class="rounded-3xl border border-white/10 bg-white/5 p-4">
                <p class="text-xs uppercase tracking-[0.18em] text-slate-500">备注</p>
                <p class="mt-2 text-sm font-medium text-white">{{ order.notes || '无' }}</p>
              </div>
              <div class="rounded-3xl border border-white/10 bg-white/5 p-4">
                <p class="text-xs uppercase tracking-[0.18em] text-slate-500">用户</p>
                <p class="mt-2 text-sm font-medium text-white">{{ order.user?.username || '未公开' }}</p>
              </div>
              <div class="rounded-3xl border border-white/10 bg-white/5 p-4">
                <p class="text-xs uppercase tracking-[0.18em] text-slate-500">代练</p>
                <p v-if="order.booster" class="mt-2 text-sm font-medium">
                  <router-link
                    :to="{ name: 'booster-profile', params: { id: order.booster_id } }"
                    class="text-primary-200 underline-offset-4 hover:underline"
                  >{{ order.booster.username }}</router-link>
                </p>
                <p v-else class="mt-2 text-sm font-medium text-white">待接单</p>
              </div>
            </div>
          </article>
        </section>

        <aside class="surface-card p-6 sm:p-8">
          <div class="flex items-center justify-between gap-4">
            <h2 class="text-2xl font-semibold text-white">操作</h2>
            <span class="text-sm text-slate-400">{{ statusMeta.label }}</span>
          </div>

          <div class="mt-6 flex flex-col gap-3">
            <!-- 代练接单：PENDING 状态，代练可见 -->
            <button
              v-if="isBooster && order.status === 'PENDING' && !isOwner"
              class="btn-primary py-3"
              :disabled="actionLoading"
              @click="handleAccept"
            >
              接单
            </button>

            <!-- 代练提交完成：LOCKED 状态，接单代练可见 -->
            <button
              v-if="isAssignedBooster && order.status === 'LOCKED'"
              class="btn-success py-3"
              :disabled="actionLoading"
              @click="handleDeliver"
            >
              提交完成
            </button>

            <!-- LOCKED 状态提示：客户不要登号 -->
            <p v-if="isLocked && isBoostOrder && isOwner" class="rounded-2xl border border-yellow-500/30 bg-yellow-500/10 px-4 py-3 text-xs leading-6 text-yellow-200">
              代练正在你的账号上操作，请勿登录账号，避免影响进度。
            </p>

            <!-- DELIVERED 状态提示：代练等待确认 -->
            <p v-if="isDelivered && isAssignedBooster" class="rounded-2xl border border-cyan-500/30 bg-cyan-500/10 px-4 py-3 text-xs leading-6 text-cyan-200">
              已提交完成，等待老板确认中。如超过 72 小时未确认，系统将自动完成。
            </p>

            <!-- 客户确认完成：DELIVERED 状态，下单用户可见 -->
            <button
              v-if="isOwner && order.status === 'DELIVERED'"
              class="btn-success py-3"
              :class="{ 'btn-confirm-success': confirmSuccess }"
              :disabled="actionLoading"
              @click="handleConfirm"
            >
              确认完成
            </button>

            <!-- DELIVERED 状态提示：客户核查 -->
            <p v-if="isDelivered && isOwner" class="rounded-2xl border border-yellow-500/30 bg-yellow-500/10 px-4 py-3 text-xs leading-6 text-yellow-200">
              代练已提交完成，请核实结果。如有问题可发起争议。72 小时后将自动确认。
            </p>

            <!-- 发起争议：LOCKED / DELIVERED 状态，双方可见 -->
            <button
              v-if="(isOwner || isAssignedBooster) && ['LOCKED', 'DELIVERED'].includes(order.status)"
              class="btn-danger py-3"
              :disabled="actionLoading"
              @click="handleDispute"
            >
              发起争议
            </button>

            <!-- 取消订单：PENDING 状态，客户可见 -->
            <button
              v-if="isOwner && order.status === 'PENDING'"
              class="btn-danger py-3"
              :disabled="actionLoading"
              @click="handleCancel"
            >
              取消
            </button>

            <!-- 支付按钮 -->
            <button
              v-if="order.payment_status === 'UNPAID' && order.user_id === currentUser?.id"
              type="button"
              class="btn-primary py-3"
              :disabled="actionLoading"
              @click="handlePay"
            >
              确认支付
            </button>

            <!-- 退款按钮：管理员可见 -->
            <button
              v-if="order.payment_status === 'PAID' && isAdmin && ['CANCELLED', 'DISPUTED'].includes(order.status)"
              type="button"
              class="btn-secondary py-3"
              :disabled="actionLoading"
              @click="handleRefund"
            >
              退款
            </button>

            <!-- 联系对方 -->
            <button
              v-if="canStartChat"
              class="btn-secondary py-3"
              :disabled="chatLoading"
              @click="handleStartConversation"
            >
              {{ chatLoading ? '打开中...' : (isOwner ? '联系代练' : '联系老板') }}
            </button>

            <button class="btn-secondary py-3" @click="router.push({ name: 'orders' })">返回列表</button>
          </div>
        </aside>
      </div>

      <section v-if="order.status === 'COMPLETED'" class="surface-card space-y-4 p-6 sm:p-8">
        <h3 class="section-title !text-2xl">{{ isAssignedBooster ? '给老板留个评价' : '说说这次体验' }}</h3>

        <div v-for="review in reviews" :key="review.id" class="stat-card">
          <div class="flex items-center justify-between gap-3">
            <span class="text-sm text-slate-400">{{ review.reviewer?.username }}</span>
            <span class="text-yellow-400">{{ '★'.repeat(review.rating) }}{{ '☆'.repeat(5 - review.rating) }}</span>
          </div>
          <p v-if="review.content" class="mt-2 text-sm text-slate-300">{{ review.content }}</p>
          <button
            v-if="review.reviewer_id === currentUser?.id"
            type="button"
            class="btn-ghost mt-2 !px-3 !py-1 !text-xs"
            @click="startEditReview(review)"
          >
            修改
          </button>
        </div>

        <div v-if="(canReview && !hasReviewed) || editingReview" class="stat-card space-y-3">
          <p class="text-xs uppercase tracking-[0.24em] text-slate-500">
            {{ editingReview ? '修改评价' : '写评价' }}
          </p>
          <div class="flex gap-1">
            <button
              v-for="star in 5"
              :key="star"
              type="button"
              class="text-2xl"
              :class="star <= reviewForm.rating ? 'text-yellow-400' : 'text-slate-600'"
              @click="reviewForm.rating = star"
            >
              ★
            </button>
          </div>
          <textarea
            v-model="reviewForm.content"
            class="home-search-input !min-h-[80px]"
            :placeholder="isAssignedBooster ? '老板好配合吗？沟通顺畅吗？' : '打法怎么样？服务态度好不好？达到你的预期了吗？'"
          ></textarea>
          <div class="flex gap-2">
            <button type="button" class="btn-primary !px-4 !py-2" @click="submitReview">
              {{ editingReview ? '保存修改' : '说说这次体验' }}
            </button>
            <button v-if="editingReview" type="button" class="btn-ghost !px-4 !py-2" @click="editingReview = false">
              取消
            </button>
          </div>
        </div>
      </section>
    </template>

    <section v-else class="empty-panel">
      <h2 class="text-2xl font-semibold text-white">订单不存在</h2>
    </section>
  </div>
</template>
