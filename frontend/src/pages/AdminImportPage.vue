<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import {
  UploadCloud,
  FileSpreadsheet,
  CheckCircle2,
  XCircle,
  Clock,
  LoaderCircle,
  ArrowLeft,
} from 'lucide-vue-next'
import { api, type BatchImportResult } from '@/lib/api'

const router = useRouter()

const dragOver = ref(false)
const file = ref<File | null>(null)
const importing = ref(false)
const result = ref<BatchImportResult | null>(null)
const errorMsg = ref<string | null>(null)

const accept = '.xlsx,.xls,.csv'

function setFile(f: File | undefined) {
  errorMsg.value = null
  result.value = null
  file.value = f || null
}

function onDrop(e: DragEvent) {
  dragOver.value = false
  const f = e.dataTransfer?.files?.[0]
  if (f) setFile(f)
}

function onSelect(e: Event) {
  const f = (e.target as HTMLInputElement).files?.[0]
  if (f) setFile(f)
}

async function doImport() {
  if (!file.value) return
  importing.value = true
  errorMsg.value = null
  result.value = null
  try {
    result.value = await api.batchImport(file.value)
  } catch (err) {
    errorMsg.value = err instanceof Error ? err.message : '导入失败'
  } finally {
    importing.value = false
  }
}

const elapsedText = computed(() => {
  if (!result.value) return ''
  const ms = result.value.elapsed_ms
  return ms >= 1000 ? (ms / 1000).toFixed(2) + ' 秒' : ms + ' 毫秒'
})

// 颜色映射用完整类名字面量，确保 Tailwind 能扫描生成
const toneClass: Record<string, string> = {
  ink: 'text-ink',
  celadon: 'text-celadon',
  vermilion: 'text-vermilion',
  gold: 'text-gold',
}

const summary = computed(() => {
  if (!result.value) return []
  const r = result.value
  return [
    { label: '总条数', value: r.total, icon: FileSpreadsheet, tone: 'ink' },
    { label: '成功', value: r.success, icon: CheckCircle2, tone: 'celadon' },
    { label: '失败', value: r.failed, icon: XCircle, tone: 'vermilion' },
    { label: '耗时', value: elapsedText.value, icon: Clock, tone: 'gold' },
  ]
})
</script>

<template>
  <div class="container py-8 md:py-12">
    <button class="btn-ghost mb-6" @click="router.push('/admin')">
      <ArrowLeft class="h-4 w-4" /> 返回列表
    </button>

    <header class="mb-8">
      <span class="label-eyebrow">IMPORT · 批量导入</span>
      <h1 class="section-title mt-2">Excel 批量导入</h1>
      <div class="vermilion-divider mt-3" />
      <p class="mt-3 text-sm text-ink-500">
        支持 .xlsx / .xls / .csv 文件，拖拽到下方区域或点击选择文件后开始导入。
      </p>
    </header>

    <!-- 拖拽上传区 -->
    <div
      class="paper-card flex flex-col items-center justify-center gap-4 border-2 border-dashed !border-ink-300 py-16 text-center transition-colors"
      :class="{ '!border-vermilion bg-vermilion/5': dragOver }"
      @dragover.prevent="dragOver = true"
      @dragleave.prevent="dragOver = false"
      @drop.prevent="onDrop"
    >
      <div
        class="flex h-16 w-16 items-center justify-center rounded-full bg-vermilion/10 text-vermilion"
      >
        <UploadCloud class="h-8 w-8" />
      </div>
      <div>
        <p class="font-serif text-lg text-ink-800">将文件拖拽到此处</p>
        <p class="mt-1 text-xs text-ink-400">或点击下方按钮选择文件</p>
      </div>

      <label class="btn-ghost cursor-pointer">
        <FileSpreadsheet class="h-4 w-4" /> 选择文件
        <input type="file" :accept="accept" class="hidden" @change="onSelect" />
      </label>

      <!-- 已选文件 -->
      <div v-if="file" class="mt-2 flex items-center gap-2 rounded-sm bg-paper-warm px-3 py-1.5 text-xs text-ink-600">
        <FileSpreadsheet class="h-4 w-4 text-celadon" />
        <span class="font-serif">{{ file.name }}</span>
        <span class="text-ink-400">({{ (file.size / 1024).toFixed(1) }} KB)</span>
      </div>
    </div>

    <!-- 操作 -->
    <div class="mt-6 flex items-center justify-center gap-3">
      <button class="btn-primary min-w-40" :disabled="!file || importing" @click="doImport">
        <LoaderCircle v-if="importing" class="h-4 w-4 animate-spin" />
        <UploadCloud v-else class="h-4 w-4" />
        {{ importing ? '导入中…' : '开始导入' }}
      </button>
    </div>

    <!-- 进度反馈 -->
    <transition name="fade">
      <div v-if="importing" class="paper-card mt-6">
        <div class="flex items-center gap-2 text-sm text-ink-600">
          <LoaderCircle class="h-4 w-4 animate-spin text-vermilion" />
          正在解析并写入档案，请稍候…
        </div>
        <div class="mt-3 h-1.5 w-full overflow-hidden rounded-full bg-ink-100">
          <div class="h-full w-1/3 animate-pulse rounded-full bg-vermilion" style="animation-duration: 1.2s" />
        </div>
      </div>
    </transition>

    <!-- 错误 -->
    <div v-if="errorMsg" class="paper-card mt-6 text-center text-sm text-vermilion">
      {{ errorMsg }}
    </div>

    <!-- 导入结果 -->
    <transition name="fade">
      <section v-if="result" class="mt-8">
        <h2 class="section-title !text-xl">导入结果</h2>
        <div class="vermilion-divider mt-2" />
        <div class="mt-4 grid grid-cols-2 gap-3 md:grid-cols-4">
          <div v-for="s in summary" :key="s.label" class="paper-card flex items-center gap-3">
            <component :is="s.icon" class="h-5 w-5" :class="toneClass[s.tone]" />
            <div>
              <p class="display-serif text-2xl text-ink-900">{{ s.value }}</p>
              <p class="text-xs text-ink-500">{{ s.label }}</p>
            </div>
          </div>
        </div>

        <!-- 错误明细 -->
        <div v-if="result.errors.length" class="paper-card mt-4">
          <h3 class="mb-2 flex items-center gap-2 font-serif text-ink-800">
            <XCircle class="h-4 w-4 text-vermilion" />错误明细（{{ result.errors.length }}）
          </h3>
          <ul class="max-h-60 space-y-1 overflow-y-auto pr-2 text-xs text-ink-500 scrollbar-thin">
            <li
              v-for="(err, i) in result.errors"
              :key="i"
              class="border-b border-ink-100 py-1.5 last:border-0"
            >
              {{ err }}
            </li>
          </ul>
        </div>
      </section>
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
