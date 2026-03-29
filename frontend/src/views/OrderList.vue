<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useOrdersStore } from '@/stores/orders'
import { useAuthStore } from '@/stores/auth'
import { formatCount, formatPrice, formatShortDate } from '@/utils/display'
import {
  ORDER_STATUS_OPTIONS,
  getOrderStatusBadgeClass,
  getOrderStatusLabel,
} from '@/utils/order'

const router = useRouter()
const ordersStore = useOrdersStore()
const authStore = useAuthStore()

const searchGame = ref('')
const selectedStatus = ref('')

const orders = computed(() => ordersStore.orders)
const loading = computed(() => ordersStore.loading)
const storeError = computed(() => ordersStore.error)
const pagination = computed(() => ordersStore.pagination)
const isBooster = computed(() => authStore.isBooster)
const currentUserId = computed(() => authStore.user?.id ?? null)

const quickGames = ['王者荣耀', '英雄联盟', '和平精英', '原神', '永劫无间', '穿越火线']

const summaryStats = computed(() => [
  {
    label: '当前页订单',
    value: formatCount(orders.value.length),
    hint: pagination.value.total ? `总计 ${formatCount(pagination.value.total)} 条筛选结果` : '按筛选条件实时刷新',
  },
  {
    label: '待接单',
    value: formatCount(orders.value.filter((item) => item.status === 'PENDING').length),
    hint: isBooster.value ? '适合优先抢单' : '等待代练师响应',
  },
  {
    label: '进行中',
    value: formatCount(orders.value.filter((item) => item.status === 'LOCKED').length),
    hint: '持续跟踪进度与沟通状态',
  },
  {
    label: '已完成',
    value: formatCount(orders.value.filter((item) => item.status === 'COMPLETED').length),
    hint: '用于回看历史服务表现',
  },
])

const pageHeading = computed(() => {
  return isBooster.value ? '浏览最新需求，挑选你最擅长的上分订单' : '集中查看你的上分、代肝和陪练订单进度'
})

const pageDescription = computed(() => {
  return isBooster.value
    ? '按游戏、状态和报价快速筛选，先看清订单内容，再决定是否接单。'
    : '无论是王者冲星、LOL 补分还是原神代肝，订单状态、报价和进度都能在这里集中查看。'
})

const displayPages = computed(() => {
  const totalPages = pagination.value.pages
  const currentPage = pagination.value.page

  if (totalPages <= 7) {
    return Array.from({ length: totalPages }, (_, index) => ({
      type: 'page',
      value: index + 1,
    }))
  }

  const items = [{ type: 'page', value: 1 }]
  const start = Math.max(2, currentPage - 1)
  const end = Math.min(totalPages - 1, currentPage + 1)

  if (start > 2) {
    items.push({ type: 'ellipsis', value: 'left' })
  }

  for (let page = start; page <= end; page += 1) {
    items.push({ type: 'page', value: page })
  }

  if (end < totalPages - 1) {
    items.push({ type: 'ellipsis', value: 'right' })
  }

  items.push({ type: 'page', value: totalPages })
  return items
})

async function fetchOrders() {
  ordersStore.setFilters({
    gameName: searchGame.value,
    status: selectedStatus.value,
  })
  await ordersStore.fetchOrders()
}

function handleSearch() {
  ordersStore.setPage(1)
  fetchOrders()
}

function handleStatusChange() {
  ordersStore.setPage(1)
  fetchOrders()
}

function handlePageChange(page) {
  if (page < 1 || page > pagination.value.pages || page === pagination.value.page) {
    return
  }

  ordersStore.setPage(page)
  fetchOrders()
}

function applyQuickGame(game) {
  searchGame.value = game
}

function resetFilters() {
  const searchWasEmpty = searchGame.value === ''
  searchGame.value = ''
  selectedStatus.value = ''
  ordersStore.setPage(1)

  if (searchWasEmpty) {
    fetchOrders()
  }
}

