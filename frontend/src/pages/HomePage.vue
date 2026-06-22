<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import { Search, BookOpen, ShieldCheck, ArrowRight, ScrollText, GitBranch } from 'lucide-vue-next'
import { api } from '@/lib/api'
import { useAsync } from '@/composables/useAsync'
import SealBadge from '@/components/SealBadge.vue'

// 统计：剧种数 + 传承人总数
const genresReq = useAsync(() => api.listGenres())
const inheritorsReq = useAsync(() => api.listInheritors({ size: 1 }))

const genreCount = computed(() => genresReq.data.value?.length ?? 0)
const inheritorCount = computed(() => inheritorsReq.data.value?.total ?? 0)

const modules = [
  {
    to: '/directory',
    icon: Search,
    eyebrow: 'DIRECTORY',
    title: '名录查询',
    desc: '按剧种、行当、地区、师承、年龄段与拼音首字母多维检索传承人档案。',
  },
  {
    to: '/genres',
    icon: BookOpen,
    eyebrow: 'GENRES',
    title: '剧种百科',
    desc: '纵览各戏曲剧种的历史渊源、艺术特点、经典剧目与主要流派。',
  },
  {
    to: '/genres/1/genealogy',
    icon: GitBranch,
    eyebrow: 'GENEALOGY',
    title: '传承谱系',
    desc: '以树状网络图谱直观呈现某剧种从宗师到传人的师承关系与亲属脉络。',
  },
  {
    to: '/admin',
    icon: ShieldCheck,
    eyebrow: 'ADMIN',
    title: '后台管理',
    desc: '登录后管理传承人档案，支持单条编辑与 Excel 批量导入。',
  },
]

const stats = computed(() => [
  { label: '收录剧种', value: genreCount.value, suffix: '种' },
  { label: '传承人档案', value: inheritorCount.value, suffix: '位' },
  { label: '编纂机构', value: '非遗中心', suffix: '' },
])
</script>

<template>
  <div>
    <!-- 英雄区：水墨渐变背景 -->
    <section
      class="relative overflow-hidden"
      style="
        background:
          radial-gradient(120% 90% at 80% 0%, rgba(158, 43, 37, 0.08), transparent 60%),
          radial-gradient(80% 60% at 0% 100%, rgba(92, 122, 107, 0.1), transparent 60%),
          linear-gradient(180deg, #EFE9DA 0%, #F5F1E8 55%, #E7DFCB 100%);
      "
    >
      <div class="container relative py-20 md:py-28">
        <div class="flex flex-col items-center text-center">
          <span class="label-eyebrow mb-5 animate-fade-up"
            >OPERA HERITAGE · 戏曲传承人口齿录</span
          >
          <h1
            class="display-serif animate-fade-up text-balance text-5xl text-ink-900 md:text-7xl"
            style="animation-delay: 0.05s"
          >
            梨园典藏
          </h1>
          <div class="vermilion-divider my-6 animate-fade-up" style="animation-delay: 0.1s" />
          <p
            class="max-w-2xl animate-fade-up text-balance text-base leading-relaxed text-ink-600 md:text-lg"
            style="animation-delay: 0.15s"
          >
            一座为戏曲传承人而立的数字档案馆——以名录为经、以剧种为纬，
            勾勒师承脉络，留存声腔光影。
          </p>

          <div class="mt-8 flex animate-fade-up flex-wrap items-center justify-center gap-3" style="animation-delay: 0.2s">
            <RouterLink to="/directory" class="btn-primary">
              进入名录 <ArrowRight class="h-4 w-4" />
            </RouterLink>
            <RouterLink to="/genres" class="btn-ghost">浏览剧种</RouterLink>
          </div>
        </div>

        <!-- 印章角标 -->
        <div class="pointer-events-none absolute right-6 top-10 hidden md:block">
          <span class="seal-stamp animate-seal-stamp h-20 w-20 rounded-sm font-seal text-2xl">
            梨园
          </span>
        </div>
      </div>

      <!-- 数据统计条 -->
      <div class="container pb-12">
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <div
            v-for="s in stats"
            :key="s.label"
            class="paper-card flex items-center gap-4"
          >
            <SealBadge :text="s.label.charAt(0)" size="sm" />
            <div>
              <p class="display-serif text-2xl text-ink-900">
                {{ s.value }}<span class="ml-0.5 text-sm font-normal text-ink-400">{{ s.suffix }}</span>
              </p>
              <p class="text-xs text-ink-500">{{ s.label }}</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 三模块入口 -->
    <section class="container py-16">
      <div class="mb-10 flex items-end justify-between gap-4">
        <div>
          <span class="label-eyebrow">EXPLORE</span>
          <h2 class="section-title mt-2">三径入藏</h2>
        </div>
        <ScrollText class="hidden h-8 w-8 text-ink-300 md:block" />
      </div>

      <div class="grid grid-cols-1 gap-5 md:grid-cols-2 xl:grid-cols-4">
        <RouterLink
          v-for="(m, i) in modules"
          :key="m.to"
          :to="m.to"
          class="paper-card paper-card-hover group flex flex-col"
        >
          <div class="flex items-center justify-between">
            <span
              class="flex h-12 w-12 items-center justify-center rounded-sm bg-vermilion/10 text-vermilion transition-colors group-hover:bg-vermilion group-hover:text-paper"
            >
              <component :is="m.icon" class="h-6 w-6" />
            </span>
            <span class="font-seal text-2xl text-gold/60">{{ String(i + 1).padStart(2, '0') }}</span>
          </div>
          <span class="label-eyebrow mt-4">{{ m.eyebrow }}</span>
          <h3 class="display-serif mt-1 text-xl text-ink-900">{{ m.title }}</h3>
          <p class="mt-2 flex-1 text-sm leading-relaxed text-ink-500">{{ m.desc }}</p>
          <span class="mt-4 inline-flex items-center gap-1 text-sm text-vermilion">
            进入 <ArrowRight class="h-4 w-4 transition-transform group-hover:translate-x-1" />
          </span>
        </RouterLink>
      </div>
    </section>
  </div>
</template>
