<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter, RouterLink } from 'vue-router'
import { ArrowLeft, Quote, Landmark, Users } from 'lucide-vue-next'
import { api, mediaUrl, type GenreDetail } from '@/lib/api'
import { useAsync } from '@/composables/useAsync'
import SectionHeader from '@/components/SectionHeader.vue'
import InheritorCard from '@/components/InheritorCard.vue'
import Loading from '@/components/Loading.vue'
import Empty from '@/components/Empty.vue'

const route = useRoute()
const router = useRouter()
const id = computed(() => Number(route.params.id))

const { data: genre, loading, error } = useAsync(
  () => api.getGenre(id.value),
)

// 将「、，,;」等分隔的文本拆为条目
function splitItems(text: string | null | undefined): string[] {
  if (!text) return []
  return text
    .split(/[、，,;；\n]+/)
    .map((s) => s.trim())
    .filter(Boolean)
}

const classicPlays = computed(() => splitItems(genre.value?.classic_plays))
const schools = computed(() => splitItems(genre.value?.main_schools))
const areas = computed(() => splitItems(genre.value?.distribution_areas))
const coverUrl = computed(() => mediaUrl(genre.value?.cover_image))
// 引用块：取历史渊源首句作为导语
const leadQuote = computed(() => {
  const h = genre.value?.history
  if (!h) return null
  return h.split(/[。！！\n]/)[0]?.trim() || null
})
const activeInheritors = computed(() => (genre.value?.inheritors ?? []).slice(0, 8))
</script>

<template>
  <div class="container py-8 md:py-12">
    <button class="btn-ghost mb-6" @click="router.back()">
      <ArrowLeft class="h-4 w-4" /> 返回剧种
    </button>

    <Loading v-if="loading" text="正在展卷…" />
    <div v-else-if="error" class="paper-card text-center text-vermilion">
      {{ error }}
    </div>

    <template v-else-if="genre">
      <!-- 头图 -->
      <section class="paper-card relative overflow-hidden p-0">
        <div class="relative aspect-[21/9] w-full">
          <img
            v-if="coverUrl"
            :src="coverUrl"
            :alt="genre.name"
            class="h-full w-full object-cover"
          />
          <div
            v-else
            class="flex h-full w-full items-center justify-center"
            style="background: linear-gradient(135deg, #332E27, #241F1A)"
          >
            <span class="font-seal text-7xl text-paper/25">{{ genre.name?.charAt(0) }}</span>
          </div>
          <div class="absolute inset-0 bg-gradient-to-t from-ink-900/80 to-transparent" />
          <div class="absolute bottom-0 left-0 p-6 md:p-8">
            <span class="label-eyebrow !text-gold-light">GENRE · 剧种</span>
            <h1 class="display-serif mt-2 text-4xl text-paper md:text-6xl">{{ genre.name }}</h1>
            <p v-if="genre.pinyin" class="mt-1 font-seal text-paper/70">pinyin · {{ genre.pinyin }}</p>
          </div>
        </div>
      </section>

      <!-- 引用块 -->
      <section v-if="leadQuote" class="mt-8">
        <blockquote class="paper-card relative border-l-4 border-vermilion pl-8">
          <Quote class="absolute -left-2 -top-2 h-6 w-6 text-vermilion/30" />
          <p class="font-serif text-lg leading-relaxed text-ink-700">{{ leadQuote }}</p>
        </blockquote>
      </section>

      <!-- 历史渊源 -->
      <section v-if="genre.history" class="mt-10">
        <SectionHeader index="01" eyebrow="ORIGIN" title="历史渊源" />
        <p class="paper-card mt-4 whitespace-pre-line text-sm leading-relaxed text-ink-600">
          {{ genre.history }}
        </p>
      </section>

      <!-- 艺术特点 -->
      <section v-if="genre.art_features" class="mt-10">
        <SectionHeader index="02" eyebrow="FEATURES" title="艺术特点" />
        <p class="paper-card mt-4 whitespace-pre-line text-sm leading-relaxed text-ink-600">
          {{ genre.art_features }}
        </p>
      </section>

      <!-- 经典剧目 -->
      <section v-if="classicPlays.length" class="mt-10">
        <SectionHeader index="03" eyebrow="REPERTOIRE" title="经典剧目" />
        <div class="mt-4 grid grid-cols-1 gap-2 sm:grid-cols-2 lg:grid-cols-3">
          <div
            v-for="(p, i) in classicPlays"
            :key="i"
            class="paper-card flex items-center gap-2"
          >
            <span class="font-seal text-gold">{{ String(i + 1).padStart(2, '0') }}</span>
            <span class="font-serif text-ink-800">{{ p }}</span>
          </div>
        </div>
      </section>

      <!-- 主要流派 -->
      <section v-if="schools.length" class="mt-10">
        <SectionHeader index="04" eyebrow="SCHOOLS" title="主要流派" />
        <div class="mt-4 flex flex-wrap gap-2">
          <span v-for="(s, i) in schools" :key="i" class="chip !py-1.5 font-serif">{{ s }}</span>
        </div>
      </section>

      <!-- 分布地区 -->
      <section v-if="areas.length" class="mt-10">
        <SectionHeader index="05" eyebrow="REGIONS" title="分布地区" />
        <div class="mt-4 flex flex-wrap gap-2">
          <span v-for="(a, i) in areas" :key="i" class="chip chip-active !py-1.5 font-serif">{{ a }}</span>
        </div>
      </section>

      <!-- 关联活跃传承人 -->
      <section class="mt-12">
        <div class="mb-4 flex items-center gap-2">
          <Users class="h-5 w-5 text-vermilion" />
          <h2 class="section-title !text-xl">活跃传承人</h2>
        </div>
        <div v-if="activeInheritors.length" class="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
          <InheritorCard v-for="item in activeInheritors" :key="item.id" :inheritor="item" />
        </div>
        <Empty v-else title="暂无关联传承人" description="该剧种尚未录入活跃传承人。" />
      </section>

      <!-- 关联现存剧团 -->
      <section class="mt-10">
        <div class="mb-4 flex items-center gap-2">
          <Landmark class="h-5 w-5 text-vermilion" />
          <h2 class="section-title !text-xl">现存剧团</h2>
        </div>
        <div v-if="genre.troupes?.length" class="space-y-2">
          <RouterLink
            v-for="t in genre.troupes"
            :key="t.id"
            :to="`/directory?region=${t.region || ''}`"
            class="paper-card paper-card-hover flex items-center gap-3"
          >
            <Landmark class="h-5 w-5 shrink-0 text-gold" />
            <div class="min-w-0 flex-1">
              <p class="font-serif text-ink-900">{{ t.name }}</p>
              <p v-if="t.description" class="truncate text-xs text-ink-400">{{ t.description }}</p>
            </div>
            <span v-if="t.region" class="chip">{{ t.region }}</span>
          </RouterLink>
        </div>
        <Empty v-else title="暂无剧团" description="该剧种尚未录入现存剧团。" />
      </section>
    </template>
  </div>
</template>
