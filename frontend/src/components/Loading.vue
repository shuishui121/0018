<script setup lang="ts">
import { LoaderCircle } from 'lucide-vue-next'

withDefaults(
  defineProps<{
    text?: string
    size?: number
  }>(),
  { text: '加载中', size: 24 },
)
</script>

<template>
  <div
    class="flex flex-col items-center justify-center gap-3 px-6 py-16 text-center"
  >
    <LoaderCircle
      class="animate-spin text-vermilion"
      :style="{ width: size + 'px', height: size + 'px' }"
    />
    <p class="text-sm text-ink-400">{{ text }}</p>
  </div>
</template>
