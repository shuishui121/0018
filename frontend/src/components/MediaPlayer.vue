<script setup lang="ts">
import { computed } from 'vue'
import { Music, Video } from 'lucide-vue-next'
import { mediaUrl, type Media } from '@/lib/api'

const props = defineProps<{ media: Media }>()

// 依据 type 字段判断视频/音频；视频优先按扩展名兜底
const isVideo = computed(() => {
  const t = (props.media.type || '').toLowerCase()
  const p = (props.media.file_path || '').toLowerCase()
  return t.includes('video') || /\.(mp4|webm|mov|m4v)(\?|$)/.test(p)
})

const url = computed(() => mediaUrl(props.media.file_path))
</script>

<template>
  <div class="paper-card paper-card-hover">
    <div class="mb-3 flex items-center gap-2">
      <component
        :is="isVideo ? Video : Music"
        class="h-4 w-4 text-vermilion"
      />
      <span class="font-serif text-sm text-ink-800">{{
        media.title || '未命名资料'
      }}</span>
      <span class="ml-auto chip">{{ isVideo ? '影像' : '声腔' }}</span>
    </div>

    <video
      v-if="isVideo && url"
      :src="url"
      controls
      preload="metadata"
      class="aspect-video w-full rounded-sm bg-ink-900"
    />
    <audio v-else-if="url" :src="url" controls preload="metadata" class="w-full" />
    <div
      v-else
      class="flex aspect-video w-full items-center justify-center rounded-sm bg-ink-100 text-xs text-ink-400"
    >
      暂无可用媒体文件
    </div>

    <p v-if="media.description" class="mt-3 text-xs leading-relaxed text-ink-500">
      {{ media.description }}
    </p>
  </div>
</template>
