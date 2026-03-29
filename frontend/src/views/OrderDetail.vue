<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useOrdersStore } from '@/stores/orders'
import { useAuthStore } from '@/stores/auth'
import { formatDateTime, formatPrice } from '@/utils/display'
import { getOrderStatusBadgeClass, getOrderStatusLabel, getOrderStatusMeta } from '@/utils/order'

const props = defineProps({
  id: {
    type: [String, Number],
    required: true,
  },
})

const router = useRouter()
const ordersStore = useOrdersStore()
const authStore = useAuthStore()

const errorMessage = ref('')
const successMessage = ref('')
const actionLoading = ref(false)

const order = computed(() => ordersStore.currentOrder)
const loading = computed(() => ordersStore.loading)
const currentUser = computed(() => authStore.user)
const isBooster = computed(() => authStore.isBooster)
const isOwner = computed(() => order.value?.user_id === currentUser.value?.id)
const isAssignedBooster = computed(() => order.value?.booster_id === currentUser.value?.id)
const statusMeta = computed(() => getOrderStatusMeta(order.value?.status))

const timeline = computed(() => {
  if (!order.value) {
    return []
  }

  return [
    {
      title: '订单发布',
      time: formatDateTime(order.value.created_at),
      active: true,
    },
    {
      title: '代练接单',
      time: order.value.locked_at ? formatDateTime(order.value.locked_at) : '待接单',
      active: ['LOCKED', 'COMPLETED', 'DISPUTED'].includes(order.value.status),
    },
    {
      title: '订单完成',
      time: order.value.completed_at ? formatDateTime(order.value.completed_at) : '尚未完成',
      active: order.value.status === 'COMPLETED',
    },
  ]
})

const detailItems = computed(() => {
  if (!order.value) {
    return []
  }

  return [
    { label: '订单编号', value: `#${order.value.id}` },
    { label: '创建时间', value: formatDateTime(order.value.created_at) },
    { label: '最近更新', value: formatDateTime(order.value.updated_at) },
    { label: '优先级', value: `${order.value.priority ?? 0}` },
    { label: '游戏账号', value: order.value.game_account || '未填写' },
  ]
})

const actionHint = computed(() => {
  if (!order.value) {
    return '订单不存在或你暂时没有访问权限。'
  }

  if (isAssignedBooster.value && order.value.status === 'LOCKED') {
    return '你已接下此单，完成服务后可在这里提交完成状态。'
  }

  if (isBooster.value && order.value.status === 'PENDING' && !isOwner.value) {
    return '这是一个可接订单，确认时间和要求合适后即可接单。'
  }

  if (isOwner.value && order.value.status === 'PENDING') {
    return '订单尚未被接走，如需调整可取消后重新发布。'
  }

  return statusMeta.value.description
})

async function handleAccept() {
  actionLoading.value = true
  errorMessage.value = ''
  successMessage.value = ''

  const result = await ordersStore.acceptOrder(order.value.id)
  if (result.success) {
    successMessage.value = '接单成功，订单已进入进行中状态。'
  } else {
    errorMessage.value = result.error
  }

  actionLoading.value = false
}

async function handleComplete() {
  actionLoading.value = true
  errorMessage.value = ''
  successMessage.value = ''

  const result = await ordersStore.completeOrder(order.value.id)
  if (result.success) {
    successMessage.value = '订单已标记为完成。'
  } else {
    errorMessage.value = result.error
  }

  actionLoading.value = false
}

async function handleCancel() {
  if (!confirm('确定要取消此订单吗？')) {
    return
  }

  actionLoading.value = true
  errorMessage.value = ''
  successMessage.value = ''

  const result = await ordersStore.cancelOrder(order.value.id)
  if (result.success) {
    successMessage.value = '订单已取消。'
  } else {
    errorMessage.value = result.error
  }

  actionLoading.value = false
}

onMounted(() => {
  ordersStore.fetchOrder(props.id)
})
</script>

