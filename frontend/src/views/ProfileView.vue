<script setup>
import { computed, onMounted, ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/utils/api'
import { formatDate } from '@/utils/display'
import { getApplicationStatusMeta, getUserRoleMeta } from '@/utils/order'

const authStore = useAuthStore()

const user = computed(() => authStore.user)
const roleMeta = computed(() => getUserRoleMeta(user.value?.role))
const applicationMeta = computed(() => getApplicationStatusMeta(application.value?.status || 'NONE'))
const avatarText = computed(() => user.value?.username?.slice(0, 1)?.toUpperCase() || 'U')
const proofFileName = computed(() => appForm.value.proof_image?.name || '未选择截图文件')
const canSubmitPassword = computed(() => {
  return (
    passwordForm.value.currentPassword.trim() !== '' &&
    passwordForm.value.newPassword.length >= 6 &&
    passwordForm.value.newPassword === passwordForm.value.confirmPassword
  )
})

const shouldShowApplicationForm = computed(() => {
  if (user.value?.role === 'ADMIN') {
    return false
  }

  return !application.value || ['NONE', 'REJECTED'].includes(application.value.status)
})

const profileForm = ref({
  username: '',
  phone: '',
  bio: '',
})

const passwordForm = ref({
  currentPassword: '',
  newPassword: '',
  confirmPassword: '',
})

const appForm = ref({
  game_name: '',
  current_rank: '',
  target_rank: '',
  note: '',
  proof_image: null,
})

const application = ref(null)
const profileMessage = ref({ type: '', text: '' })
const passwordMessage = ref({ type: '', text: '' })
const applicationMessage = ref({ type: '', text: '' })
const savingProfile = ref(false)
const changingPassword = ref(false)
const submittingApplication = ref(false)

function messageClass(type) {
  if (type === 'success') {
    return 'message-success'
  }

  if (type === 'error') {
    return 'message-error'
  }

  return 'message-info'
}

function resetProfileForm() {
  profileForm.value = {
    username: user.value?.username || '',
    phone: user.value?.phone || '',
    bio: user.value?.bio || '',
  }
}

function hydrateApplicationForm() {
  appForm.value.game_name = application.value?.game_name || ''
  appForm.value.current_rank = application.value?.current_rank || ''
  appForm.value.target_rank = application.value?.target_rank || ''
  appForm.value.note = application.value?.note || ''
  appForm.value.proof_image = null
}

async function fetchApplication() {
  try {
    const res = await api.get('/users/me/booster-application')
    application.value = res.data
    hydrateApplicationForm()
  } catch (error) {
    application.value = null
  }
}

async function updateProfile() {
  profileMessage.value = { type: '', text: '' }
  savingProfile.value = true

  const result = await authStore.updateProfile(profileForm.value)
  if (result.success) {
    profileMessage.value = { type: 'success', text: '个人资料已更新。' }
    resetProfileForm()
  } else {
    profileMessage.value = { type: 'error', text: result.error }
  }

  savingProfile.value = false
}

async function changePassword() {
  passwordMessage.value = { type: '', text: '' }
  if (!canSubmitPassword.value) {
    passwordMessage.value = { type: 'error', text: '请检查当前密码、新密码和确认密码。' }
    return
  }

  changingPassword.value = true
  const result = await authStore.changePassword(
    passwordForm.value.currentPassword,
    passwordForm.value.newPassword
  )

  if (result.success) {
    passwordMessage.value = { type: 'success', text: '密码修改成功，请妥善保管。' }
    passwordForm.value = {
      currentPassword: '',
      newPassword: '',
      confirmPassword: '',
    }
  } else {
    passwordMessage.value = { type: 'error', text: result.error }
  }

  changingPassword.value = false
}

function onProofChange(event) {
  const file = event.target.files?.[0] || null
  appForm.value.proof_image = file
}

async function submitBoosterApplication() {
  applicationMessage.value = { type: '', text: '' }

  if (!appForm.value.proof_image) {
    applicationMessage.value = { type: 'error', text: '请上传段位截图后再提交。' }
    return
  }

  submittingApplication.value = true

  try {
    const form = new FormData()
    form.append('game_name', appForm.value.game_name)
    form.append('current_rank', appForm.value.current_rank)
    form.append('target_rank', appForm.value.target_rank)
    if (appForm.value.note) {
      form.append('note', appForm.value.note)
    }
    form.append('proof_image', appForm.value.proof_image)

    const res = await api.post('/users/booster-application', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })

    application.value = res.data
    hydrateApplicationForm()
    applicationMessage.value = { type: 'success', text: '申请已提交，请等待管理员审核。' }
  } catch (error) {
    applicationMessage.value = { type: 'error', text: error.message || '提交申请失败。' }
  }

  submittingApplication.value = false
}

