<script setup lang="ts">
import { PINYIN_INITIALS } from '@/lib/options'

// 拼音首字母索引条：点击触发选中，移动端横向滚动
const props = withDefaults(
  defineProps<{
    active?: string | null
  }>(),
  { active: null },
)

const emit = defineEmits<{
  (e: 'select', initial: string | null): void
}>()

function pick(initial: string | null) {
  emit('select', initial)
}
</script>

<template>
  <div class="paper-card flex items-center gap-1 overflow-x-auto p-2 scrollbar-thin">
    <button
      type="button"
      class="shrink-0 rounded-sm px-2.5 py-1.5 text-xs font-medium transition-colors"
      :class="
        active === null
          ? 'bg-vermilion text-paper'
          : 'text-ink-500 hover:bg-ink-50 hover:text-ink-900'
      "
      style="min-height: 44px; min-width: 44px"
      @click="pick(null)"
    >
      全部
    </button>
    <button
      v-for="letter in PINYIN_INITIALS"
      :key="letter"
      type="button"
      class="shrink-0 rounded-sm px-2 py-1.5 font-serif text-sm transition-colors"
      :class="
        active === letter
          ? 'bg-vermilion text-paper'
          : 'text-ink-600 hover:bg-ink-50 hover:text-vermilion'
      "
      style="min-height: 44px; min-width: 44px"
      :aria-pressed="active === letter"
      @click="pick(letter)"
    >
      {{ letter }}
    </button>
  </div>
</template>
