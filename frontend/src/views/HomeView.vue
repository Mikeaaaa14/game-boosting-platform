<script setup>
import { computed, ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { GAME_IMAGES, PAGE_BACKGROUNDS, onImgError } from '@/data/gameImages.js'

const authStore = useAuthStore()
const isAuthenticated = computed(() => authStore.isAuthenticated)
const isBooster = computed(() => authStore.isBooster)
const serviceRail = ref(null)
const activeGameKey = ref('wzry')

const primaryAction = computed(() => {
  if (!isAuthenticated.value) {
    return { to: '/register', label: '立即注册' }
  }

  return {
    to: isBooster.value ? '/orders' : '/orders/create',
    label: isBooster.value ? '查看可接订单' : '发布代练需求',
  }
})

const secondaryAction = computed(() => {
  if (!isAuthenticated.value) {
    return { to: '/login', label: '登录已有账号' }
  }

  return { to: '/profile', label: '查看个人中心' }
})

const heroStats = [
  { label: '热门游戏', value: '6+', hint: '王者、LOL、和平精英、原神等常见需求都能发布' },
  { label: '服务类型', value: '多场景', hint: '冲段、代肝、赛季冲刺、陪练与双排都可描述清楚' },
  { label: '订单状态', value: '可追踪', hint: '待接单、进行中、完成等节点都能随时查看' },
]

const gameShowcases = [
  {
    key: 'wzry',
    short: '王',
    name: '王者荣耀',
    category: 'MOBA 手游',
    headline: '赛季冲星、卡段突破、巅峰赛补分',
    intro: '适合赛季末冲王者、晋级赛卡段、巅峰积分补分与指定分路上分。可补充微信区 / QQ 区、常用英雄和可打时段。',
    highlights: ['分路和英雄池可备注', '支持赛季末冲分和保星需求', '适合想快速突破瓶颈的玩家'],
    scenes: [
      {
        title: '赛季末冲王者',
        route: '星耀三 → 王者',
        copy: '适合卡在晋级赛、想在赛季结算前稳定补星的玩家。',
      },
      {
        title: '巅峰赛补分',
        route: '巅峰 1500 → 1800',
        copy: '适合想提高巅峰积分、补足常用英雄战力的玩家。',
      },
      {
        title: '指定分路上分',
        route: '打野 / 发育路 / 中路',
        copy: '可写清常用英雄和补位偏好，减少来回确认。',
      },
    ],
  },
  {
    key: 'lol',
    short: 'LOL',
    name: '英雄联盟',
    category: '端游排位',
    headline: '单双排冲段、定位赛补分、分路专精',
    intro: '适合艾欧尼亚等大区的赛季补分、单双排冲段和指定分路需求。可补充英雄池、位置偏好与在线时段。',
    highlights: ['支持大区、单双排和位置偏好', '适合定位赛、晋级赛和赛季冲刺', '对中野联动、上路单带等打法偏好更友好'],
    scenes: [
      {
        title: '单双排冲钻石',
        route: '铂金二 → 钻石',
        copy: '适合想在赛季中后段补分、快速提升隐藏分的玩家。',
      },
      {
        title: '定位赛开局优化',
        route: '新赛季定位',
        copy: '适合刚开赛季，希望前期把定位结果打得更稳的玩家。',
      },
      {
        title: '分路专精上分',
        route: '中单 / 打野 / ADC',
        copy: '可备注常用英雄和禁用思路，降低沟通成本。',
      },
    ],
  },
  {
    key: 'hpjy',
    short: '和',
    name: '和平精英',
    category: '战术竞技',
    headline: '王牌冲刺、双排语音、赛季稳定上分',
    intro: '适合想稳定冲王牌、提高段位分、偏好双排语音沟通的玩家。可写清楚单双排、四排与时间安排。',
    highlights: ['适合赛季冲王牌和稳分需求', '可备注双排语音或固定时段', '对团队协作和沟通型需求更友好'],
    scenes: [
      {
        title: '赛季冲王牌',
        route: '皇冠五 → 王牌',
        copy: '适合赛季时间有限、想尽快完成目标段位的玩家。',
      },
      {
        title: '双排语音配合',
        route: '双排 / 语音指挥',
        copy: '适合希望边打边沟通、提高配合效率的用户。',
      },
      {
        title: '稳分保段',
        route: '防掉段 / 防掉星',
        copy: '适合已经接近目标段位，只想稳定保住当前成绩的玩家。',
      },
    ],
  },
  {
    key: 'ys',
    short: '原',
    name: '原神',
    category: '开放世界',
    headline: '日常代肝、活动推进、阶段目标整理',
    intro: '适合每日委托、体力消耗、活动奖励、深境螺旋和材料收集等代肝需求。可写清服务器、练度和目标任务。',
    highlights: ['适合长期日常和活动节奏整理', '可按周目标或活动节点发单', '对材料、圣遗物和副本目标支持更清楚'],
    scenes: [
      {
        title: '每日体力与委托',
        route: '日常代肝',
        copy: '适合工作忙、上线时间少，但又不想落下日常资源的玩家。',
      },
      {
        title: '限时活动推进',
        route: '活动奖励 / 商店兑换',
        copy: '适合想拿满活动奖励、却来不及完成阶段任务的玩家。',
      },
      {
        title: '阶段目标整理',
        route: '材料 / 圣遗物 / 深境螺旋',
        copy: '可提前写清角色培养方向，减少重复沟通。',
      },
    ],
  },
  {
    key: 'yjwj',
    short: '劫',
    name: '永劫无间',
    category: '竞技协作',
    headline: '排位冲分、三排配合、英雄熟练度提升',
    intro: '适合单排冲分、三排配合和指定英雄练习。可补充常用武器、队伍模式和希望提升的具体环节。',
    highlights: ['适合排位冲分和三排协作', '可备注常用英雄与武器体系', '对想提升配合质量的玩家更实用'],
    scenes: [
      {
        title: '赛季冲分',
        route: '当前段位 → 目标段位',
        copy: '适合赛季末想补分、提升排位结算成绩的玩家。',
      },
      {
        title: '三排协作',
        route: '组排配合',
        copy: '适合希望在配合、集火和资源分配上更顺畅的用户。',
      },
      {
        title: '英雄 / 武器专项',
        route: '角色熟练度提升',
        copy: '可说明常用英雄与武器，服务目标更聚焦。',
      },
    ],
  },
]

const activeGame = computed(() => {
  return gameShowcases.find((game) => game.key === activeGameKey.value) || gameShowcases[0]
})

const servicePromises = [
  {
    title: '热门段位冲刺',
    tag: '上分',
    copy: '适合王者、LOL、永劫无间等有明确段位目标的用户，把当前段位、目标段位和预算一次写清楚。',
  },
  {
    title: '日常与活动代肝',
    tag: '代肝',
    copy: '适合原神等周期任务较多的游戏，按每日、每周或活动节点整理需求会更高效。',
  },
  {
    title: '双排与陪练沟通',
    tag: '陪练',
    copy: '适合和平精英等强调实时配合的游戏，可以补充语音、时段和沟通方式偏好。',
  },
]

const journeySteps = [
  {
    title: '选好游戏与目标',
    copy: '先明确你是要冲段、代肝、双排还是赛季冲刺，目标越清楚，后续越省事。',
  },
  {
    title: '写清预算与偏好',
    copy: '把区服、常用位置、英雄池、在线时段和沟通方式一起写出来，减少反复确认。',
  },
  {
    title: '等待接单与沟通',
    copy: '订单发布后可以查看状态变化，决定是否继续补充信息或确认合作。',
  },
  {
    title: '跟进进度与验收',
    copy: '完成、争议或其他关键节点都会显示在订单里，方便你随时回看。',
  },
]

function selectGame(gameKey) {
  activeGameKey.value = gameKey
  serviceRail.value?.scrollTo({ left: 0, behavior: 'smooth' })
}

function scrollScenes(direction) {
  serviceRail.value?.scrollBy({ left: direction * 320, behavior: 'smooth' })
}
</script>

<template>
  <div class="page-shell space-y-14">
    <section class="hero-panel scanline-overlay p-6 sm:p-8 lg:p-10" style="background-image: linear-gradient(135deg, rgba(10,10,15,0.92), rgba(18,18,26,0.88)), url('https://images.unsplash.com/photo-1579546929518-9e396f3cc809?w=1600&q=80'); background-size: cover; background-position: center;">
      <div class="absolute inset-y-0 right-0 hidden w-1/2 bg-gradient-to-l from-primary-400/10 via-transparent to-transparent lg:block"></div>
      <div class="grid gap-8 lg:grid-cols-[1.08fr_0.92fr] lg:items-center">
        <div class="space-y-6">
          <p class="eyebrow">热门游戏上分 · 赛季冲刺 · 代肝代打 · 陪练协作</p>
          <div class="space-y-4">
            <h1 class="display-title max-w-3xl">
              把上分、冲段、代肝和赛季冲刺，
              <span class="cyber-gradient neon-text">交给更懂游戏节奏的人</span>
              去完成。
            </h1>
            <p class="section-copy max-w-2xl">
              王者荣耀、英雄联盟、和平精英、原神等常见需求都能在同一平台发布。先把游戏、目标、预算和时段写清楚，再决定下一步怎么下单，会比零散沟通省心得多。
            </p>
          </div>

          <div class="flex flex-col gap-3 sm:flex-row">
            <router-link :to="primaryAction.to" class="btn-primary px-6 py-3">
              {{ primaryAction.label }}
            </router-link>
            <router-link :to="secondaryAction.to" class="btn-secondary px-6 py-3">
              {{ secondaryAction.label }}
            </router-link>
          </div>

          <div class="grid gap-3 sm:grid-cols-3">
            <div
              v-for="item in heroStats"
              :key="item.label"
              class="stat-card cyber-corner"
            >
              <p class="text-2xl font-semibold text-white">{{ item.value }}</p>
              <p class="mt-1 text-sm text-slate-200">{{ item.label }}</p>
              <p class="mt-2 text-xs leading-6 text-slate-400">{{ item.hint }}</p>
            </div>
          </div>
        </div>

        <div class="surface-card overflow-hidden p-6 sm:p-7">
          <div class="flex items-center justify-between gap-4">
            <div>
              <p class="text-sm font-medium text-primary-100">按游戏切换</p>
              <p class="mt-2 text-sm leading-6 text-slate-400">先选你最关心的游戏，再看更贴近该游戏节奏的服务场景。</p>
            </div>
            <span class="badge-review">可切换</span>
          </div>

          <div class="mt-5 flex flex-wrap gap-2">
            <button
              v-for="game in gameShowcases"
              :key="game.key"
              type="button"
              class="rounded-full border px-4 py-2 text-sm font-medium transition"
              :class="game.key === activeGame.key ? 'border-primary-300/50 bg-primary-500/15 text-white shadow-glow' : 'border-white/10 bg-white/5 text-slate-300 hover:border-white/20 hover:text-white'"
              @click="selectGame(game.key)"
            >
              {{ game.name }}
            </button>
          </div>

          <div class="mt-6 rounded-[30px] border border-white/10 bg-white/5 p-5 sm:p-6">
            <div class="flex items-start gap-4">
              <div class="flex h-16 w-16 shrink-0 items-center justify-center rounded-[24px] bg-gradient-to-br from-primary-300/30 to-accent-300/20 text-2xl font-semibold text-white">
                {{ activeGame.short }}
              </div>
              <div class="space-y-2">
                <div class="flex flex-wrap items-center gap-2">
                  <h2 class="text-2xl font-semibold text-white">{{ activeGame.name }}</h2>
                  <span class="tag">{{ activeGame.category }}</span>
                </div>
                <p class="text-lg font-medium text-primary-100">{{ activeGame.headline }}</p>
                <p class="text-sm leading-7 text-slate-300">{{ activeGame.intro }}</p>
              </div>
            </div>

            <div class="mt-6 grid gap-3 sm:grid-cols-3">
              <div
                v-for="item in activeGame.highlights"
                :key="item"
                class="rounded-3xl border border-white/10 bg-slate-950/40 p-4 text-sm leading-6 text-slate-300"
              >
                {{ item }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="space-y-6">
      <div class="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <p class="eyebrow">服务场景</p>
          <h2 class="section-title mt-4">切换游戏后，横向浏览更具体的下单方向</h2>
        </div>
        <div class="flex items-center gap-3">
          <p class="max-w-xl text-sm leading-7 text-slate-400">
            这一排卡片支持横向滑动，你可以快速切换不同游戏对应的常见场景，再决定自己想发布哪类需求。
          </p>
          <div class="hidden gap-2 sm:flex">
            <button class="btn-secondary !px-4 !py-2" @click="scrollScenes(-1)">向左</button>
            <button class="btn-secondary !px-4 !py-2" @click="scrollScenes(1)">向右</button>
          </div>
        </div>
      </div>

      <div
        ref="serviceRail"
        class="flex snap-x snap-mandatory gap-4 overflow-x-auto pb-2"
      >
        <article
          v-for="scene in activeGame.scenes"
          :key="`${activeGame.key}-${scene.title}`"
          class="card-hover scanline-overlay min-w-[280px] snap-start sm:min-w-[320px]"
        >
          <div class="flex items-center justify-between gap-3">
            <span class="tag">{{ activeGame.name }}</span>
            <span class="text-sm font-semibold text-accent-300">{{ scene.route }}</span>
          </div>
          <h3 class="mt-8 text-2xl font-semibold text-white">{{ scene.title }}</h3>
          <p class="mt-4 text-sm leading-7 text-slate-400">{{ scene.copy }}</p>
        </article>
      </div>
    </section>

    <section class="grid gap-5 lg:grid-cols-3">
      <article
        v-for="item in servicePromises"
        :key="item.title"
        class="card-hover cyber-corner"
      >
        <div class="flex items-center justify-between">
          <span class="tag">{{ item.tag }}</span>
          <span class="text-sm font-semibold text-primary-200">适合明确目标的玩家</span>
        </div>
        <h2 class="mt-6 text-xl font-semibold text-white">{{ item.title }}</h2>
        <p class="mt-3 text-sm leading-7 text-slate-400">{{ item.copy }}</p>
      </article>
    </section>

    <section class="grid gap-8 lg:grid-cols-[0.92fr_1.08fr]">
      <div class="surface-card p-6 sm:p-8">
        <p class="eyebrow">下单流程</p>
        <h2 class="section-title mt-5">把需求说清楚，比盲目发单更容易拿到合适结果</h2>
        <p class="section-copy mt-3">
          对玩家来说，最重要的不是页面有多少块，而是能不能快速说清楚“我玩什么、我想提升什么、我愿意花多少、我什么时候方便”。
        </p>
      </div>

      <div class="grid gap-4 sm:grid-cols-2">
        <article
          v-for="(step, index) in journeySteps"
          :key="step.title"
          class="card cyber-corner"
        >
          <div class="flex h-10 w-10 items-center justify-center rounded-2xl bg-primary-500/10 text-sm font-semibold text-primary-100 border" style="border-color: rgba(0, 240, 255, 0.5); box-shadow: 0 0 10px rgba(0, 240, 255, 0.3);">
            {{ index + 1 }}
          </div>
          <h3 class="mt-5 text-lg font-semibold text-white">{{ step.title }}</h3>
          <p class="mt-2 text-sm leading-6 text-slate-400">{{ step.copy }}</p>
        </article>
      </div>
    </section>

    <section class="surface-card scanline-overlay p-6 text-center sm:p-8 lg:p-10">
      <p class="eyebrow">开始下单</p>
      <h2 class="section-title mt-4">已经想好目标了，就把需求写出来。</h2>
      <p class="mx-auto mt-3 max-w-3xl text-sm leading-7 text-slate-400">
        不管你是想冲段、赛季保分，还是想把原神活动和日常委托交给别人处理，先把需求整理清楚，再进入订单大厅或发布页面会更顺手。
      </p>
      <div class="mt-8 flex flex-col justify-center gap-3 sm:flex-row">
        <router-link :to="primaryAction.to" class="btn-primary px-6 py-3">
          {{ primaryAction.label }}
        </router-link>
        <router-link :to="secondaryAction.to" class="btn-secondary px-6 py-3">
          {{ secondaryAction.label }}
        </router-link>
      </div>
    </section>
  </div>
</template>