onMounted(async () => {
  resetProfileForm()
  await fetchApplication()
})
</script>

<template>
  <div class="page-shell space-y-8">
    <section class="hero-panel p-6 sm:p-8 lg:p-10">
      <div class="flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
        <div class="flex items-start gap-5">
          <div class="flex h-20 w-20 items-center justify-center rounded-[28px] border border-primary-300/30 bg-primary-500/10 text-3xl font-semibold text-primary-100 shadow-glow">
            {{ avatarText }}
          </div>
          <div class="space-y-3">
            <div class="flex flex-wrap items-center gap-3">
              <h1 class="section-title !text-4xl sm:!text-5xl">{{ user?.username || '个人中心' }}</h1>
              <span :class="roleMeta.badgeClass">{{ roleMeta.label }}</span>
            </div>
            <p class="text-sm text-slate-300">{{ user?.email }}</p>
            <p class="section-copy max-w-2xl">
              在这里维护昵称、联系方式、常玩游戏简介和代练认证信息，方便后续发单、接单和审核沟通。
            </p>
          </div>
        </div>

        <div class="grid gap-4 sm:grid-cols-3 lg:grid-cols-1">
          <div class="stat-card">
            <p class="text-sm text-slate-400">注册时间</p>
            <p class="mt-2 text-lg font-semibold text-white">{{ formatDate(user?.created_at) }}</p>
          </div>
          <div class="stat-card">
            <p class="text-sm text-slate-400">账号状态</p>
            <p class="mt-2 text-lg font-semibold text-white">{{ user?.is_active ? '正常可用' : '已停用' }}</p>
          </div>
          <div class="stat-card">
            <p class="text-sm text-slate-400">认证状态</p>
            <p class="mt-2 text-lg font-semibold text-white">{{ applicationMeta.label }}</p>
          </div>
        </div>
      </div>
    </section>

    <div class="grid gap-6 xl:grid-cols-[1.02fr_0.98fr]">
      <section class="space-y-6">
        <article class="surface-card p-6 sm:p-8">
          <div class="flex items-end justify-between gap-4">
            <div>
              <h2 class="text-2xl font-semibold text-white">编辑资料</h2>
              <p class="mt-2 text-sm leading-7 text-slate-400">
                补充常玩游戏、擅长方向和合作习惯，让别人更快看懂你的账号信息。
              </p>
            </div>
          </div>

          <div v-if="profileMessage.text" class="mt-6" :class="messageClass(profileMessage.type)">
            {{ profileMessage.text }}
          </div>

          <form class="mt-6 space-y-5" @submit.prevent="updateProfile">
            <div class="grid gap-5 sm:grid-cols-2">
              <div>
                <label for="profile-username" class="label">用户名</label>
                <input id="profile-username" v-model="profileForm.username" type="text" class="input" placeholder="请输入用户名" />
              </div>
              <div>
                <label for="profile-phone" class="label">手机号</label>
                <input id="profile-phone" v-model="profileForm.phone" type="text" class="input" placeholder="请输入手机号" />
              </div>
            </div>

            <div>
              <label for="profile-bio" class="label">个人简介</label>
              <textarea
                id="profile-bio"
                v-model="profileForm.bio"
                rows="4"
                class="input resize-none"
                placeholder="介绍一下你常玩的游戏、擅长方向或合作习惯。"
              ></textarea>
            </div>

            <button class="btn-primary w-full py-3" :disabled="savingProfile">
              {{ savingProfile ? '保存中...' : '保存个人资料' }}
            </button>
          </form>
        </article>

        <article class="surface-card p-6 sm:p-8">
          <h2 class="text-2xl font-semibold text-white">账户安全</h2>
          <p class="mt-2 text-sm leading-7 text-slate-400">
            如果需要调整密码，可以直接在这里更新，保护账号和订单沟通安全。
          </p>

          <div v-if="passwordMessage.text" class="mt-6" :class="messageClass(passwordMessage.type)">
            {{ passwordMessage.text }}
          </div>

          <form class="mt-6 space-y-5" @submit.prevent="changePassword">
            <div>
              <label for="current-password" class="label">当前密码</label>
              <input id="current-password" v-model="passwordForm.currentPassword" type="password" class="input" placeholder="请输入当前密码" />
            </div>
            <div class="grid gap-5 sm:grid-cols-2">
              <div>
                <label for="new-password" class="label">新密码</label>
                <input id="new-password" v-model="passwordForm.newPassword" type="password" class="input" placeholder="不少于 6 位" />
              </div>
              <div>
                <label for="confirm-new-password" class="label">确认新密码</label>
                <input id="confirm-new-password" v-model="passwordForm.confirmPassword" type="password" class="input" placeholder="再次输入新密码" />
              </div>
            </div>
            <button class="btn-secondary w-full py-3" :disabled="changingPassword || !canSubmitPassword">
              {{ changingPassword ? '提交中...' : '更新账户密码' }}
            </button>
          </form>
        </article>
      </section>

      <aside class="space-y-6">
        <article class="surface-card p-6 sm:p-8">
          <div class="flex items-start justify-between gap-4">
            <div>
              <h2 class="text-2xl font-semibold text-white">代练师申请</h2>
              <p class="mt-2 text-sm leading-7 text-slate-400">
                上传段位截图和服务说明，让管理员更容易判断你适合接哪类订单。
              </p>
            </div>
            <span :class="applicationMeta.badgeClass">{{ applicationMeta.label }}</span>
          </div>

          <div v-if="applicationMessage.text" class="mt-6" :class="messageClass(applicationMessage.type)">
            {{ applicationMessage.text }}
          </div>

          <div class="mt-6 space-y-4">
            <div class="rounded-3xl border border-white/10 bg-white/5 p-5">
              <p class="text-sm font-medium text-primary-100">当前说明</p>
              <p class="mt-3 text-sm leading-7 text-slate-300">{{ applicationMeta.description }}</p>
            </div>

            <div v-if="application?.review_note" class="rounded-3xl border border-amber-400/20 bg-amber-400/10 p-5">
              <p class="text-sm font-medium text-amber-100">管理员备注</p>
              <p class="mt-3 text-sm leading-7 text-amber-50">{{ application.review_note }}</p>
            </div>

            <div v-if="application?.reviewed_at" class="rounded-3xl border border-white/10 bg-white/5 p-5">
              <p class="text-sm font-medium text-primary-100">最近审核时间</p>
              <p class="mt-3 text-sm leading-7 text-slate-300">{{ formatDate(application.reviewed_at) }}</p>
            </div>
          </div>

          <form
            v-if="shouldShowApplicationForm"
            class="mt-6 space-y-5"
            @submit.prevent="submitBoosterApplication"
          >
            <div>
              <label for="apply-game" class="label">申请游戏</label>
              <input id="apply-game" v-model="appForm.game_name" type="text" class="input" placeholder="例如：王者荣耀" required />
            </div>
            <div class="grid gap-5 sm:grid-cols-2">
              <div>
                <label for="apply-current-rank" class="label">当前段位</label>
                <input id="apply-current-rank" v-model="appForm.current_rank" type="text" class="input" placeholder="例如：王者 20 星" required />
              </div>
              <div>
                <label for="apply-target-rank" class="label">擅长目标段位</label>
                <input id="apply-target-rank" v-model="appForm.target_rank" type="text" class="input" placeholder="例如：荣耀王者" required />
              </div>
            </div>
            <div>
              <label for="apply-note" class="label">补充说明</label>
              <textarea
                id="apply-note"
                v-model="appForm.note"
                rows="4"
                class="input resize-none"
                placeholder="补充说明你的经验、可服务时段或历史成绩。"
              ></textarea>
            </div>
            <div class="rounded-3xl border border-white/10 bg-white/5 p-5">
              <label for="apply-proof" class="label">段位截图</label>
              <input id="apply-proof" type="file" accept="image/*" class="input" @change="onProofChange" />
              <p class="helper-text">当前文件：{{ proofFileName }}</p>
            </div>
            <button class="btn-success w-full py-3" :disabled="submittingApplication">
              {{ submittingApplication ? '提交中...' : '提交代练师申请' }}
            </button>
          </form>

          <div v-else class="mt-6 rounded-3xl border border-white/10 bg-white/5 p-5">
            <p class="text-sm leading-7 text-slate-300">
              {{ application?.status === 'APPROVED' ? '你的代练师申请已通过，无需重复提交。' : '申请已进入审核流程，当前阶段无需重复填写。' }}
            </p>
          </div>
        </article>
      </aside>
    </div>
  </div>
</template>
