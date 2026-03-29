<script setup>
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const email = ref('')
const password = ref('')
const showPassword = ref(false)
const errorMessage = ref('')

const isLoading = computed(() => authStore.loading)
const isFormValid = computed(() => email.value.trim() !== '' && password.value.trim() !== '')

const sceneHighlights = [
  {
    title: '继续查看订单进度',
    copy: '登录后可以直接回到你正在跟进的上分、代肝或陪练订单。',
  },
  {
    title: '同步个人资料',
    copy: '维护昵称、手机号和常玩游戏，方便后续发单、接单和沟通。',
  },
  {
    title: '申请成为代练师',
    copy: '上传段位截图和擅长说明后，可以申请接取更适合自己的订单。',
  },
]

async function handleLogin() {
  if (!isFormValid.value) {
    errorMessage.value = '请填写邮箱和密码。'
    return
  }

  errorMessage.value = ''

  const result = await authStore.login(email.value, password.value)
  if (result.success) {
    const redirect = route.query.redirect || '/'
    router.push(redirect)
    return
  }

  errorMessage.value = result.error
}

function togglePassword() {
  showPassword.value = !showPassword.value
}
</script>

<template>
  <div class="page-shell">
    <div class="grid gap-8 lg:grid-cols-[1.04fr_0.96fr] lg:items-stretch">
      <section class="hero-panel scanline-overlay flex flex-col justify-between p-6 sm:p-8 lg:p-10">
        <div class="space-y-5">
          <p class="eyebrow">账号入口</p>
          <h1 class="section-title neon-text !text-4xl sm:!text-5xl">
            欢迎回来，继续处理你的上分订单和服务进度。
          </h1>
          <p class="section-copy max-w-2xl">
            无论你是来发布王者冲星、LOL 冲段，还是查看原神代肝和陪练进度，登录后都能直接回到上次操作的位置。
          </p>
        </div>

        <div class="mt-8 grid gap-4">
          <div class="grid gap-4 sm:grid-cols-3">
            <div class="stat-card cyber-corner">
              <p class="text-2xl font-semibold text-white">订单进度</p>
              <p class="mt-2 text-sm text-slate-400">查看已发布、已接单和已完成状态</p>
            </div>
            <div class="stat-card cyber-corner">
              <p class="text-2xl font-semibold text-white">个人资料</p>
              <p class="mt-2 text-sm text-slate-400">补充联系方式、简介和常玩游戏</p>
            </div>
            <div class="stat-card cyber-corner">
              <p class="text-2xl font-semibold text-white">接单认证</p>
              <p class="mt-2 text-sm text-slate-400">提交段位截图后可申请成为代练师</p>
            </div>
          </div>

          <div class="grid gap-4">
            <article
              v-for="item in sceneHighlights"
              :key="item.title"
              class="rounded-[28px] border border-white/10 bg-white/5 p-5"
            >
              <h2 class="text-lg font-semibold text-white">{{ item.title }}</h2>
              <p class="mt-2 text-sm leading-7 text-slate-400">{{ item.copy }}</p>
            </article>
          </div>
        </div>
      </section>

      <section class="surface-card cyber-corner p-6 sm:p-8 lg:p-10">
        <div class="mb-8">
          <p class="text-sm font-medium text-primary-100">登录账号</p>
          <h2 class="mt-2 text-3xl font-semibold text-white">回到你的服务面板</h2>
          <p class="mt-3 text-sm leading-6 text-slate-400">
            使用邮箱和密码登录，系统会自动带你回到刚才想访问的页面。
          </p>
        </div>

        <div v-if="errorMessage" class="message-error mb-6">
          {{ errorMessage }}
        </div>

        <form class="space-y-5" @submit.prevent="handleLogin">
          <div>
            <label for="email" class="label">邮箱地址</label>
            <input
              id="email"
              v-model="email"
              type="email"
              class="input"
              :class="{ 'input-error': errorMessage && !email }"
              placeholder="请输入注册邮箱"
              autocomplete="email"
              required
            />
          </div>

          <div>
            <div class="mb-2 flex items-center justify-between">
              <label for="password" class="label !mb-0">登录密码</label>
              <button type="button" class="text-xs text-slate-400 hover:text-white" @click="togglePassword">
                {{ showPassword ? '隐藏密码' : '显示密码' }}
              </button>
            </div>
            <input
              id="password"
              v-model="password"
              :type="showPassword ? 'text' : 'password'"
              class="input"
              :class="{ 'input-error': errorMessage && !password }"
              placeholder="请输入密码"
              autocomplete="current-password"
              required
            />
          </div>

          <button
            type="submit"
            :disabled="isLoading || !isFormValid"
            class="btn-primary w-full py-3"
          >
            <svg
              v-if="isLoading"
              class="h-5 w-5 animate-spin"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
            {{ isLoading ? '登录中...' : '登录并进入平台' }}
          </button>
        </form>

        <div class="my-8 border-t border-white/10"></div>

        <div class="space-y-3">
          <router-link to="/register" class="btn-secondary w-full py-3">
            还没有账号，前往注册
          </router-link>
          <router-link to="/" class="btn-ghost w-full py-3">
            返回首页
          </router-link>
        </div>
      </section>
    </div>
  </div>
</template>
