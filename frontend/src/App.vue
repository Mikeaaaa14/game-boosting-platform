<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { getUserRoleMeta } from '@/utils/order'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const isAuthenticated = computed(() => authStore.isAuthenticated)
const isBooster = computed(() => authStore.isBooster)
const isAdmin = computed(() => authStore.isAdmin)
const user = computed(() => authStore.user)
const roleMeta = computed(() => getUserRoleMeta(user.value?.role))

const navItems = computed(() => [
  { to: '/', label: '首页', exact: true, show: true },
  {
    to: '/orders',
    label: isBooster.value ? '订单大厅' : '我的订单',
    exact: false,
    show: isAuthenticated.value,
  },
  {
    to: '/orders/create',
    label: '发布需求',
    exact: false,
    show: isAuthenticated.value && !isBooster.value,
  },
  {
    to: '/profile',
    label: '个人中心',
    exact: false,
    show: isAuthenticated.value,
  },
  {
    to: '/admin',
    label: '运营面板',
    exact: false,
    show: isAuthenticated.value && isAdmin.value,
  },
].filter((item) => item.show))

function isActiveLink(item) {
  if (item.exact) {
    return route.path === item.to
  }

  return route.path === item.to || route.path.startsWith(`${item.to}/`)
}

function handleLogout() {
  authStore.logout()
  router.push({ name: 'login' })
}
</script>

<template>
  <div class="min-h-screen">
    <nav class="sticky top-0 z-50 border-b border-white/10 bg-slate-950/80 backdrop-blur-xl">
      <div class="shell-container flex min-h-20 flex-wrap items-center justify-between gap-4 py-4">
        <router-link to="/" class="flex items-center gap-3">
          <div class="flex h-11 w-11 items-center justify-center rounded-2xl border border-primary-300/30 bg-primary-500/10 text-lg font-semibold text-primary-100 shadow-glow">
            练
          </div>
          <div>
            <p class="text-base font-semibold text-white">游戏代练平台</p>
            <p class="text-xs text-slate-400">上分、冲段、代肝与定制代练服务</p>
          </div>
        </router-link>

        <div class="hidden items-center gap-1 xl:flex">
          <router-link
            v-for="item in navItems"
            :key="item.to"
            :to="item.to"
            :class="isActiveLink(item) ? 'nav-chip-active' : 'nav-chip-idle'"
          >
            {{ item.label }}
          </router-link>
        </div>

        <div class="flex flex-wrap items-center justify-end gap-2 sm:gap-3">
          <span
            v-if="isAuthenticated"
            :class="roleMeta.badgeClass"
          >
            {{ roleMeta.label }}
          </span>

          <template v-if="isAuthenticated">
            <router-link to="/profile" class="btn-secondary !px-4">
              {{ user?.username || '个人中心' }}
            </router-link>
            <button class="btn-ghost !px-4" @click="handleLogout">退出登录</button>
          </template>
          <template v-else>
            <router-link to="/login" class="btn-ghost !px-4">登录</router-link>
            <router-link to="/register" class="btn-primary !px-4">立即注册</router-link>
          </template>
        </div>
      </div>

      <div class="shell-container flex gap-2 overflow-x-auto pb-4 xl:hidden">
        <router-link
          v-for="item in navItems"
          :key="`${item.to}-mobile`"
          :to="item.to"
          :class="isActiveLink(item) ? 'nav-chip-active' : 'nav-chip-idle'"
        >
          {{ item.label }}
        </router-link>
      </div>
    </nav>

    <main class="relative z-10">
      <router-view />
    </main>

    <footer class="border-t border-white/10 bg-slate-950/70">
      <div class="shell-container grid gap-8 py-10 lg:grid-cols-[1.2fr_0.8fr]">
        <div class="space-y-3">
          <p class="eyebrow">热门服务</p>
          <h2 class="section-title max-w-xl">
            把上分、冲段、代肝和赛季冲刺需求集中到同一平台处理。
          </h2>
          <p class="section-copy max-w-2xl">
            无论是王者荣耀冲星、英雄联盟冲段、和平精英双排上分，还是原神日常代肝，都可以在同一套流程里发布需求、查看状态与继续沟通。
          </p>
        </div>

        <div class="grid grid-cols-1 gap-4 sm:grid-cols-3 lg:grid-cols-1">
          <div class="stat-card">
            <p class="text-2xl font-semibold text-white">6+</p>
            <p class="mt-1 text-sm text-slate-400">热门游戏服务覆盖</p>
          </div>
          <div class="stat-card">
            <p class="text-2xl font-semibold text-white">多场景</p>
            <p class="mt-1 text-sm text-slate-400">冲段、代肝、活动与陪练</p>
          </div>
          <div class="stat-card">
            <p class="text-2xl font-semibold text-white">全流程</p>
            <p class="mt-1 text-sm text-slate-400">下单、接单、完成状态可查</p>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>
