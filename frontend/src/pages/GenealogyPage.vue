<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute, useRouter, RouterLink } from 'vue-router'
import { ArrowLeft, Search, Filter, X, User, Users, MapPin, GitBranch, ChevronRight, Award } from 'lucide-vue-next'
import {
  api,
  mediaUrl,
  type GenealogyResponse,
  type GenealogyNode,
  type GenealogyEdge,
  type InheritorRelationsResponse,
  type InheritorRelationItem,
} from '@/lib/api'
import { useAsync } from '@/composables/useAsync'
import { useDebounce } from '@/composables/useDebounce'
import GenealogyGraph from '@/components/GenealogyGraph.vue'
import Loading from '@/components/Loading.vue'
import Empty from '@/components/Empty.vue'
import SectionHeader from '@/components/SectionHeader.vue'

const route = useRoute()
const router = useRouter()
const genreId = computed(() => Number(route.params.id))

// 过滤器状态
const searchKeyword = ref('')
const regionFilter = ref('')
const maxGenerations = ref(5)
const relationTypeFilter = ref('')

const debouncedKeyword = useDebounce(searchKeyword, 300)
const debouncedRegion = useDebounce(regionFilter, 300)

const RELATION_TYPES = [
  { value: '', label: '全部关系' },
  { value: 'master_apprentice', label: '师徒传承' },
  { value: 'master', label: '师傅' },
  { value: 'apprentice', label: '徒弟' },
  { value: 'senior_fellow', label: '师兄/师姐' },
  { value: 'junior_fellow', label: '师弟/师妹' },
  { value: 'sibling', label: '兄弟姐妹' },
  { value: 'spouse', label: '配偶' },
  { value: 'parent', label: '父母' },
  { value: 'child', label: '子女' },
  { value: 'colleague', label: '同事' },
  { value: 'friend', label: '友人' },
]

// 图谱数据
const genealogyData = ref<GenealogyResponse | null>(null)
const graphLoading = ref(false)
const graphError = ref<string | null>(null)

async function loadGenealogy() {
  graphLoading.value = true
  graphError.value = null
  try {
    genealogyData.value = await api.getGenreGenealogy(genreId.value, {
      max_generations: maxGenerations.value,
      keyword: debouncedKeyword.value || undefined,
      region: debouncedRegion.value || undefined,
    })
  } catch (e: any) {
    graphError.value = e?.message || '加载谱系数据失败'
  } finally {
    graphLoading.value = false
  }
}

// 高亮节点ID（搜索结果）
const highlightIds = computed<number[]>(() => {
  if (!debouncedKeyword.value && !debouncedRegion.value) return []
  return (genealogyData.value?.nodes || []).map((n) => n.id)
})

// 选中节点与关系详情抽屉
const selectedNode = ref<GenealogyNode | null>(null)
const relationsDrawer = ref(false)
const relationsLoading = ref(false)
const relationsError = ref<string | null>(null)
const relationsData = ref<InheritorRelationsResponse | null>(null)
const relationFilterForDrawer = ref('')

async function loadRelations(nodeId: number) {
  relationsLoading.value = true
  relationsError.value = null
  try {
    relationsData.value = await api.getInheritorRelations(nodeId, {
      relation_type: relationFilterForDrawer.value || undefined,
      max_distance: 3,
    })
  } catch (e: any) {
    relationsError.value = e?.message || '加载关系数据失败'
  } finally {
    relationsLoading.value = false
  }
}

function handleNodeClick(node: GenealogyNode) {
  selectedNode.value = node
  relationsDrawer.value = true
  relationFilterForDrawer.value = ''
  loadRelations(node.id)
}

function handleEdgeClick(_edge: GenealogyEdge) {
  // 可以扩展点击连线时的行为
}

watch(relationFilterForDrawer, () => {
  if (selectedNode.value) {
    loadRelations(selectedNode.value.id)
  }
})

// 按关系类型分组
const groupedRelations = computed<Record<string, InheritorRelationItem[]>>(() => {
  const groups: Record<string, InheritorRelationItem[]> = {}
  for (const r of relationsData.value?.relations || []) {
    if (!groups[r.relation_label]) {
      groups[r.relation_label] = []
    }
    groups[r.relation_label].push(r)
  }
  return groups
})

// 从图谱节点中按关系类型筛选显示
const filteredEdges = computed(() => {
  const edges = genealogyData.value?.edges || []
  if (!relationTypeFilter.value) return edges
  return edges.filter((e) => {
    if (relationTypeFilter.value === 'master_apprentice') {
      return e.relation_type === 'master_apprentice'
    }
    return e.relation_type === relationTypeFilter.value
  })
})