<template>
  <div class="page-shell space-y-6">
    <button class="btn-ghost self-start !px-0 text-sm" @click="router.back()">
      返回订单列表
    </button>

    <div v-if="loading" class="surface-card flex items-center justify-center py-20">
      <svg class="h-10 w-10 animate-spin text-primary-300" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
      </svg>
    </div>

    <div v-else-if="order" class="space-y-6">
      <div v-if="errorMessage" class="message-error">
        {{ errorMessage }}
      </div>
      <div v-if="successMessage" class="message-success">
        {{ successMessage }}
      </div>

      <section class="hero-panel p-6 sm:p-8 lg:p-10">
        <div class="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
          <div class="space-y-4">
            <div class="flex flex-wrap items-center gap-3">
              <span class="tag">{{ order.game_name }}</span>
              <span :class="getOrderStatusBadgeClass(order.status)">
                {{ getOrderStatusLabel(order.status) }}
              </span>
            </div>
            <h1 class="section-title !text-4xl sm:!text-5xl">
              {{ order.current_rank }}
              <span class="mx-3 text-primary-300">→</span>
              {{ order.target_rank }}
            </h1>
            <p class="section-copy max-w-3xl">
              {{ statusMeta.description }}
            </p>
          </div>

          <div class="grid gap-4 sm:grid-cols-3 lg:grid-cols-1">
            <div class="stat-card">
              <p class="text-sm text-slate-400">订单金额</p>
              <p class="mt-2 text-3xl font-semibold text-accent-300">{{ formatPrice(order.price) }}</p>
            </div>
            <div class="stat-card">
              <p class="text-sm text-slate-400">发布用户</p>
              <p class="mt-2 text-lg font-semibold text-white">{{ order.user?.username || '未公开' }}</p>
            </div>
            <div class="stat-card">
              <p class="text-sm text-slate-400">当前代练师</p>
              <p class="mt-2 text-lg font-semibold text-white">{{ order.booster?.username || '尚未接单' }}</p>
            </div>
          </div>
        </div>
      </section>

      <div class="grid gap-6 xl:grid-cols-[1.02fr_0.98fr]">
        <section class="space-y-6">
          <article class="surface-card p-6 sm:p-8">
            <h2 class="text-2xl font-semibold text-white">订单详情</h2>

            <div class="mt-6 grid gap-4 sm:grid-cols-2">
              <div
                v-for="item in detailItems"
                :key="item.label"
                class="rounded-3xl border border-white/10 bg-white/5 p-4"
              >
                <p class="text-xs uppercase tracking-[0.18em] text-slate-500">{{ item.label }}</p>
                <p class="mt-2 text-sm font-medium text-white">{{ item.value }}</p>
              </div>
            </div>

            <div class="mt-6 space-y-4">
              <div class="rounded-3xl border border-white/10 bg-white/5 p-5">
                <p class="text-sm font-medium text-primary-100">需求描述</p>
                <p class="mt-3 text-sm leading-7 text-slate-300">
                  {{ order.description_raw || '下单时未填写原始需求描述。' }}
                </p>
              </div>

              <div class="rounded-3xl border border-white/10 bg-white/5 p-5">
                <p class="text-sm font-medium text-primary-100">备注说明</p>
                <p class="mt-3 text-sm leading-7 text-slate-300">
                  {{ order.notes || '暂无备注。' }}
                </p>
              </div>
            </div>
          </article>

          <article class="surface-card p-6 sm:p-8">
            <h2 class="text-2xl font-semibold text-white">流程进度</h2>
            <div class="mt-6 space-y-4">
              <div
                v-for="(item, index) in timeline"
                :key="item.title"
                class="flex gap-4"
              >
                <div class="flex flex-col items-center">
                  <div
                    class="flex h-10 w-10 items-center justify-center rounded-2xl text-sm font-semibold"
                    :class="item.active ? 'bg-primary-300 text-slate-950' : 'bg-white/5 text-slate-400'"
                  >
                    {{ index + 1 }}
                  </div>
                  <div v-if="index !== timeline.length - 1" class="mt-2 h-12 w-px bg-white/10"></div>
                </div>
                <div class="rounded-3xl border border-white/10 bg-white/5 p-4 flex-1">
                  <p class="text-sm font-semibold text-white">{{ item.title }}</p>
                  <p class="mt-2 text-sm text-slate-400">{{ item.time }}</p>
                </div>
              </div>
            </div>
          </article>
        </section>

        <aside class="space-y-6">
          <article class="surface-card p-6 sm:p-8">
            <h2 class="text-2xl font-semibold text-white">参与角色</h2>
            <div class="mt-6 space-y-4">
              <div class="rounded-3xl border border-white/10 bg-white/5 p-5">
                <p class="text-sm font-medium text-primary-100">下单用户</p>
                <p class="mt-2 text-lg font-semibold text-white">{{ order.user?.username || '未公开' }}</p>
                <p class="mt-2 text-sm text-slate-400">{{ order.user?.email || '暂无邮箱信息' }}</p>
              </div>
              <div class="rounded-3xl border border-white/10 bg-white/5 p-5">
                <p class="text-sm font-medium text-primary-100">当前代练师</p>
                <p class="mt-2 text-lg font-semibold text-white">{{ order.booster?.username || '尚未接单' }}</p>
                <p class="mt-2 text-sm text-slate-400">{{ order.booster?.email || '接单后显示代练师信息' }}</p>
              </div>
            </div>
          </article>

          <article class="surface-card p-6 sm:p-8">
            <h2 class="text-2xl font-semibold text-white">可执行操作</h2>
            <p class="mt-3 text-sm leading-7 text-slate-400">
              {{ actionHint }}
            </p>

            <div class="mt-6 flex flex-col gap-3">
              <button
                v-if="isBooster && order.status === 'PENDING' && !isOwner"
                class="btn-primary py-3"
                :disabled="actionLoading"
                @click="handleAccept"
              >
                立即接单
              </button>
              <button
                v-if="isAssignedBooster && order.status === 'LOCKED'"
                class="btn-success py-3"
                :disabled="actionLoading"
                @click="handleComplete"
              >
                标记订单完成
              </button>
              <button
                v-if="isOwner && order.status === 'PENDING'"
                class="btn-danger py-3"
                :disabled="actionLoading"
                @click="handleCancel"
              >
                取消当前订单
              </button>
              <button class="btn-secondary py-3" @click="router.push('/orders')">
                返回订单大厅
              </button>
            </div>
          </article>
        </aside>
      </div>
    </div>

    <section v-else class="empty-panel">
      <h2 class="text-2xl font-semibold text-white">订单不存在或暂时无法访问</h2>
      <p class="mx-auto mt-3 max-w-2xl text-sm leading-7 text-slate-400">
        可能是订单已被删除、权限不足，或者页面刷新时请求尚未成功。你可以先返回订单列表重新进入。
      </p>
      <button class="btn-primary mt-8 px-6 py-3" @click="router.push('/orders')">
        返回订单大厅
      </button>
    </section>
  </div>
</template>
