<script setup lang="ts">
const year = new Date().getFullYear()
</script>

<template>
  <footer class="mt-16 border-t border-ink-200/60 bg-ink-50/60">
    <div
      class="container flex flex-col items-center gap-2 py-8 text-center md:flex-row md:justify-between md:text-left"
    >
      <div class="flex items-center gap-2">
        <span class="seal-stamp h-6 w-6 rounded-sm text-xs">藏</span>
        <span class="font-serif text-sm text-ink-700">梨园典藏</span>
      </div>
      <p class="text-xs text-ink-400">
        省非物质文化遗产保护中心 · 戏曲传承人口齿录管理系统 ©
        {{ year }}
      </p>
    </div>
  </footer>
</template>
