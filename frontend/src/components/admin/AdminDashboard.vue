<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import EChart from '@/components/charts/EChart.vue'
import api from '@/utils/api'

const router = useRouter()

const overview = ref(null)
const orderTrend = ref(null)
const gameDist = ref(null)
const boosterRank = ref(null)
const userGrowth = ref(null)
const loading = ref(true)
const trendPeriod = ref('day')
const trendDays = ref(30)

const LEVEL_COLORS = {
  master: '#facc15',
  diamond: '#22d3ee',
  gold: '#f59e0b',
  silver: '#94a3b8',
  bronze: '#fb923c',
}

const overviewCards = computed(() => {
  if (!overview.value) return []
  const o = overview.value
  return [
    { label: '总用户', value: o.total_users, color: 'text-primary-300' },
    { label: '代练', value: o.total_boosters, color: 'text-cyan-300' },
    { label: '总订单', value: o.total_orders, color: 'text-white' },
    { label: '总收入', value: `¥${o.total_revenue.toFixed(2)}`, color: 'text-accent-300' },
    { label: '待接单', value: o.pending_orders, color: 'text-yellow-300' },
    { label: '进行中', value: o.active_orders, color: 'text-blue-300' },
    { label: '已完成', value: o.completed_orders, color: 'text-green-300' },
    { label: '争议', value: o.disputed_orders, color: 'text-red-300' },
  ]
})

const orderTrendOption = computed(() => {
  if (!orderTrend.value?.points?.length) return null
  const pts = orderTrend.value.points
  return {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis' },
    legend: { data: ['订单数', '金额'], textStyle: { color: '#94a3b8' } },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: {
      type: 'category',
      data: pts.map((p) => p.date),
      axisLabel: { color: '#94a3b8', fontSize: 11 },
      axisLine: { lineStyle: { color: '#334155' } },
    },
    yAxis: [
      { type: 'value', name: '订单数', axisLabel: { color: '#94a3b8' }, splitLine: { lineStyle: { color: '#1e293b' } } },
      { type: 'value', name: '金额(¥)', axisLabel: { color: '#94a3b8' }, splitLine: { show: false } },
    ],
    series: [
      {
        name: '订单数',
        type: 'bar',
        data: pts.map((p) => p.count),
        itemStyle: { color: '#6366f1', borderRadius: [4, 4, 0, 0] },
      },
      {
        name: '金额',
        type: 'line',
        yAxisIndex: 1,
        data: pts.map((p) => p.revenue),
        smooth: true,
        lineStyle: { color: '#22d3ee', width: 2 },
        itemStyle: { color: '#22d3ee' },
        areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: 'rgba(34,211,238,0.25)' }, { offset: 1, color: 'rgba(34,211,238,0)' }] } },
      },
    ],
  }
})

const gameDistOption = computed(() => {
  if (!gameDist.value?.items?.length) return null
  const items = gameDist.value.items
  return {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'item', formatter: '{b}: {c}单 ({d}%)' },
    legend: { type: 'scroll', bottom: 0, textStyle: { color: '#94a3b8', fontSize: 11 } },
    series: [
      {
        type: 'pie',
        radius: ['35%', '65%'],
        center: ['50%', '45%'],
        avoidLabelOverlap: true,
        itemStyle: { borderRadius: 6, borderColor: '#0f172a', borderWidth: 2 },
        label: { color: '#e2e8f0', fontSize: 11 },
        emphasis: { label: { show: true, fontSize: 14, fontWeight: 'bold' } },
        data: items.map((g) => ({ value: g.count, name: g.game_name })),
      },
    ],
  }
})

const userGrowthOption = computed(() => {
  if (!userGrowth.value?.points?.length) return null
  const pts = userGrowth.value.points
  return {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis' },
    legend: { data: ['新增用户', '累计用户'], textStyle: { color: '#94a3b8' } },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: {
      type: 'category',
      data: pts.map((p) => p.date),
      axisLabel: { color: '#94a3b8', fontSize: 11 },
      axisLine: { lineStyle: { color: '#334155' } },
    },
    yAxis: [
      { type: 'value', name: '新增', axisLabel: { color: '#94a3b8' }, splitLine: { lineStyle: { color: '#1e293b' } } },
      { type: 'value', name: '累计', axisLabel: { color: '#94a3b8' }, splitLine: { show: false } },
    ],
    series: [
      {
        name: '新增用户',
        type: 'bar',
        data: pts.map((p) => p.new_users),
        itemStyle: { color: '#a78bfa', borderRadius: [4, 4, 0, 0] },
      },
      {
        name: '累计用户',
        type: 'line',
        yAxisIndex: 1,
        data: pts.map((p) => p.cumulative),
        smooth: true,
        lineStyle: { color: '#34d399', width: 2 },
        itemStyle: { color: '#34d399' },
      },
    ],
  }
})

