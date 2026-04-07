<script setup>
import { computed, onBeforeUnmount, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import ChatUnreadBadge from '@/components/chat/ChatUnreadBadge.vue'
import { useAuthStore } from '@/stores/auth'
import { useChatStore } from '@/stores/chat'
import { getUserRoleMeta } from '@/utils/order'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const chatStore = useChatStore()

let unreadPollingTimer = null

const copy = {
  brandTitle: '\u6e38\u620f\u4ee3\u7ec3\u5e73\u53f0',
  home: '\u9996\u9875',
  enterZone: '\u6e38\u620f\u8be6\u60c5',
  orderHall: '\u8ba2\u5355\u5927\u5385',
  myOrders: '\u6211\u7684\u8ba2\u5355',
  boosterDesk: '\u966a\u7ec3\u5de5\u4f5c\u53f0',
  messages: '\u6d88\u606f',
  ops: '\u8fd0\u8425',
  searchOrders: '\u641c\u7d22\u9700\u6c42 / \u6807\u7b7e',
  profile: '\u4e2a\u4eba\u4e2d\u5fc3',
  logout: '\u9000\u51fa\u767b\u5f55',
  login: '\u767b\u5f55',
  signup: '\u7acb\u5373\u6ce8\u518c',
  footerLine: '\u9996\u9875\u5148\u8fdb\u573a\uff0c\u518d\u9009\u4e13\u533a\u548c\u7cbe\u786e\u641c\u7d22',
  advancedSearch: '\u9ad8\u7ea7\u641c\u7d22',
}

const isAuthenticated = computed(() => authStore.isAuthenticated)
const isBooster = computed(() => authStore.isBooster)
const isAdmin = computed(() => authStore.isAdmin)
const user = computed(() => authStore.user)
const roleMeta = computed(() => getUserRoleMeta(user.value?.role))
const unreadTotal = computed(() => Number(chatStore.unreadTotal || 0))
const hideFooter = computed(() => ['login', 'register', 'chat-list', 'chat-detail'].includes(route.name))

const primaryNavItems = computed(() => [
  {
    key: 'home',
    label: copy.home,
    show: true,
    active: route.name === 'home' && !route.hash,
    action: () => router.push({ name: 'home' }),
    badge: 0,
  },
  {
    key: 'enter-zone',
    label: copy.enterZone,
    show: true,
    active: route.name === 'home',
    action: () => openHomeAnchor('#match-floor'),
    badge: 0,
  },
  {
    key: 'orders',
    label: isBooster.value ? copy.orderHall : copy.myOrders,
    show: isAuthenticated.value,
    active: ['orders', 'order-detail', 'order-create'].includes(route.name),
    action: () => router.push({ name: 'orders' }),
    badge: 0,
  },
  {
    key: 'services',
    label: copy.boosterDesk,
    show: isAuthenticated.value && isBooster.value,
    active: ['services', 'service-detail'].includes(route.name),
    action: () => router.push({ name: 'services' }),
    badge: 0,
  },
  {
    key: 'chat',
    label: copy.messages,
    show: isAuthenticated.value,
    active: ['chat-list', 'chat-detail'].includes(route.name),
    action: () => router.push({ name: 'chat-list' }),
    badge: unreadTotal.value,
  },
  {
    key: 'admin',
    label: copy.ops,
    show: isAuthenticated.value && isAdmin.value,
    active: route.name === 'admin',
    action: () => router.push({ name: 'admin' }),
    badge: 0,
  },
].filter((item) => item.show))

function openHomeAnchor(hash) {
  if (route.name === 'home') {
    const target = document.querySelector(hash)
    target?.scrollIntoView({ behavior: 'smooth', block: 'start' })
    return
  }

  router.push({ name: 'home', hash })
}

function stopUnreadPolling() {
  if (unreadPollingTimer) {
    window.clearInterval(unreadPollingTimer)
    unreadPollingTimer = null
  }
}

function openSearch() {
  router.push({ name: 'search', query: { type: 'all' } })
}

function startUnreadPolling() {
  stopUnreadPolling()

  unreadPollingTimer = window.setInterval(() => {
    if (authStore.isAuthenticated && chatStore.socketStatus !== 'connected') {
      chatStore.fetchUnreadSummary()
    }
  }, 45000)
}

async function syncChatLifecycle(isLoggedIn) {
  if (isLoggedIn) {
    await chatStore.fetchUnreadSummary()
    chatStore.connectWebSocket()
    startUnreadPolling()
    return
  }

  stopUnreadPolling()
  chatStore.disconnectWebSocket({ clearState: true })
}

async function handleLogout() {
  stopUnreadPolling()
  chatStore.disconnectWebSocket({ clearState: true })
  authStore.logout()
  router.push({ name: 'login' })
}

watch(
  isAuthenticated,
  async (isLoggedIn) => {
    await syncChatLifecycle(isLoggedIn)
  },
  { immediate: true }
)

watch(
  () => chatStore.socketStatus,
  async (status) => {
    if (isAuthenticated.value && status === 'connected') {
      await chatStore.fetchUnreadSummary()
    }
  }
)

onBeforeUnmount(() => {
  stopUnreadPolling()
  chatStore.disconnectWebSocket()
})
</script>

<template>
  <div class="min-h-screen">
    <nav class="app-header">
      <div class="shell-container flex min-h-20 flex-wrap items-center justify-between gap-4 py-4">
        <button type="button" class="brand-lockup text-left" @click="router.push({ name: 'home' })">
          <div class="brand-mark">G</div>
          <div>
            <p class="brand-lockup__title text-base text-white">{{ copy.brandTitle }}</p>
          </div>
        </button>

        <div class="hidden flex-1 items-center justify-center gap-2 xl:flex">
          <button
            v-for="item in primaryNavItems"
            :key="item.key"
            type="button"
            :class="item.active ? 'app-nav-link app-nav-link-active' : 'app-nav-link'"
            @click="item.action"
          >
            <span>{{ item.label }}</span>
            <ChatUnreadBadge v-if="item.badge" :count="item.badge" />
          </button>
        </div>

        <div class="flex flex-wrap items-center justify-end gap-2 sm:gap-3">
          <button type="button" class="app-command hidden lg:inline-flex" @click="openSearch">
            {{ copy.searchOrders }}
          </button>

          <span v-if="isAuthenticated" :class="roleMeta.badgeClass">
            {{ roleMeta.label }}
          </span>

          <template v-if="isAuthenticated">
            <router-link to="/profile" class="btn-secondary !px-4">
              {{ user?.username || copy.profile }}
            </router-link>
            <button class="btn-ghost !px-4" @click="handleLogout">{{ copy.logout }}</button>
          </template>
          <template v-else>
            <router-link to="/login" class="btn-ghost !px-4">{{ copy.login }}</router-link>
            <router-link to="/register" class="btn-primary !px-4">{{ copy.signup }}</router-link>
          </template>
        </div>
      </div>

      <div class="shell-container flex flex-col gap-3 pb-4 xl:hidden">
        <div class="flex gap-2 overflow-x-auto">
          <button
            v-for="item in primaryNavItems"
            :key="`${item.key}-mobile`"
            type="button"
            :class="item.active ? 'app-nav-link app-nav-link-active whitespace-nowrap' : 'app-nav-link whitespace-nowrap'"
            @click="item.action"
          >
            <span>{{ item.label }}</span>
            <ChatUnreadBadge v-if="item.badge" :count="item.badge" />
          </button>
        </div>

        <button type="button" class="app-command w-full justify-center" @click="openSearch">
          {{ copy.searchOrders }}
        </button>
      </div>
    </nav>

    <main class="relative z-10">
      <router-view v-slot="{ Component }">
        <transition name="page-fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>

    <footer v-if="!hideFooter" class="border-t border-white/5 bg-dark-base/70">
      <div class="shell-container flex flex-col gap-4 py-6 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p class="brand-lockup__title text-sm text-white">{{ copy.brandTitle }}</p>
        </div>

        <div class="flex flex-wrap gap-2">
          <button type="button" class="filter-pill" @click="openHomeAnchor('#match-floor')">{{ copy.enterZone }}</button>
          <router-link to="/search?type=all" class="filter-pill">{{ copy.advancedSearch }}</router-link>
          <router-link v-if="isAuthenticated" to="/orders" class="filter-pill">{{ copy.orderHall }}</router-link>
          <router-link v-if="isAuthenticated && isBooster" to="/services" class="filter-pill">{{ copy.boosterDesk }}</router-link>
        </div>
      </div>
    </footer>
  </div>
</template>