function goToOrder(orderId) {
  router.push(`/orders/${orderId}`)
}

function summarizeText(text) {
  if (!text) {
    return '暂无详细需求描述，点击详情可查看完整订单信息。'
  }

  return text.length > 58 ? `${text.slice(0, 58)}...` : text
}

async function handleAcceptOrder(orderId, event) {
  event.stopPropagation()

  const result = await ordersStore.acceptOrder(orderId)
  if (!result.success) {
    alert(result.error)
  }
}

let searchTimeout = null

watch(searchGame, () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    ordersStore.setPage(1)
    fetchOrders()
  }, 350)
})

onMounted(() => {
  fetchOrders()
})

onUnmounted(() => {
  clearTimeout(searchTimeout)
})
</script>

<template>
  <div class="page-shell space-y-8">
    <section class="hero-panel p-6 sm:p-8 lg:p-10">
      <div class="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
        <div class="space-y-4">
          <p class="eyebrow">订单总览</p>
          <h1 class="section-title !text-4xl sm:!text-5xl">
            {{ pageHeading }}
          </h1>
          <p class="section-copy max-w-3xl">
            {{ pageDescription }}
          </p>
        </div>

        <router-link
          v-if="!isBooster"
          to="/orders/create"
          class="btn-primary px-6 py-3"
        >
          发布新订单
        </router-link>
      </div>

      <div class="mt-8 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <article
          v-for="item in summaryStats"
          :key="item.label"
          class="stat-card"
        >
          <p class="text-3xl font-semibold text-white">{{ item.value }}</p>
          <p class="mt-2 text-sm font-medium text-slate-200">{{ item.label }}</p>
          <p class="mt-2 text-xs leading-6 text-slate-400">{{ item.hint }}</p>
        </article>
      </div>
    </section>

    <section class="surface-card p-5 sm:p-6">
      <div class="flex flex-col gap-4 lg:flex-row lg:items-center">
        <div class="flex-1">
          <label for="order-search" class="label">搜索游戏名称</label>
          <input
            id="order-search"
            v-model="searchGame"
            type="text"
            class="input"
            placeholder="例如：王者荣耀、英雄联盟"
          />
        </div>

        <div class="lg:w-56">
          <label for="order-status" class="label">订单状态</label>
          <select
            id="order-status"
            v-model="selectedStatus"
            class="input"
            @change="handleStatusChange"
          >
            <option
              v-for="option in ORDER_STATUS_OPTIONS"
              :key="option.value"
              :value="option.value"
            >
              {{ option.label }}
            </option>
          </select>
        </div>

        <div class="flex gap-3 lg:self-end">
          <button class="btn-secondary px-5 py-3" @click="handleSearch">立即筛选</button>
          <button class="btn-ghost px-5 py-3" @click="resetFilters">重置</button>
        </div>
      </div>

      <div class="mt-4 flex flex-wrap gap-2">
        <button
          v-for="game in quickGames"
          :key="game"
          type="button"
          class="tag hover:border-primary-300/40 hover:text-white"
          @click="applyQuickGame(game)"
        >
          {{ game }}
        </button>
      </div>
    </section>

    <div v-if="storeError" class="message-error">
      {{ storeError }}
    </div>

    <div v-if="loading" class="surface-card flex items-center justify-center py-20">
      <svg class="h-10 w-10 animate-spin text-primary-300" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
      </svg>
    </div>

    <section v-else-if="!orders.length" class="empty-panel">
      <h2 class="text-2xl font-semibold text-white">当前没有符合条件的订单</h2>
      <p class="mx-auto mt-3 max-w-2xl text-sm leading-7 text-slate-400">
        {{ isBooster ? '可以尝试切换状态筛选，或稍后再回来查看新的接单机会。' : '你还没有发布订单，现在就可以创建一个更完整、更可追踪的代练需求。' }}
      </p>
      <router-link
        v-if="!isBooster"
        to="/orders/create"
        class="btn-primary mt-8 px-6 py-3"
      >
        发布第一个订单
      </router-link>
    </section>

    <section v-else class="grid gap-5 xl:grid-cols-2">
      <article
        v-for="order in orders"
        :key="order.id"
        class="card-hover cursor-pointer"
        @click="goToOrder(order.id)"
      >
        <div class="flex items-start justify-between gap-4">
          <div>
            <div class="flex flex-wrap items-center gap-2">
              <span class="tag">{{ order.game_name }}</span>
              <span class="text-xs uppercase tracking-[0.18em] text-slate-500">#{{ order.id }}</span>
            </div>
            <h2 class="mt-5 text-2xl font-semibold text-white">
              {{ order.current_rank }}
              <span class="mx-2 text-primary-300">→</span>
              {{ order.target_rank }}
            </h2>
          </div>
          <span :class="getOrderStatusBadgeClass(order.status)">
            {{ getOrderStatusLabel(order.status) }}
          </span>
        </div>

        <p class="mt-4 text-sm leading-7 text-slate-400">
          {{ summarizeText(order.description_raw) }}
        </p>

        <div class="mt-5 grid gap-3 sm:grid-cols-2">
          <div class="rounded-2xl border border-white/10 bg-white/5 p-4">
            <p class="text-xs uppercase tracking-[0.18em] text-slate-500">发布用户</p>
            <p class="mt-2 text-sm font-medium text-white">{{ order.user?.username || '未公开' }}</p>
          </div>
          <div class="rounded-2xl border border-white/10 bg-white/5 p-4">
            <p class="text-xs uppercase tracking-[0.18em] text-slate-500">创建时间</p>
            <p class="mt-2 text-sm font-medium text-white">{{ formatShortDate(order.created_at) }}</p>
          </div>
        </div>

        <div class="mt-5 flex flex-col gap-4 border-t border-white/10 pt-5 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p class="text-xs uppercase tracking-[0.18em] text-slate-500">报价</p>
            <p class="mt-1 text-3xl font-semibold text-accent-300">{{ formatPrice(order.price) }}</p>
          </div>

          <div class="flex flex-wrap gap-2">
            <button
              v-if="isBooster && order.status === 'PENDING' && order.user_id !== currentUserId"
              class="btn-primary !px-4 !py-2"
              @click="handleAcceptOrder(order.id, $event)"
            >
              立即接单
            </button>
            <button
              class="btn-secondary !px-4 !py-2"
              @click.stop="goToOrder(order.id)"
            >
              查看详情
            </button>
          </div>
        </div>
      </article>
    </section>

    <section
      v-if="pagination.pages > 1"
      class="surface-card p-5"
    >
      <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <p class="text-sm text-slate-400">
          共 {{ formatCount(pagination.total) }} 条订单，当前第 {{ pagination.page }} / {{ pagination.pages }} 页
        </p>

        <div class="flex items-center gap-2">
          <button
            class="btn-secondary !px-4 !py-2"
            :disabled="pagination.page <= 1"
            @click="handlePageChange(pagination.page - 1)"
          >
            上一页
          </button>

          <template v-for="item in displayPages" :key="`${item.type}-${item.value}`">
            <button
              v-if="item.type === 'page'"
              class="h-10 min-w-10 rounded-full px-3 text-sm font-medium transition-colors"
              :class="item.value === pagination.page ? 'bg-primary-300 text-slate-950' : 'bg-white/5 text-slate-300 hover:bg-white/10 hover:text-white'"
              @click="handlePageChange(item.value)"
            >
              {{ item.value }}
            </button>
            <span
              v-else
              class="px-2 text-sm text-slate-500"
            >
              ...
            </span>
          </template>

          <button
            class="btn-secondary !px-4 !py-2"
            :disabled="pagination.page >= pagination.pages"
            @click="handlePageChange(pagination.page + 1)"
          >
            下一页
          </button>
        </div>
      </div>
    </section>
  </div>
</template>
