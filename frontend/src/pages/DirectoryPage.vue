<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { Search, SlidersHorizontal } from 'lucide-vue-next'
import { api, type InheritorListItem, type Genre, type Page } from '@/lib/api'
import { useDebounce } from '@/composables/useDebounce'
import { useFilters } from '@/composables/useFilters'
import InheritorCard from '@/components/InheritorCard.vue'
import FilterBar from '@/components/FilterBar.vue'
import PinyinBar from '@/components/PinyinBar.vue'
import Pagination from '@/components/Pagination.vue'
import Empty from '@/components/Empty.vue'
import Loading from '@/components/Loading.vue'

// 筛选状态
const { filters } = useFilters()

// 搜索：输入即时、300ms 防抖
const keyword = ref('')
const debouncedKeyword = useDebounce(keyword, 300)

// 下拉与师承建议所需的基础数据
const genres = ref<Genre[]>([])
const masters = ref<InheritorListItem[]>([])

// 列表结果
const result = ref<Page<InheritorListItem> | null>(null)
const loading = ref(false)
const error = ref<string | null>(null)
const gridRef = ref<HTMLElement | null>(null)

async function fetchList() {
  loading.value = true
  error.value = null
  try {
    result.value = await api.listInheritors({ ...filters })
  } catch (e) {
    error.value = e instanceof Error ? e.message : '加载失败'
  } finally {
    loading.value = false
  }
}

// 搜索词变化：写入 keyword 筛选并回到首页
watch(debouncedKeyword, (val) => {
  filters.keyword = val.trim() || null
  filters.page = 1
  fetchList()
})

function onFilterChange() {
  fetchList()
}

function onSelectPinyin(initial: string | null) {
  filters.pinyin = initial
  filters.page = 1
  fetchList()
  scrollToGrid()
}

function onPageChange(p: number) {
  filters.page = p
  fetchList()
  scrollToGrid()
}

function scrollToGrid() {
  gridRef.value?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

onMounted(async () => {
  // 并行加载基础数据与首屏列表
  fetchList()
  try {
    const [g, m] = await Promise.all([
      api.listGenres(),
      api.listInheritors({ size: 200 }),
    ])
    genres.value = g
    masters.value = m.items
  } catch {
    /* 下拉数据失败不阻塞主列表 */
  }
})
</script>

<template>
  <div class="container py-8 md:py-12">
    <!-- 标题 -->
    <header class="mb-8">
      <span class="label-eyebrow">DIRECTORY · 名录查询</span>
      <h1 class="section-title mt-2">传承人名录</h1>
      <div class="vermilion-divider mt-3" />
    </header>

    <!-- 搜索框 -->
    <div class="relative mb-4">
      <Search class="pointer-events-none absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-ink-400" />
      <input
        v-model="keyword"
        type="search"
        class="input-field pl-11"
        placeholder="输入姓名 / 剧种 / 关键词，模糊检索…"
        style="min-height: 48px"
      />
    </div>

    <!-- 多维筛选条 -->
    <FilterBar
      :filters="filters"
      :genres="genres"
      :masters="masters"
      @change="onFilterChange"
    />

    <!-- 拼音索引条 -->
    <div class="mt-4">
      <PinyinBar :active="filters.pinyin" @select="onSelectPinyin" />
    </div>

    <!-- 结果区 -->
    <div ref="gridRef" class="mt-8 scroll-mt-24">
      <div class="mb-4 flex items-center justify-between">
        <p class="text-sm text-ink-500">
          <SlidersHorizontal class="mr-1 inline h-3.5 w-3.5" />
          共 <span class="font-serif text-ink-800">{{ result?.total ?? 0 }}</span> 位传承人
        </p>
      </div>

      <Loading v-if="loading" text="正在调阅档案…" />

      <div v-else-if="error" class="paper-card text-center text-sm text-vermilion">
        {{ error }}
      </div>

      <Empty
        v-else-if="!result || result.items.length === 0"
        title="未寻得传承人"
        description="请调整筛选条件或拼音首字母后重试。"
      />

      <template v-else>
        <div class="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
          <InheritorCard
            v-for="item in result.items"
            :key="item.id"
            :inheritor="item"
          />
        </div>

        <div class="mt-8">
          <Pagination
            :page="result.page"
            :page-size="result.size"
            :total="result.total"
            @change="onPageChange"
          />
        </div>
      </template>
    </div>
  </div>
</template>
