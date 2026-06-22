<script setup lang="ts">
import { Inbox } from 'lucide-vue-next'

// 空状态：图标 + 标题 + 描述，居中留白
withDefaults(
  defineProps<{
    title?: string
    description?: string
  }>(),
  { title: '暂无数据', description: '未能找到符合条件的记录' },
)
</script>

<template>
  <div
    class="flex flex-col items-center justify-center gap-3 px-6 py-16 text-center"
  >
    <div
      class="flex h-16 w-16 items-center justify-center rounded-full border border-ink-200 bg-paper-warm/60"
    >
      <Inbox class="h-7 w-7 text-ink-300" />
    </div>
    <p class="font-serif text-base text-ink-600">{{ title }}</p>
    <p class="max-w-xs text-sm text-ink-400">{{ description }}</p>
  </div>
</template>
