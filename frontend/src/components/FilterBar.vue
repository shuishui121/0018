<script setup lang="ts">
import { ref, computed } from 'vue'
import { SlidersHorizontal, ChevronDown, X } from 'lucide-vue-next'
import type { Genre, InheritorListItem, InheritorFilters } from '@/lib/api'
import { ROLE_OPTIONS, REGION_OPTIONS, AGE_GROUP_OPTIONS } from '@/lib/options'

// 多维筛选条：剧种/行当/地区下拉 + 师承输入(含建议) + 年龄段单选 chips
const props = defineProps<{
  filters: InheritorFilters
  genres: Genre[]
  masters: InheritorListItem[]
}>()

const emit = defineEmits<{ (e: 'change'): void }>()

// 移动端折叠状态
const expanded = ref(false)

// 师承输入：以姓名呈现，change 时解析为 master_id
const masterName = computed({
  get() {
    const id = props.filters.master
    if (!id) return ''
    return props.masters.find((m) => m.id === id)?.name ?? ''
  },
  set(name: string) {
    const found = props.masters.find((m) => m.name === name.trim())
    props.filters.master = found ? found.id : null
  },
})

// 任意筛选变化：写入值、重置页码、通知父级重新拉取
function update<K extends keyof InheritorFilters>(key: K, value: InheritorFilters[K]) {
  props.filters[key] = value
  props.filters.page = 1
  emit('change')
}

function toggleAge(value: string) {
  update('age_group', props.filters.age_group === value ? null : value)
}

function clearAll() {
  props.filters.genre = null
  props.filters.role = null
  props.filters.region = null
  props.filters.master = null
  props.filters.age_group = null
  props.filters.page = 1
  emit('change')
}

const hasActive = computed(
  () =>
    !!(
      props.filters.genre ||
      props.filters.role ||
      props.filters.region ||
      props.filters.master ||
      props.filters.age_group
    ),
)
</script>

<template>
  <div class="paper-card">
    <!-- 移动端折叠触发 -->
    <button
      type="button"
      class="flex w-full items-center justify-between md:hidden"
      style="min-height: 44px"
      @click="expanded = !expanded"
    >
      <span class="flex items-center gap-2 font-serif text-sm text-ink-800">
        <SlidersHorizontal class="h-4 w-4 text-vermilion" />筛选条件
        <span
          v-if="hasActive"
          class="chip chip-active !px-2 !py-0.5 text-[10px]"
          >已筛选</span
        >
      </span>
      <ChevronDown
        class="h-4 w-4 text-ink-400 transition-transform"
        :class="{ 'rotate-180': expanded }"
      />
    </button>

    <div
      class="grid grid-cols-1 gap-3 md:grid-cols-2 lg:grid-cols-4"
      :class="{ 'hidden md:grid': !expanded }"
    >
      <!-- 剧种 -->
      <label class="flex flex-col gap-1">
        <span class="label-eyebrow !text-[10px]">剧种</span>
        <select
          class="input-field"
          :value="filters.genre ?? ''"
          @change="update('genre', ($event.target as HTMLSelectElement).value ? Number(($event.target as HTMLSelectElement).value) : null)"
        >
          <option value="">全部剧种</option>
          <option v-for="g in genres" :key="g.id" :value="g.id">{{ g.name }}</option>
        </select>
      </label>

      <!-- 行当 -->
      <label class="flex flex-col gap-1">
        <span class="label-eyebrow !text-[10px]">行当</span>
        <select
          class="input-field"
          :value="filters.role ?? ''"
          @change="update('role', ($event.target as HTMLSelectElement).value || null)"
        >
          <option value="">全部行当</option>
          <option v-for="r in ROLE_OPTIONS" :key="r" :value="r">{{ r }}</option>
        </select>
      </label>

      <!-- 地区 -->
      <label class="flex flex-col gap-1">
        <span class="label-eyebrow !text-[10px]">地区</span>
        <select
          class="input-field"
          :value="filters.region ?? ''"
          @change="update('region', ($event.target as HTMLSelectElement).value || null)"
        >
          <option value="">全部地区</option>
          <option v-for="r in REGION_OPTIONS" :key="r" :value="r">{{ r }}</option>
        </select>
      </label>

      <!-- 师承 -->
      <label class="flex flex-col gap-1">
        <span class="label-eyebrow !text-[10px]">师承</span>
        <input
          v-model="masterName"
          list="master-suggestions"
          class="input-field"
          placeholder="输入师承姓名"
          @change="emit('change')"
        />
        <datalist id="master-suggestions">
          <option v-for="m in masters" :key="m.id" :value="m.name">
            {{ m.genre_name }}
          </option>
        </datalist>
      </label>

      <!-- 年龄段 chips -->
      <div class="flex flex-col gap-1 md:col-span-2 lg:col-span-4">
        <span class="label-eyebrow !text-[10px]">年龄段</span>
        <div class="flex flex-wrap gap-2">
          <button
            v-for="age in AGE_GROUP_OPTIONS"
            :key="age"
            type="button"
            class="chip transition-colors"
            :class="{ 'chip-active': filters.age_group === age }"
            style="min-height: 44px"
            @click="toggleAge(age)"
          >
            {{ age }}
          </button>
          <button
            v-if="hasActive"
            type="button"
            class="ml-auto inline-flex items-center gap-1 self-center text-xs text-ink-400 hover:text-vermilion"
            @click="clearAll"
          >
            <X class="h-3 w-3" />清除筛选
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
