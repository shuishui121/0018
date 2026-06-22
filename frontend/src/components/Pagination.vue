<script setup lang="ts">
import { computed } from 'vue'
import { ChevronLeft, ChevronRight } from 'lucide-vue-next'

// 通用分页：展示页码窗口，移动端仅显示首尾与当前
const props = defineProps<{
  page: number
  pageSize: number
  total: number
}>()

const emit = defineEmits<{ (e: 'change', page: number): void }>()

const totalPages = computed(() =>
  Math.max(1, Math.ceil(props.total / props.pageSize)),
)

const window = computed(() => {
  const pages: (number | '…')[] = []
  const cur = props.page
  const last = totalPages.value
  if (last <= 7) {
    for (let i = 1; i <= last; i++) pages.push(i)
    return pages
  }
  pages.push(1)
  const start = Math.max(2, cur - 1)
  const end = Math.min(last - 1, cur + 1)
  if (start > 2) pages.push('…')
  for (let i = start; i <= end; i++) pages.push(i)
  if (end < last - 1) pages.push('…')
  pages.push(last)
  return pages
})

function go(p: number) {
  if (p < 1 || p > totalPages.value || p === props.page) return
  emit('change', p)
}
</script>

<template>
  <nav
    v-if="totalPages > 1"
    class="flex items-center justify-center gap-1"
    aria-label="分页"
  >
    <button
      type="button"
      class="flex h-10 w-10 items-center justify-center rounded-sm text-ink-500 transition-colors hover:bg-ink-50 disabled:opacity-40"
      style="min-width: 44px"
      :disabled="page <= 1"
      @click="go(page - 1)"
    >
      <ChevronLeft class="h-4 w-4" />
    </button>
    <template v-for="(p, i) in window" :key="i">
      <span
        v-if="p === '…'"
        class="px-1 text-ink-300"
        >…</span
      >
      <button
        v-else
        type="button"
        class="h-10 w-10 rounded-sm font-serif text-sm transition-colors"
        style="min-width: 44px; min-height: 44px"
        :class="
          p === page
            ? 'bg-vermilion text-paper'
            : 'text-ink-600 hover:bg-ink-50 hover:text-ink-900'
        "
        @click="go(p as number)"
      >
        {{ p }}
      </button>
    </template>
    <button
      type="button"
      class="flex h-10 w-10 items-center justify-center rounded-sm text-ink-500 transition-colors hover:bg-ink-50 disabled:opacity-40"
      style="min-width: 44px"
      :disabled="page >= totalPages"
      @click="go(page + 1)"
    >
      <ChevronRight class="h-4 w-4" />
    </button>
  </nav>
</template>
