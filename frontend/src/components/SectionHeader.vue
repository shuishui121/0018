<script setup lang="ts">
import { computed } from 'vue'

// 章节标题：可选眉标、编号、朱砂分隔线
const props = withDefaults(
  defineProps<{
    title: string
    eyebrow?: string
    index?: string | number
    divider?: boolean
    align?: 'left' | 'center'
  }>(),
  { divider: true, align: 'left' },
)

const alignClass = computed(() =>
  props.align === 'center' ? 'items-center text-center' : 'items-start',
)
</script>

<template>
  <div class="flex flex-col gap-2" :class="alignClass">
    <div v-if="eyebrow || index" class="flex items-baseline gap-3">
      <span
        v-if="index !== undefined"
        class="font-seal text-lg text-gold"
        >{{ String(index).padStart(2, '0') }}</span
      >
      <span v-if="eyebrow" class="label-eyebrow">{{ eyebrow }}</span>
    </div>
    <h2 class="section-title">{{ title }}</h2>
    <div v-if="divider" class="vermilion-divider mt-1" />
  </div>
</template>
