<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import { MapPin, Users } from 'lucide-vue-next'
import { mediaUrl, type InheritorListItem } from '@/lib/api'
import SealBadge from '@/components/SealBadge.vue'

const props = defineProps<{ inheritor: InheritorListItem }>()

const avatarUrl = computed(() => mediaUrl(props.inheritor.avatar))
const initial = computed(
  () => (props.inheritor.pinyin_initial || '#').charAt(0).toUpperCase(),
)
const tags = computed(() =>
  [props.inheritor.genre_name, props.inheritor.role_type].filter(Boolean) as string[],
)
</script>

<template>
  <RouterLink
    :to="`/inheritor/${inheritor.id}`"
    class="paper-card paper-card-hover group block focus:outline-none focus-visible:ring-2 focus-visible:ring-vermilion/50"
  >
    <!-- 拼音首字母印章 -->
    <span class="absolute right-3 top-3 z-10">
      <SealBadge :text="initial" size="sm" />
    </span>

    <div class="flex gap-4">
      <!-- 头像 -->
      <div
        class="relative h-20 w-20 shrink-0 overflow-hidden rounded-sm border border-ink-200 bg-paper-warm"
      >
        <img
          v-if="avatarUrl"
          :src="avatarUrl"
          :alt="inheritor.name"
          loading="lazy"
          class="h-full w-full object-cover transition-transform duration-300 group-hover:scale-105"
        />
        <div
          v-else
          class="flex h-full w-full items-center justify-center font-serif text-2xl text-ink-300"
        >
          {{ inheritor.name?.charAt(0) }}
        </div>
      </div>

      <!-- 文案 -->
      <div class="min-w-0 flex-1 pr-6">
        <h3 class="display-serif truncate text-lg text-ink-900">
          {{ inheritor.name }}
        </h3>
        <div v-if="tags.length" class="mt-2 flex flex-wrap gap-1.5">
          <span v-for="t in tags" :key="t" class="chip">{{ t }}</span>
        </div>
        <div class="mt-2 space-y-1 text-xs text-ink-500">
          <p v-if="inheritor.region" class="flex items-center gap-1">
            <MapPin class="h-3 w-3" />{{ inheritor.region }}
          </p>
          <p v-if="inheritor.master_name" class="flex items-center gap-1">
            <Users class="h-3 w-3" />师承 · {{ inheritor.master_name }}
          </p>
        </div>
      </div>
    </div>

    <p
      v-if="inheritor.bio"
      class="mt-3 line-clamp-2 border-t border-ink-200/60 pt-3 text-xs leading-relaxed text-ink-500"
    >
      {{ inheritor.bio }}
    </p>
  </RouterLink>
</template>