const filteredNodes = computed(() => genealogyData.value?.nodes || [])

// 提取所有地区供过滤选择
const allRegions = computed(() => {
  const set = new Set<string>()
  for (const n of genealogyData.value?.nodes || []) {
    if (n.region) set.add(n.region)
  }
  return Array.from(set).sort()
})

function clearFilters() {
  searchKeyword.value = ''
  regionFilter.value = ''
  relationTypeFilter.value = ''
  maxGenerations.value = 5
}

onMounted(() => {
  loadGenealogy()
})

watch(
  [debouncedKeyword, debouncedRegion, () => maxGenerations.value, () => relationTypeFilter.value],
  () => {
    loadGenealogy()
  },
)

const generationStats = computed(() => {
  if (!genealogyData.value) return {}
  const stats: Record<number, number> = {}
  for (const n of genealogyData.value.nodes) {
    stats[n.generation] = (stats[n.generation] || 0) + 1
  }
  return stats
})
</script>

<template>
  <div class="container py-6 md:py-8">
    <!-- 顶部导航 -->
    <div class="flex items-center justify-between mb-6 flex-wrap gap-3">
      <button class="btn-ghost" @click="router.back()">
        <ArrowLeft class="h-4 w-4" /> 返回
      </button>
      <div class="flex items-center gap-2">
        <RouterLink
          v-if="genealogyData"
          :to="`/genres/${genreId}`"
          class="chip !py-1.5 font-serif hover:border-vermilion"
        >
          {{ genealogyData.genre.name }} · 百科
        </RouterLink>
      </div>
    </div>

    <!-- 页头 -->
    <section class="paper-card mb-6">
      <div class="flex items-start gap-4 flex-wrap md:flex-nowrap">
        <div class="flex-1 min-w-0">
          <span class="label-eyebrow">GENEALOGY · 传承谱系</span>
          <h1 class="display-serif mt-2 text-3xl md:text-4xl text-ink-900">
            {{ genealogyData?.genre?.name || '加载中…' }}
            <span class="font-seal text-gold text-base md:text-lg ml-2">传承脉络图谱</span>
          </h1>
          <p class="mt-2 text-sm text-ink-500 font-serif">
            从第一代宗师到当代传人，共 <span class="text-vermilion font-bold">{{ genealogyData?.max_generation || 0 }}</span> 代，
            收录传承人 <span class="text-vermilion font-bold">{{ genealogyData?.nodes.length || 0 }}</span> 位，
            关系连线 <span class="text-vermilion font-bold">{{ genealogyData?.edges.length || 0 }}</span> 条。
          </p>
          <!-- 代数统计 -->
          <div v-if="Object.keys(generationStats).length" class="mt-4 flex flex-wrap gap-2">
            <span
              v-for="(count, gen) in generationStats"
              :key="gen"
              class="chip !py-1 font-seal"
              :class="{
                '!bg-vermilion/10 !border-vermilion !text-vermilion': Number(gen) === 1,
                '!bg-gold/10 !border-gold !text-gold-dark': Number(gen) === 2,
              }"
            >
              第{{ gen }}代 · {{ count }}人
            </span>
          </div>
        </div>
      </div>
    </section>

    <!-- 筛选条 -->
    <section class="paper-card mb-6">
      <div class="flex items-center gap-2 mb-4">
        <Filter class="h-4 w-4 text-vermilion" />
        <h3 class="font-serif font-bold text-ink-800">检索筛选</h3>
        <button
          v-if="searchKeyword || regionFilter || relationTypeFilter || maxGenerations !== 5"
          class="ml-auto text-xs text-ink-400 hover:text-vermilion flex items-center gap-1"
          @click="clearFilters"
        >
          <X class="h-3 w-3" /> 清除筛选
        </button>
      </div>
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        <!-- 姓名搜索 -->
        <div class="relative">
          <Search class="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-ink-400" />
          <input
            v-model="searchKeyword"
            type="text"
            placeholder="按姓名搜索传承人…"
            class="input-field !pl-9"
          />
        </div>
        <!-- 地区过滤 -->
        <div>
          <select v-model="regionFilter" class="input-field appearance-none pr-8">
            <option value="">全部地区</option>
            <option v-for="r in allRegions" :key="r" :value="r">{{ r }}</option>
          </select>
        </div>
        <!-- 关系类型 -->
        <div>
          <select v-model="relationTypeFilter" class="input-field appearance-none pr-8">
            <option v-for="rt in RELATION_TYPES" :key="rt.value" :value="rt.value">
              {{ rt.label }}
            </option>
          </select>
        </div>
        <!-- 代数 -->
        <div>
          <select v-model.number="maxGenerations" class="input-field appearance-none pr-8">
            <option v-for="n in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]" :key="n" :value="n">
              最多 {{ n }} 代
            </option>
          </select>
        </div>
      </div>
    </section>

    <!-- 图谱区域 -->
    <section class="paper-card relative overflow-hidden" style="min-height: 650px;">
      <div class="flex items-center gap-2 mb-3 px-1">
        <GitBranch class="h-5 w-5 text-vermilion" />
        <h3 class="section-title !text-xl !mb-0">传承谱系图</h3>
        <span class="ml-auto text-xs text-ink-400 font-seal">
          点击任意传承人节点查看关系详情
        </span>
      </div>

      <Loading v-if="graphLoading" text="正在绘卷谱系…" class="py-24" />
      <div v-else-if="graphError" class="py-24 text-center text-vermilion paper-card !bg-vermilion/5">
        {{ graphError }}
      </div>
      <Empty
        v-else-if="!filteredNodes.length"
        title="未找到匹配的传承人"
        description="请尝试调整筛选条件，或查看该剧种全部传承人。"
        class="py-24"
      />
      <div v-else style="height: 620px;">
        <GenealogyGraph
          :nodes="filteredNodes"
          :edges="filteredEdges"
          :highlight-ids="highlightIds"
          :selected-id="selectedNode?.id ?? null"
          @node-click="handleNodeClick"
          @edge-click="handleEdgeClick"
        />
      </div>
    </section>

    <!-- 关系详情抽屉 -->
    <Teleport to="body">
      <Transition name="drawer-fade">
        <div
          v-if="relationsDrawer"
          class="fixed inset-0 z-50 bg-ink-900/50 backdrop-blur-sm"
          @click.self="relationsDrawer = false"
        />
      </Transition>
      <Transition name="drawer-slide">
        <aside
          v-if="relationsDrawer"
          class="fixed right-0 top-0 bottom-0 z-50 w-full max-w-md bg-paper-warm shadow-2xl border-l border-ink-200 overflow-hidden flex flex-col"
        >
          <!-- 抽屉头 -->
          <div class="relative border-b border-ink-200 bg-gradient-to-b from-vermilion/5 to-transparent p-5">
            <button
              class="absolute top-4 right-4 h-8 w-8 flex items-center justify-center rounded-full hover:bg-ink-100 text-ink-500"
              @click="relationsDrawer = false"
            >
              <X class="h-5 w-5" />
            </button>
            <template v-if="selectedNode">
              <div class="flex items-start gap-4">
                <div
                  class="w-20 h-20 rounded-full flex items-center justify-center shrink-0 shadow-md border-2"
                  :class="{
                    'border-gold bg-vermilion/10': selectedNode.generation === 1,
                    'border-vermilion/50 bg-gold/10': selectedNode.generation === 2,
                    'border-ink-200 bg-ink-50': selectedNode.generation > 2,
                  }"
                >
                  <img
                    v-if="selectedNode.avatar"
                    :src="mediaUrl(selectedNode.avatar)"
                    class="w-full h-full object-cover rounded-full"
                  />
                  <span
                    v-else
                    class="font-seal text-3xl"
                    :class="selectedNode.generation === 1 ? 'text-vermilion' : 'text-gold'"
                  >
                    {{ selectedNode.name.charAt(0) }}
                  </span>
                </div>
                <div class="min-w-0 flex-1">
                  <div class="label-eyebrow !text-xs">GEN · 第{{ selectedNode.generation }}代</div>
                  <h2 class="display-serif mt-1 text-2xl text-ink-900">{{ selectedNode.name }}</h2>
                  <div class="mt-2 flex flex-wrap gap-1.5">
                    <span class="chip !py-0.5 !text-xs">
                      <User class="h-3 w-3" /> {{ selectedNode.role_type || '行当未录' }}
                    </span>
                    <span v-if="selectedNode.region" class="chip !py-0.5 !text-xs">
                      <MapPin class="h-3 w-3" /> {{ selectedNode.region }}
                    </span>
                  </div>
                </div>
              </div>
              <!-- 操作按钮 -->
              <div class="mt-4 flex gap-2">
                <RouterLink
                  :to="`/inheritor/${selectedNode.id}`"
                  class="btn-primary !py-2 !text-xs flex-1 justify-center"
                >
                  <Award class="h-3.5 w-3.5" /> 查看完整档案
                </RouterLink>
              </div>
            </template>
          </div>

          <!-- 筛选 -->
          <div class="border-b border-ink-100 p-4 bg-paper/60">
            <div class="flex items-center gap-2">
              <Users class="h-4 w-4 text-vermilion" />
              <span class="font-serif font-bold text-sm text-ink-800">关系网</span>
              <select
                v-model="relationFilterForDrawer"
                class="ml-auto input-field !py-1.5 !text-xs w-36 !pr-6"
              >
                <option value="">全部关系类型</option>
                <option
                  v-for="rt in RELATION_TYPES.filter((r) => r.value !== 'master_apprentice')"
                  :key="rt.value"
                  :value="rt.value"
                >
                  {{ rt.label }}
                </option>
              </select>
            </div>
            <p v-if="relationsData" class="mt-2 text-xs text-ink-500 font-serif">
              共发现 <span class="text-vermilion font-bold">{{ relationsData.relations.length }}</span> 位关联人
            </p>
          </div>

          <!-- 关系列表 -->
          <div class="flex-1 overflow-y-auto scrollbar-thin p-4 space-y-5">
            <Loading v-if="relationsLoading" text="正在梳理关系…" class="py-16" />
            <div v-else-if="relationsError" class="py-12 text-center text-vermilion text-sm">
              {{ relationsError }}
            </div>
            <Empty
              v-else-if="!relationsData?.relations.length"
              title="未发现关联关系"
              description="该传承人暂未录入相关师承或亲属信息。"
              class="py-16"
            />
            <template v-else>
              <section v-for="(items, label) in groupedRelations" :key="label">
                <SectionHeader
                  :index="String(Object.keys(groupedRelations).indexOf(label) + 1).padStart(2, '0')"
                  :eyebrow="`${items.length}人`"
                  :title="label"
                  class="!mb-3"
                />
                <div class="space-y-2">
                  <RouterLink
                    v-for="r in items"
                    :key="r.inheritor.id"
                    :to="`/inheritor/${r.inheritor.id}`"
                    class="paper-card paper-card-hover !p-3 flex items-center gap-3 block"
                  >
                    <div
                      class="w-11 h-11 shrink-0 rounded-full bg-ink-100 flex items-center justify-center border border-ink-200 overflow-hidden"
                    >
                      <img
                        v-if="r.inheritor.avatar"
                        :src="mediaUrl(r.inheritor.avatar)"
                        class="w-full h-full object-cover"
                      />
                      <span v-else class="font-seal text-lg text-ink-500">
                        {{ r.inheritor.name.charAt(0) }}
                      </span>
                    </div>
                    <div class="min-w-0 flex-1">
                      <div class="flex items-center gap-2">
                        <span class="font-serif font-bold text-ink-900">{{ r.inheritor.name }}</span>
                        <span
                          v-if="r.distance > 1"
                          class="text-[10px] font-seal text-gold border border-gold/40 rounded px-1"
                        >
                          {{ r.distance }}度关联
                        </span>
                      </div>
                      <div class="text-xs text-ink-500 mt-0.5 truncate">
                        {{ r.inheritor.role_type || '—' }} · {{ r.inheritor.region || '地区未录' }}
                      </div>
                      <div
                        v-if="r.shared_learning"
                        class="text-[11px] text-celadon mt-1 truncate"
                        :title="r.shared_learning"
                      >
                        共同经历：{{ r.shared_learning }}
                      </div>
                    </div>
                    <ChevronRight class="h-4 w-4 text-ink-300 shrink-0" />
                  </RouterLink>
                </div>
              </section>
            </template>
          </div>
        </aside>
      </Transition>
    </Teleport>
  </div>
</template>

<style scoped>
.drawer-fade-enter-active,
.drawer-fade-leave-active {
  transition: opacity 0.25s ease;
}
.drawer-fade-enter-from,
.drawer-fade-leave-to {
  opacity: 0;
}
.drawer-slide-enter-active,
.drawer-slide-leave-active {
  transition: transform 0.3s cubic-bezier(0.22, 1, 0.36, 1);
}
.drawer-slide-enter-from,
.drawer-slide-leave-to {
  transform: translateX(100%);
}
</style>
