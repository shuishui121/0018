<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import { BookOpen } from 'lucide-vue-next'
import { api, mediaUrl, type Genre } from '@/lib/api'
import { useAsync } from '@/composables/useAsync'
import SealBadge from '@/components/SealBadge.vue'
import Loading from '@/components/Loading.vue'
import Empty from '@/components/Empty.vue'

const { data: genres, loading, error } = useAsync(() => api.listGenres())

const sorted = computed(() => genres.value ?? [])
</script>

<template>
  <div class="container py-8 md:py-12">
    <header class="mb-8">
      <span class="label-eyebrow">GENRES · 剧种百科</span>
      <h1 class="section-title mt-2">戏曲剧种</h1>
      <div class="vermilion-divider mt-3" />
      <p class="mt-4 max-w-2xl text-sm leading-relaxed text-ink-500">
        中国戏曲剧种繁多，声腔各异。点击卡片进入剧种详情，查阅其历史渊源、艺术特点与流派传承。
      </p>
    </header>

    <Loading v-if="loading" text="正在汇集剧种…" />

    <div v-else-if="error" class="paper-card text-center text-vermilion">
      {{ error }}
    </div>

    <Empty
      v-else-if="sorted.length === 0"
      title="暂无剧种"
      description="尚未收录任何剧种资料。"
    />

    <div v-else class="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-4">
      <RouterLink
        v-for="(g, i) in sorted"
        :key="g.id"
        :to="`/genres/${g.id}`"
        class="paper-card paper-card-hover group block overflow-hidden p-0"
      >
        <div class="relative aspect-[3/4] overflow-hidden">
          <!-- 封面 -->
          <img
            v-if="mediaUrl(g.cover_image)"
            :src="mediaUrl(g.cover_image)"
            :alt="g.name"
            loading="lazy"
            class="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
          />
          <div
            v-else
            class="flex h-full w-full items-center justify-center"
            style="background: linear-gradient(135deg, #332E27, #4A4339)"
          >
            <span class="font-seal text-6xl text-paper/30">{{ g.name?.charAt(0) }}</span>
          </div>

          <!-- 渐隐遮罩 -->
          <div class="absolute inset-0 bg-gradient-to-t from-ink-900/70 via-ink-900/10 to-transparent" />

          <!-- 编号 -->
          <span
            class="absolute left-3 top-3 rounded-sm bg-paper/80 px-2 py-0.5 font-seal text-sm text-vermilion backdrop-blur"
          >
            {{ String(i + 1).padStart(2, '0') }}
          </span>

          <!-- 竖排标题 -->
          <div class="absolute bottom-0 right-0 flex h-full items-end justify-end p-4">
            <h3
              class="font-serif text-2xl font-bold text-paper drop-shadow-lg"
              style="writing-mode: vertical-rl; letter-spacing: 0.15em"
            >
              {{ g.name }}
            </h3>
          </div>
        </div>
      </RouterLink>
    </div>
  </div>
</template>
