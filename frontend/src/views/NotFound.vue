<template>
  <div class="page-shell">
    <section class="hero-panel p-8 sm:p-10 lg:p-14">
      <div class="mx-auto max-w-3xl text-center">
        <p class="eyebrow">404</p>
        <h1 class="mt-6 text-5xl font-semibold tracking-[-0.04em] text-white sm:text-6xl">
          这个地址暂时打不开，去看看正在进行的服务吧。
        </h1>
        <p class="mx-auto mt-5 max-w-2xl text-sm leading-7 text-slate-400 sm:text-base">
          链接可能已经变更，或者这个页面暂时不可用。你可以返回首页重新浏览，也可以直接进入订单大厅继续下单或接单。
        </p>

        <div class="mt-10 flex flex-col justify-center gap-3 sm:flex-row">
          <router-link to="/" class="btn-primary px-6 py-3">
            返回首页
          </router-link>
          <router-link to="/orders" class="btn-secondary px-6 py-3">
            前往订单大厅
          </router-link>
        </div>
      </div>
    </section>
  </div>
</template>
