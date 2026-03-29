<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const email = ref('')
const username = ref('')
const password = ref('')
const confirmPassword = ref('')
const showPassword = ref(false)
const errorMessage = ref('')

const isLoading = computed(() => authStore.loading)

const passwordError = computed(() => {
  if (password.value && password.value.length < 6) {
    return '密码长度至少为 6 位。'
  }

  if (confirmPassword.value && password.value !== confirmPassword.value) {
    return '两次输入的密码不一致。'
  }

  return ''
})

const isFormValid = computed(() => {
  return (
    email.value.trim() !== '' &&
    username.value.trim() !== '' &&
    password.value.length >= 6 &&
    password.value === confirmPassword.value
  )
})

const registerBenefits = [
  '发布王者荣耀、英雄联盟、和平精英、原神等常见服务需求。',
  '在个人中心补充常玩游戏、联系方式和服务偏好，减少反复沟通。',
  '上传段位截图并填写擅长方向后，可申请成为代练师接单。',
]

async function handleRegister() {
  if (!isFormValid.value) {
    errorMessage.value = passwordError.value || '请先完成所有必填项。'
    return
  }

  errorMessage.value = ''

  const result = await authStore.register(email.value, username.value, password.value)
  if (result.success) {
    router.push('/')
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
    <div class="grid gap-8 lg:grid-cols-[0.98fr_1.02fr] lg:items-stretch">
      <section class="surface-card p-6 sm:p-8 lg:p-10">
        <div class="mb-8">
          <p class="text-sm font-medium text-primary-100">创建账号</p>
          <h1 class="mt-2 text-3xl font-semibold text-white sm:text-4xl">注册后即可发布需求、查看进度或申请接单</h1>
          <p class="mt-3 text-sm leading-6 text-slate-400">
            创建账号后，你可以统一管理上分、代肝、陪练等需求，也能把常玩游戏和服务偏好整理到个人资料里。
          </p>
        </div>

        <div v-if="errorMessage" class="message-error mb-6">
          {{ errorMessage }}
        </div>

        <form class="space-y-5" @submit.prevent="handleRegister">
          <div>
            <label for="register-email" class="label">邮箱地址</label>
            <input
              id="register-email"
              v-model="email"
              type="email"
              class="input"
              placeholder="请输入常用邮箱"
              autocomplete="email"
              required
            />
          </div>

          <div>
            <label for="register-username" class="label">用户名</label>
            <input
              id="register-username"
              v-model="username"
              type="text"
              class="input"
              placeholder="请输入昵称或称呼"
              autocomplete="username"
              required
            />
          </div>

          <div>
            <div class="mb-2 flex items-center justify-between">
              <label for="register-password" class="label !mb-0">登录密码</label>
              <button type="button" class="text-xs text-slate-400 hover:text-white" @click="togglePassword">
                {{ showPassword ? '隐藏密码' : '显示密码' }}
              </button>
            </div>
            <input
              id="register-password"
              v-model="password"
              :type="showPassword ? 'text' : 'password'"
              class="input"
              :class="{ 'input-error': password && password.length < 6 }"
              placeholder="不少于 6 位"
              autocomplete="new-password"
              required
            />
          </div>

          <div>
            <label for="register-confirm-password" class="label">确认密码</label>
            <input
              id="register-confirm-password"
              v-model="confirmPassword"
              :type="showPassword ? 'text' : 'password'"
              class="input"
              :class="{ 'input-error': confirmPassword && password !== confirmPassword }"
              placeholder="再次输入密码"
              autocomplete="new-password"
              required
            />
            <p v-if="passwordError" class="helper-text !text-rose-200">
              {{ passwordError }}
            </p>
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
            {{ isLoading ? '注册中...' : '创建账号并进入平台' }}
          </button>
        </form>

        <div class="my-8 border-t border-white/10"></div>

        <div class="space-y-3">
          <router-link to="/login" class="btn-secondary w-full py-3">
            已有账号，立即登录
          </router-link>
          <router-link to="/" class="btn-ghost w-full py-3">
            返回首页
          </router-link>
        </div>
      </section>

      <section class="hero-panel flex flex-col justify-between p-6 sm:p-8 lg:p-10">
        <div class="space-y-5">
          <p class="eyebrow">注册后可做什么</p>
          <h2 class="section-title !text-4xl sm:!text-5xl">
            想下单也好，想接单也好，都能从这里开始。
          </h2>
          <p class="section-copy max-w-2xl">
            如果你是玩家，可以发布冲段、代肝和赛季冲刺需求；如果你本身擅长某个游戏，也可以后续申请成为代练师。
          </p>
        </div>

        <div class="mt-8 space-y-4">
          <div class="grid gap-4 sm:grid-cols-3">
            <div class="stat-card">
              <p class="text-2xl font-semibold text-white">1</p>
              <p class="mt-2 text-sm text-slate-400">创建账号</p>
            </div>
            <div class="stat-card">
              <p class="text-2xl font-semibold text-white">2</p>
              <p class="mt-2 text-sm text-slate-400">完善个人资料</p>
            </div>
            <div class="stat-card">
              <p class="text-2xl font-semibold text-white">3</p>
              <p class="mt-2 text-sm text-slate-400">发布需求或申请接单</p>
            </div>
          </div>

          <div class="rounded-[28px] border border-white/10 bg-white/5 p-6">
            <h3 class="text-lg font-semibold text-white">注册后你可以做什么</h3>
            <ul class="mt-4 space-y-3 text-sm leading-7 text-slate-300">
              <li
                v-for="item in registerBenefits"
                :key="item"
                class="flex items-start gap-3"
              >
                <span class="mt-2 h-2 w-2 rounded-full bg-primary-300"></span>
                <span>{{ item }}</span>
              </li>
            </ul>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>