async function fetchAll() {
  loading.value = true
  try {
    const [ovRes, trendRes, distRes, rankRes, growthRes] = await Promise.all([
      api.get('/admin/dashboard/overview'),
      api.get('/admin/dashboard/order-trend', { params: { period: trendPeriod.value, days: trendDays.value } }),
      api.get('/admin/dashboard/game-distribution'),
      api.get('/admin/dashboard/booster-ranking', { params: { limit: 10 } }),
      api.get('/admin/dashboard/user-growth', { params: { days: trendDays.value } }),
    ])
    overview.value = ovRes.data
    orderTrend.value = trendRes.data
    gameDist.value = distRes.data
    boosterRank.value = rankRes.data
    userGrowth.value = growthRes.data
  } catch {
    // handled by interceptor
  } finally {
    loading.value = false
  }
}

async function changeTrendPeriod(period) {
  trendPeriod.value = period
  try {
    const res = await api.get('/admin/dashboard/order-trend', { params: { period, days: trendDays.value } })
    orderTrend.value = res.data
  } catch {
    // ignore
  }
}

function levelColor(level) {
  return LEVEL_COLORS[level] || '#94a3b8'
}

onMounted(fetchAll)
</script>

<template>
  <div class="space-y-6">
    <!-- Loading -->
    <div v-if="loading" class="flex items-center justify-center py-16">
      <svg class="h-8 w-8 animate-spin text-primary-300" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
      </svg>
    </div>

    <template v-else>
      <!-- Overview cards -->
      <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <article v-for="card in overviewCards" :key="card.label" class="stat-card">
          <p class="text-sm text-slate-400">{{ card.label }}</p>
          <p class="mt-2 text-3xl font-semibold" :class="card.color">{{ card.value }}</p>
        </article>
      </div>

      <!-- Charts row: Order Trend + Game Distribution -->
      <div class="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
        <section class="surface-card p-5">
          <div class="flex flex-wrap items-center justify-between gap-3">
            <h3 class="text-lg font-semibold text-white">订单趋势</h3>
            <div class="flex gap-2">
              <button
                v-for="p in ['day', 'week', 'month']"
                :key="p"
                class="filter-pill text-xs"
                :class="trendPeriod === p ? 'filter-pill-active' : ''"
                @click="changeTrendPeriod(p)"
              >
                {{ p === 'day' ? '日' : p === 'week' ? '周' : '月' }}
              </button>
            </div>
          </div>
          <EChart v-if="orderTrendOption" :option="orderTrendOption" height="320px" class="mt-4" />
          <div v-else class="flex h-[320px] items-center justify-center text-slate-500">暂无数据</div>
        </section>

        <section class="surface-card p-5">
          <h3 class="text-lg font-semibold text-white">游戏分布</h3>
          <EChart v-if="gameDistOption" :option="gameDistOption" height="320px" class="mt-4" />
          <div v-else class="flex h-[320px] items-center justify-center text-slate-500">暂无数据</div>
        </section>
      </div>

      <!-- Charts row: User Growth -->
      <section class="surface-card p-5">
        <h3 class="text-lg font-semibold text-white">用户增长</h3>
        <EChart v-if="userGrowthOption" :option="userGrowthOption" height="280px" class="mt-4" />
        <div v-else class="flex h-[280px] items-center justify-center text-slate-500">暂无数据</div>
      </section>

      <!-- Booster ranking table -->
      <section class="surface-card p-5">
        <h3 class="text-lg font-semibold text-white">代练排行榜</h3>

        <div v-if="!boosterRank?.items?.length" class="empty-panel mt-4">暂无数据</div>

        <div v-else class="mt-4 overflow-x-auto">
          <table class="w-full text-left text-sm">
            <thead>
              <tr class="border-b border-white/10 text-xs uppercase tracking-wider text-slate-400">
                <th class="px-3 py-3">#</th>
                <th class="px-3 py-3">代练</th>
                <th class="px-3 py-3">信誉</th>
                <th class="px-3 py-3">等级</th>
                <th class="px-3 py-3">完成</th>
                <th class="px-3 py-3">评分</th>
                <th class="px-3 py-3">收入</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(b, idx) in boosterRank.items"
                :key="b.user_id"
                class="border-b border-white/5 transition-colors hover:bg-white/5 cursor-pointer"
                @click="router.push(`/booster/${b.user_id}`)"
              >
                <td class="px-3 py-3 font-semibold" :class="idx < 3 ? 'text-accent-300' : 'text-slate-400'">{{ idx + 1 }}</td>
                <td class="px-3 py-3">
                  <div class="flex items-center gap-2">
                    <div class="flex h-8 w-8 items-center justify-center rounded-xl border border-primary-300/30 bg-primary-500/10 text-sm font-semibold text-primary-100">
                      {{ b.username?.slice(0, 1) }}
                    </div>
                    <span class="text-white">{{ b.username }}</span>
                  </div>
                </td>
                <td class="px-3 py-3 text-white">{{ b.credit_score }}</td>
                <td class="px-3 py-3">
                  <span class="inline-block rounded-full px-2 py-0.5 text-xs font-semibold" :style="{ color: levelColor(b.credit_level), backgroundColor: levelColor(b.credit_level) + '20' }">
                    {{ b.credit_level }}
                  </span>
                </td>
                <td class="px-3 py-3 text-white">{{ b.total_completed }}</td>
                <td class="px-3 py-3 text-yellow-300">{{ b.avg_rating.toFixed(1) }}</td>
                <td class="px-3 py-3 text-accent-300">¥{{ b.total_revenue.toFixed(2) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </template>
  </div>
</template>
