<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import { useNotificationsStore } from '@/stores/notifications'

const router = useRouter()
const store = useNotificationsStore()

const page = ref(1)
const showUnreadOnly = ref(false)

const NOTIFICATION_TYPE_META = {
  ORDER_ACCEPTED: { icon: '📋', label: '接单通知' },
  ORDER_DELIVERED: { icon: '📦', label: '交付通知' },
  ORDER_CONFIRMED: { icon: '✅', label: '完成通知' },
  ORDER_DISPUTED: { icon: '⚠️', label: '争议通知' },
  ORDER_CANCELLED: { icon: '❌', label: '取消通知' },
  NEW_MESSAGE: { icon: '💬', label: '消息通知' },
  APPLICATION_APPROVED: { icon: '🎉', label: '申请通过' },
  APPLICATION_REJECTED: { icon: '😞', label: '申请拒绝' },
  REVIEW_RECEIVED: { icon: '⭐', label: '评价通知' },
  SYSTEM_ANNOUNCEMENT: { icon: '📢', label: '系统公告' },
}

const notifications = computed(() => store.notifications)
const total = computed(() => store.total)
const unreadCount = computed(() => store.unreadCount)
const loading = computed(() => store.loading)
const pageCount = computed(() => Math.ceil(total.value / 20) || 1)

function typeMeta(type) {
  return NOTIFICATION_TYPE_META[type] || { icon: '🔔', label: '通知' }
}

function formatTime(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  const now = new Date()
  const diffMs = now - d
  const diffMin = Math.floor(diffMs / 60000)

  if (diffMin < 1) return '刚刚'
  if (diffMin < 60) return `${diffMin} 分钟前`
  const diffHours = Math.floor(diffMin / 60)
  if (diffHours < 24) return `${diffHours} 小时前`
  const diffDays = Math.floor(diffHours / 24)
  if (diffDays < 7) return `${diffDays} 天前`
  return d.toLocaleDateString('zh-CN')
}

async function loadPage(p = 1) {
  page.value = p
  await store.fetchNotifications({ page: p, unreadOnly: showUnreadOnly.value })
}

async function toggleUnreadFilter() {
  showUnreadOnly.value = !showUnreadOnly.value
  await loadPage(1)
}

async function handleClick(n) {
  if (!n.is_read) {
    await store.markRead(n.id)
  }
  if (n.link) {
    router.push(n.link)
  }
}

async function handleMarkAllRead() {
  await store.markAllRead()
}

onMounted(() => {
  loadPage(1)
})
</script>

<template>
  <div class="page-shell space-y-6">
    <section class="hero-panel scanline-overlay p-6 sm:p-8">
      <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 class="section-title neon-text !text-4xl">通知中心</h1>
          <p class="mt-2 text-sm text-slate-400">
            共 {{ total }} 条通知，{{ unreadCount }} 条未读
          </p>
        </div>
        <div class="flex gap-3">
          <button
            class="btn-ghost !px-4"
            :class="showUnreadOnly ? 'ring-1 ring-primary-400' : ''"
            @click="toggleUnreadFilter"
          >
            {{ showUnreadOnly ? '查看全部' : '只看未读' }}
          </button>
          <button
            v-if="unreadCount > 0"
            class="btn-secondary !px-4"
            @click="handleMarkAllRead"
          >
            全部已读
          </button>
        </div>
      </div>
    </section>

    <section v-if="loading" class="flex justify-center py-12">
      <div class="animate-pulse text-slate-400">加载中...</div>
    </section>

    <section v-else-if="notifications.length === 0" class="flex flex-col items-center gap-4 py-16">
      <div class="text-4xl">🔔</div>
      <p class="text-lg text-slate-400">暂无通知</p>
    </section>

    <section v-else class="space-y-3">
      <button
        v-for="n in notifications"
        :key="n.id"
        type="button"
        class="surface-card flex w-full items-start gap-4 p-4 text-left transition-all sm:p-5"
        :class="n.is_read ? 'opacity-60' : 'border-l-4 border-l-primary-400'"
        @click="handleClick(n)"
      >
        <span class="mt-0.5 text-2xl">{{ typeMeta(n.type).icon }}</span>
        <div class="min-w-0 flex-1">
          <div class="flex items-center gap-2">
            <span class="text-xs text-primary-300">{{ typeMeta(n.type).label }}</span>
            <span v-if="!n.is_read" class="h-2 w-2 rounded-full bg-primary-400"></span>
          </div>
          <h3 class="mt-1 text-sm font-semibold text-white">{{ n.title }}</h3>
          <p class="mt-1 text-sm text-slate-400">{{ n.content }}</p>
          <p class="mt-2 text-xs text-slate-500">{{ formatTime(n.created_at) }}</p>
        </div>
      </button>
    </section>

    <div v-if="pageCount > 1" class="flex items-center justify-center gap-2 py-4">
      <button
        v-for="p in pageCount"
        :key="p"
        class="filter-pill"
        :class="p === page ? 'filter-pill-active' : ''"
        @click="loadPage(p)"
      >
        {{ p }}
      </button>
    </div>
  </div>
</template>
