import { reactive } from 'vue'
import type { InheritorFilters } from '@/lib/api'

// 名录筛选默认值：默认第 1 页、每页 12 条
const DEFAULTS: InheritorFilters = {
  keyword: null,
  genre: null,
  role: null,
  region: null,
  master: null,
  age_group: null,
  pinyin: null,
  page: 1,
  size: 12,
}

// 集中管理名录筛选条件，提供重置方法
export function useFilters(initial: Partial<InheritorFilters> = {}) {
  const filters = reactive<InheritorFilters>({ ...DEFAULTS, ...initial })

  function reset() {
    Object.assign(filters, DEFAULTS)
  }

  function patch(partial: Partial<InheritorFilters>) {
    Object.assign(filters, partial)
  }

  return { filters, reset, patch }
}
