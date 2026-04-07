<script setup>
defineProps({
  eyebrow: {
    type: String,
    default: '',
  },
  title: {
    type: String,
    default: '',
  },
  description: {
    type: String,
    default: '',
  },
  spotlightLabel: {
    type: String,
    default: '',
  },
  spotlightTitle: {
    type: String,
    default: '',
  },
  spotlightMeta: {
    type: String,
    default: '',
  },
  backgroundUrl: {
    type: String,
    default: '',
  },
  compact: {
    type: Boolean,
    default: false,
  },
})
</script>

<template>
  <div
    class="auth-stage"
    :style="backgroundUrl ? { backgroundImage: `url('${backgroundUrl}')` } : undefined"
  >
    <div class="auth-stage__backdrop"></div>
    <div class="auth-stage__mesh"></div>

    <div class="auth-stage__inner shell-container">
      <section class="auth-story">
        <p v-if="eyebrow" class="auth-story__eyebrow">{{ eyebrow }}</p>
        <h1 :class="compact ? 'auth-story__title auth-story__title-compact' : 'auth-story__title'">{{ title }}</h1>
        <p v-if="description" class="auth-story__copy">{{ description }}</p>

        <div v-if="spotlightTitle" class="auth-story__spotlight">
          <p class="auth-story__label">{{ spotlightLabel }}</p>
          <h2>{{ spotlightTitle }}</h2>
          <p>{{ spotlightMeta }}</p>
        </div>
      </section>

      <section class="auth-panel">
        <slot />
      </section>
    </div>
  </div>
</template>
