<script setup lang="ts">
import { computed, watch } from 'vue'
import { useRoute, useRouter, RouterLink } from 'vue-router'
import { ArrowLeft, Drama, Award } from 'lucide-vue-next'
import { api, mediaUrl } from '@/lib/api'
import { useAsync } from '@/composables/useAsync'
import SealBadge from '@/components/SealBadge.vue'
import SectionHeader from '@/components/SectionHeader.vue'
import MediaPlayer from '@/components/MediaPlayer.vue'
import Loading from '@/components/Loading.vue'
import Empty from '@/components/Empty.vue'

const route = useRoute()
const router = useRouter()
const id = computed(() => Number(route.params.id))

const { data: inheritor, loading, error, run } = useAsync(
  () => api.getInheritor(id.value),
  { immediate: false },
)

// 首次拉取；路由 id 变化（在传承人之间跳转）时重新拉取
run()
watch(() => route.params.id, () => run())

const avatarUrl = computed(() => mediaUrl(inheritor.value?.avatar))
const tags = computed(() =>
  [inheritor.value?.genre_name, inheritor.value?.role_type].filter(Boolean) as string[],
)
const archiveNo = computed(() => '№' + String(id.value).padStart(4, '0'))
const ageText = computed(() => {
  const b = inheritor.value?.birth_date
  if (!b) return null
  const y = new Date(b).getFullYear()
  if (!y) return null
  return new Date().getFullYear() - y
})
</script>

