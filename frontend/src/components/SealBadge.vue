<script setup lang="ts">
import { computed } from 'vue'

// 印章式角标：复用全局 .seal-stamp 样式，仅控制尺寸
const props = withDefaults(
  defineProps<{
    text: string
    size?: 'sm' | 'md' | 'lg'
    rotate?: boolean
  }>(),
  { size: 'md', rotate: true },
)

const sizeClass = computed(
  () =>
    ({
      sm: 'h-8 w-8 text-sm',
      md: 'h-11 w-11 text-base',
      lg: 'h-16 w-16 text-xl',
    })[props.size],
)
</script>

<template>
  <span
    class="seal-stamp select-none rounded-sm font-seal leading-none"
    :class="[sizeClass, { '!rotate-0': !rotate }]"
    aria-hidden="true"
  >
    {{ text }}
  </span>
</template>
