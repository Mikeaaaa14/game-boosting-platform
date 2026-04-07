<script setup>
import { PAGE_BACKGROUNDS } from '@/data/gameImages.js'
</script>

<template>
  <div class="page-shell">
    <section
      class="hero-panel scanline-overlay flex min-h-[70vh] items-center p-8 sm:p-10 lg:p-14"
      :style="{
        backgroundImage: `linear-gradient(135deg, rgba(10,10,15,0.93), rgba(18,18,26,0.9)), url('${PAGE_BACKGROUNDS.notFound}')`,
        backgroundPosition: 'center',
        backgroundSize: 'cover',
      }"
    >
      <div class="mx-auto max-w-xl space-y-6 text-center">
        <div
          class="glitch-text text-8xl font-black animate-glitch sm:text-9xl"
          data-text="404"
          style="color: #00f0ff;"
        >
          404
        </div>
        <h2 class="section-title neon-text">页面未找到</h2>
        <div class="flex flex-wrap items-center justify-center gap-4 pt-4">
          <router-link to="/" class="btn-primary clip-angle-sm">
            返回
          </router-link>
        </div>
      </div>
    </section>
  </div>
</template>
