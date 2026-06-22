<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { RouterLink } from 'vue-router'
import { Plus, UploadCloud, Search, Pencil, Trash2, ShieldCheck, X } from 'lucide-vue-next'
import { api, mediaUrl, type InheritorListItem, type Page } from '@/lib/api'
import { useDebounce } from '@/composables/useDebounce'
import { useAuthStore } from '@/stores/auth'
import Pagination from '@/components/Pagination.vue'
import Loading from '@/components/Loading.vue'
import Empty from '@/components/Empty.vue'

const auth = useAuthStore()

const keyword = ref('')
const debounced = useDebounce(keyword, 300)
const page = ref(1)
const size = 12
const result = ref<Page<InheritorListItem> | null>(null)
const loading = ref(false)
const error = ref<string | null>(null)

// 删除确认
const pending = ref<InheritorListItem | null>(null)
const deleting = ref(false)

async function fetchList() {
  loading.value = true
  error.value = null
  try {
    result.value = await api.listInheritors({
      keyword: debounced.value.trim() || null,
      page: page.value,
      size,
    })
  } catch (e) {
    error.value = e instanceof Error ? e.message : '加载失败'
  } finally {
    loading.value = false
  }
}

watch(debounced, () => {
  page.value = 1
  fetchList()
})

function onPageChange(p: number) {
  page.value = p
  fetchList()
}

async function confirmDelete() {
  if (!pending.value) return
  deleting.value = true
  try {
    await api.deleteInheritor(pending.value.id)
    pending.value = null
    // 若当前页删空且非首页，回退一页
    if (result.value && result.value.items.length === 1 && page.value > 1) {
      page.value--
    }
    await fetchList()
  } catch (e) {
    error.value = e instanceof Error ? e.message : '删除失败'
  } finally {
    deleting.value = false
  }
}

onMounted(fetchList)
</script>

<template>
  <div class="container py-8 md:py-12">
    <header class="mb-8 flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
      <div>
        <span class="label-eyebrow">ADMIN · 后台管理</span>
        <h1 class="section-title mt-2">传承人档案管理</h1>
        <div class="vermilion-divider mt-3" />
        <p class="mt-3 text-sm text-ink-500">
          <ShieldCheck class="mr-1 inline h-4 w-4 text-vermilion" />
          已登录：{{ auth.username }} · 可编辑与删除档案
        </p>
      </div>
      <div class="flex flex-wrap gap-2">
        <RouterLink to="/admin/inheritor/new" class="btn-primary">
          <Plus class="h-4 w-4" /> 新增传承人
        </RouterLink>
        <RouterLink to="/admin/import" class="btn-ghost">
          <UploadCloud class="h-4 w-4" /> 批量导入
        </RouterLink>
      </div>
    </header>

    <!-- 搜索 -->
    <div class="relative mb-4">
      <Search class="pointer-events-none absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-ink-400" />
      <input
        v-model="keyword"
        type="search"
        class="input-field pl-11"
        placeholder="搜索姓名 / 关键词…"
        style="min-height: 48px"
      />
    </div>

    <!-- 表格 -->
    <div class="paper-card overflow-hidden p-0">
      <Loading v-if="loading" text="加载档案…" />

      <div v-else-if="error" class="p-6 text-center text-sm text-vermilion">
        {{ error }}
      </div>

      <Empty
        v-else-if="!result || result.items.length === 0"
        title="暂无档案"
        description="点击「新增传承人」开始建档。"
      />

      <div v-else class="overflow-x-auto scrollbar-thin">
        <table class="w-full min-w-[640px] text-sm">
          <thead>
            <tr class="border-b border-ink-200 bg-paper-warm/60 text-left text-xs text-ink-500">
              <th class="px-4 py-3 font-medium">姓名</th>
              <th class="px-4 py-3 font-medium">剧种</th>
              <th class="px-4 py-3 font-medium">行当</th>
              <th class="px-4 py-3 font-medium">地区</th>
              <th class="px-4 py-3 font-medium">师承</th>
              <th class="px-4 py-3 text-right font-medium">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="item in result.items"
              :key="item.id"
              class="border-b border-ink-100 transition-colors last:border-0 hover:bg-paper-warm/40"
            >
              <td class="px-4 py-3">
                <div class="flex items-center gap-3">
                  <span
                    class="flex h-9 w-9 shrink-0 items-center justify-center overflow-hidden rounded-sm border border-ink-200 bg-paper-warm"
                  >
                    <img
                      v-if="mediaUrl(item.avatar)"
                      :src="mediaUrl(item.avatar)"
                      :alt="item.name"
                      class="h-full w-full object-cover"
                    />
                    <span v-else class="font-serif text-sm text-ink-400">{{ item.name?.charAt(0) }}</span>
                  </span>
                  <RouterLink
                    :to="`/inheritor/${item.id}`"
                    class="font-serif text-ink-900 hover:text-vermilion"
                  >{{ item.name }}</RouterLink>
                </div>
              </td>
              <td class="px-4 py-3 text-ink-600">{{ item.genre_name || '—' }}</td>
              <td class="px-4 py-3 text-ink-600">{{ item.role_type || '—' }}</td>
              <td class="px-4 py-3 text-ink-600">{{ item.region || '—' }}</td>
              <td class="px-4 py-3 text-ink-600">{{ item.master_name || '—' }}</td>
              <td class="px-4 py-3">
                <div class="flex items-center justify-end gap-1">
                  <RouterLink
                    :to="`/admin/inheritor/${item.id}/edit`"
                    class="flex h-8 w-8 items-center justify-center rounded-sm text-ink-500 hover:bg-ink-50 hover:text-vermilion"
                    title="编辑"
                  >
                    <Pencil class="h-4 w-4" />
                  </RouterLink>
                  <button
                    type="button"
                    class="flex h-8 w-8 items-center justify-center rounded-sm text-ink-500 hover:bg-vermilion/10 hover:text-vermilion"
                    title="删除"
                    @click="pending = item"
                  >
                    <Trash2 class="h-4 w-4" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="result" class="mt-6">
      <Pagination :page="result.page" :page-size="result.size" :total="result.total" @change="onPageChange" />
    </div>

    <!-- 删除确认对话框 -->
    <transition name="fade">
      <div
        v-if="pending"
        class="fixed inset-0 z-50 flex items-center justify-center bg-ink-900/50 p-4"
        @click.self="pending = null"
      >
        <div class="paper-card w-full max-w-sm">
          <div class="flex items-center justify-between">
            <h3 class="display-serif text-lg text-ink-900">确认删除</h3>
            <button class="text-ink-400 hover:text-ink-900" @click="pending = null">
              <X class="h-5 w-5" />
            </button>
          </div>
          <p class="mt-3 text-sm leading-relaxed text-ink-600">
            确定要删除传承人「<span class="font-serif text-vermilion">{{ pending.name }}</span
            >」的档案吗？此操作不可撤销。
          </p>
          <div class="mt-6 flex justify-end gap-2">
            <button class="btn-ghost" @click="pending = null">取消</button>
            <button class="btn-primary" :disabled="deleting" @click="confirmDelete">
              <Trash2 class="h-4 w-4" /> {{ deleting ? '删除中…' : '确认删除' }}
            </button>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