<template>
  <div class="container py-8 md:py-12">
    <!-- 返回 -->
    <button class="btn-ghost mb-6" @click="router.back()">
      <ArrowLeft class="h-4 w-4" /> 返回
    </button>

    <Loading v-if="loading" text="正在调阅档案…" />
    <div v-else-if="error" class="paper-card text-center text-vermilion">
      {{ error }}
    </div>

    <template v-else-if="inheritor">
      <!-- 档案头 -->
      <section class="paper-card relative overflow-hidden">
        <span class="pointer-events-none absolute right-6 top-6">
          <SealBadge :text="archiveNo" size="lg" />
        </span>
        <div class="flex flex-col gap-6 md:flex-row md:items-end">
          <div
            class="h-32 w-32 shrink-0 overflow-hidden rounded-sm border border-ink-200 bg-paper-warm"
          >
            <img
              v-if="avatarUrl"
              :src="avatarUrl"
              :alt="inheritor.name"
              class="h-full w-full object-cover"
            />
            <div
              v-else
              class="flex h-full w-full items-center justify-center font-serif text-4xl text-ink-300"
            >
              {{ inheritor.name?.charAt(0) }}
            </div>
          </div>
          <div class="min-w-0 flex-1">
            <span class="label-eyebrow">INHERITOR · 传承人档案</span>
            <h1 class="display-serif mt-2 text-4xl text-ink-900 md:text-5xl">
              {{ inheritor.name }}
            </h1>
            <div v-if="tags.length" class="mt-3 flex flex-wrap gap-2">
              <span v-for="t in tags" :key="t" class="chip chip-active">{{ t }}</span>
            </div>
            <div class="vermilion-divider mt-4" />
          </div>
        </div>
      </section>

      <!-- 基本信息 -->
      <section class="mt-8">
        <SectionHeader index="01" eyebrow="PROFILE" title="基本信息" />
        <div class="paper-card mt-4 grid grid-cols-2 gap-x-6 gap-y-4 md:grid-cols-4">
          <div v-if="inheritor.gender">
            <p class="text-xs text-ink-400">性别</p>
            <p class="font-serif text-ink-800">{{ inheritor.gender }}</p>
          </div>
          <div v-if="inheritor.birth_date">
            <p class="text-xs text-ink-400">出生</p>
            <p class="font-serif text-ink-800">
              {{ inheritor.birth_date }}<span v-if="ageText" class="ml-1 text-sm text-ink-400">（{{ ageText }}岁）</span>
            </p>
          </div>
          <div v-if="inheritor.age_group">
            <p class="text-xs text-ink-400">年龄段</p>
            <p class="font-serif text-ink-800">{{ inheritor.age_group }}</p>
          </div>
          <div v-if="inheritor.region">
            <p class="text-xs text-ink-400">地区</p>
            <p class="font-serif text-ink-800">{{ inheritor.region }}</p>
          </div>
          <div v-if="inheritor.genre_name">
            <p class="text-xs text-ink-400">剧种</p>
            <p class="font-serif text-ink-800">{{ inheritor.genre_name }}</p>
          </div>
          <div v-if="inheritor.role_type">
            <p class="text-xs text-ink-400">行当</p>
            <p class="font-serif text-ink-800">{{ inheritor.role_type }}</p>
          </div>
          <div v-if="inheritor.master_name">
            <p class="text-xs text-ink-400">师承</p>
            <RouterLink
              v-if="inheritor.master_id"
              :to="`/inheritor/${inheritor.master_id}`"
              class="font-serif text-vermilion hover:underline"
            >{{ inheritor.master_name }}</RouterLink>
            <p v-else class="font-serif text-ink-800">{{ inheritor.master_name }}</p>
          </div>
        </div>
        <p
          v-if="inheritor.bio"
          class="paper-card mt-4 text-sm leading-relaxed text-ink-600"
        >
          {{ inheritor.bio }}
        </p>
      </section>

      <!-- 学艺经历时间线 -->
      <section v-if="inheritor.learning?.length" class="mt-10">
        <SectionHeader index="02" eyebrow="CAREER" title="学艺经历" />
        <ol class="paper-card mt-4 space-y-5 border-l-2 border-vermilion/30 pl-6">
          <li v-for="l in inheritor.learning" :key="l.id" class="relative">
            <span class="absolute -left-[1.65rem] top-1.5 h-3 w-3 rounded-full bg-vermilion ring-4 ring-paper" />
            <div class="flex items-baseline gap-2">
              <span class="font-seal text-lg text-gold">{{ l.year || '—' }}</span>
              <h3 class="font-serif text-ink-900">{{ l.title }}</h3>
            </div>
            <p v-if="l.description" class="mt-1 text-sm text-ink-500">{{ l.description }}</p>
          </li>
        </ol>
      </section>

      <!-- 代表剧目 -->
      <section v-if="inheritor.plays?.length" class="mt-10">
        <SectionHeader index="03" eyebrow="REPERTOIRE" title="代表剧目" />
        <div class="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-2">
          <div v-for="p in inheritor.plays" :key="p.id" class="paper-card flex items-center gap-3">
            <Drama class="h-5 w-5 shrink-0 text-vermilion" />
            <div class="min-w-0">
              <p class="truncate font-serif text-ink-900">{{ p.play_name || '未命名剧目' }}</p>
              <p v-if="p.role_name" class="text-xs text-ink-400">饰 · {{ p.role_name }}</p>
            </div>
          </div>
        </div>
      </section>

      <!-- 获奖情况 -->
      <section v-if="inheritor.awards?.length" class="mt-10">
        <SectionHeader index="04" eyebrow="HONORS" title="获奖情况" />
        <div class="mt-4 space-y-2">
          <div v-for="a in inheritor.awards" :key="a.id" class="paper-card flex items-center gap-3">
            <Award class="h-5 w-5 shrink-0 text-gold" />
            <div class="min-w-0 flex-1">
              <p class="font-serif text-ink-900">{{ a.name }}</p>
              <p v-if="a.level" class="text-xs text-ink-400">{{ a.level }}</p>
            </div>
            <span v-if="a.year" class="chip">{{ a.year }}</span>
          </div>
        </div>
      </section>

      <!-- 音视频资料 -->
      <section class="mt-10">
        <SectionHeader index="05" eyebrow="MEDIA" title="音视频资料" />
        <div v-if="inheritor.media?.length" class="mt-4 grid grid-cols-1 gap-4 lg:grid-cols-2">
          <MediaPlayer v-for="m in inheritor.media" :key="m.id" :media="m" />
        </div>
        <Empty
          v-else
          title="暂无声像资料"
          description="该传承人尚无音视频资料入库。"
        />
      </section>
    </template>
  </div>
</template>
