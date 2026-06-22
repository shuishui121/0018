<script setup lang="ts">
import { ref, computed, watch, onMounted, onBeforeUnmount, nextTick } from 'vue'
import * as echarts from 'echarts'
import type { GenealogyNode, GenealogyEdge } from '@/lib/api'
import { mediaUrl } from '@/lib/api'

const props = defineProps<{
  nodes: GenealogyNode[]
  edges: GenealogyEdge[]
  highlightIds?: number[]
  selectedId?: number | null
}>()

const emit = defineEmits<{
  nodeClick: [node: GenealogyNode]
  edgeClick: [edge: GenealogyEdge]
}>()

const chartRef = ref<HTMLDivElement | null>(null)
let chartInstance: echarts.ECharts | null = null

const COLORS = {
  ink: '#1A1714',
  paper: '#F5F1E8',
  vermilion: '#9E2B25',
  vermilionDark: '#7A1F1B',
  gold: '#B8893B',
  goldLight: '#D4A84B',
  celadon: '#5C7A6B',
  generations: [
    '#9E2B25', // 1代 - 朱砂红（宗师）
    '#B8893B', // 2代 - 鎏金
    '#5C7A6B', // 3代 - 青瓷
    '#6B4423', // 4代 - 赭石
    '#4A5568', // 5代 - 黛青
    '#2C5282', // 6代+
  ],
}

const highlightSet = computed(() => new Set(props.highlightIds || []))

function colorForGen(gen: number): string {
  const idx = Math.min(gen - 1, COLORS.generations.length - 1)
  return COLORS.generations[idx]
}

function buildOption(): echarts.EChartsOption {
  const nodeMap = new Map(props.nodes.map((n) => [n.id, n]))

  const chartNodes: any[] = props.nodes.map((n) => {
    const isHighlight = highlightSet.value.has(n.id) || highlightSet.value.size === 0
    const isSelected = props.selectedId === n.id
    const color = colorForGen(n.generation)

    return {
      id: String(n.id),
      name: n.name,
      value: n.generation,
      category: n.generation - 1,
      symbolSize: 50 + (isSelected ? 12 : 0),
      draggable: true,
      itemStyle: {
        color: isSelected ? COLORS.vermilion : color,
        borderColor: isSelected ? COLORS.gold : isHighlight ? COLORS.ink : COLORS.ink + '50',
        borderWidth: isSelected ? 4 : isHighlight ? 2.5 : 1.5,
        shadowBlur: isSelected ? 20 : isHighlight ? 10 : 4,
        shadowColor: isSelected ? COLORS.vermilion + '80' : color + '60',
        opacity: isHighlight ? 1 : 0.35,
      },
      label: {
        show: true,
        position: 'bottom',
        distance: 8,
        fontSize: isSelected ? 15 : 12,
        fontWeight: isSelected ? 'bold' : 'normal',
        color: isSelected ? COLORS.vermilionDark : COLORS.ink,
        fontFamily: "'Noto Serif SC', serif",
        formatter: `{name|${n.name}}\n{role|${n.role_type || ''}}`,
        rich: {
          name: {
            fontSize: isSelected ? 15 : 13,
            fontWeight: 'bold',
            color: isSelected ? COLORS.vermilionDark : COLORS.ink,
            lineHeight: 18,
          },
          role: {
            fontSize: 10,
            color: COLORS.gold,
            lineHeight: 14,
          },
        },
      },
      emphasis: {
        scale: 1.25,
        focus: 'adjacency',
        itemStyle: {
          shadowBlur: 30,
          shadowColor: COLORS.vermilion + '90',
        },
        label: {
          fontSize: 16,
          fontWeight: 'bold',
        },
      },
      data: n,
    }
  })

  const edgeMap = new Map<string, GenealogyEdge>()
  props.edges.forEach((e) => {
    edgeMap.set(`${e.source}-${e.target}`, e)
    edgeMap.set(`${e.target}-${e.source}`, e)
  })

  const isEdgeHighlighted = (e: GenealogyEdge) => {
    if (highlightSet.value.size === 0) return true
    return highlightSet.value.has(e.source) && highlightSet.value.has(e.target)
  }

  const chartLinks: any[] = props.edges.map((e) => {
    const highlighted = isEdgeHighlighted(e)
    const isMasterLine = e.relation_type === 'master_apprentice'
    const lineColor = isMasterLine ? COLORS.vermilion : COLORS.celadon

    return {
      source: String(e.source),
      target: String(e.target),
      value: e.relation_label,
      lineStyle: {
        color: highlighted ? lineColor : lineColor + '30',
        width: isMasterLine ? (highlighted ? 3.5 : 1.5) : highlighted ? 2 : 1,
        type: isMasterLine ? 'solid' : 'dashed',
        curveness: isMasterLine ? 0.05 : 0.2,
        opacity: highlighted ? 0.9 : 0.3,
      },
      label: {
        show: false,
        formatter: e.relation_label,
        fontSize: 11,
        color: COLORS.gold,
        backgroundColor: COLORS.paper,
        padding: [2, 6],
        borderRadius: 4,
        borderColor: COLORS.gold + '50',
        borderWidth: 1,
      },
      emphasis: {
        lineStyle: {
          width: 5,
          opacity: 1,
          shadowBlur: 10,
          shadowColor: lineColor + '80',
        },
        label: {
          show: true,
        },
      },
      data: e,
    }
  })

  const categories: { name: string }[] = []
  const maxGen = Math.max(...props.nodes.map((n) => n.generation), 1)
  for (let i = 0; i < maxGen; i++) {
    categories.push({ name: `第${i + 1}代` })
  }

  return {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      backgroundColor: COLORS.paper,
      borderColor: COLORS.vermilion + '40',
      borderWidth: 1,
      textStyle: {
        color: COLORS.ink,
        fontFamily: "'Noto Sans SC', sans-serif",
      },
      formatter: (params: any) => {
        if (params.dataType === 'edge') {
          const edge: GenealogyEdge = params.data.data
          const src = nodeMap.get(edge.source)
          const tgt = nodeMap.get(edge.target)
          return `
            <div style="padding:4px 2px;">
              <div style="font-weight:bold;color:${COLORS.vermilion};margin-bottom:6px;font-family:'Noto Serif SC',serif;">
                ${edge.relation_label}
              </div>
              <div style="font-size:12px;color:${COLORS.ink};">
                ${src?.name || ''} → ${tgt?.name || ''}
              </div>
            </div>
          `
        }
        const node: GenealogyNode = params.data.data
        const avatarHtml = node.avatar
          ? `<img src="${mediaUrl(node.avatar)}" style="width:60px;height:60px;border-radius:50%;object-fit:cover;border:2px solid ${COLORS.gold};margin-right:10px;float:left;" />`
          : `<div style="width:60px;height:60px;border-radius:50%;background:${colorForGen(node.generation)};margin-right:10px;float:left;display:flex;align-items:center;justify-content:center;color:${COLORS.paper};font-family:'Ma Shan Zheng',cursive;font-size:28px;">${node.name.charAt(0)}</div>`
        return `
          <div style="padding:4px;min-width:200px;">
            ${avatarHtml}
            <div style="overflow:hidden;">
              <div style="font-size:16px;font-weight:bold;color:${COLORS.ink};font-family:'Noto Serif SC',serif;">${node.name}</div>
              <div style="font-size:12px;color:${COLORS.gold};margin:2px 0;">第 ${node.generation} 代 · ${node.role_type || '行当待录'}</div>
              <div style="font-size:11px;color:${COLORS.ink}99;">${node.region || '地区未录'}</div>
            </div>
          </div>
        `
      },
    },
    legend: [{
      data: categories.map((c) => c.name),
      orient: 'horizontal',
      top: 10,
      left: 'center',
      textStyle: {
        color: COLORS.ink,
        fontFamily: "'Noto Serif SC', serif",
      },
      itemStyle: {
        borderColor: COLORS.ink + '30',
      },
      inactiveColor: COLORS.ink + '30',
    }],
    animationDuration: 1500,
    animationEasingUpdate: 'quinticInOut',
    series: [{
      type: 'graph',
      layout: 'force',
      roam: true,
      data: chartNodes,
      links: chartLinks,
      categories,
      force: {
        repulsion: 650,
        edgeLength: [80, 160],
        gravity: 0.1,
        friction: 0.2,
      },
      emphasis: {
        focus: 'adjacency',
      },
      select: {
        itemStyle: {
          borderColor: COLORS.gold,
          borderWidth: 5,
        },
        label: {
          fontWeight: 'bold',
        },
      },
      lineStyle: {
        curveness: 0.1,
      },
      label: {
        position: 'bottom',
      },
    }],
  }
}

function initChart() {
  if (!chartRef.value) return
  chartInstance = echarts.init(chartRef.value, null, { renderer: 'canvas' })
  chartInstance.on('click', (params: any) => {
    if (params.dataType === 'node') {
      const node: GenealogyNode = params.data.data
      emit('nodeClick', node)
    } else if (params.dataType === 'edge') {
      const edge: GenealogyEdge = params.data.data
      emit('edgeClick', edge)
    }
  })
  renderChart()
}

function renderChart() {
  if (!chartInstance) return
  if (props.nodes.length === 0) {
    chartInstance.clear()
    return
  }
  chartInstance.setOption(buildOption(), true)
}

function resize() {
  chartInstance?.resize()
}

onMounted(async () => {
  await nextTick()
  initChart()
  window.addEventListener('resize', resize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', resize)
  chartInstance?.dispose()
  chartInstance = null
})

watch(
  () => [props.nodes, props.edges, props.highlightIds, props.selectedId],
  () => {
    renderChart()
  },
  { deep: true },
)

defineExpose({ resize })
</script>

<template>
  <div class="relative w-full h-full min-h-[500px]">
    <div ref="chartRef" class="w-full h-full" />
    <!-- 图例提示 -->
    <div class="absolute bottom-3 right-3 paper-card !p-3 text-xs space-y-2 max-w-xs">
      <div class="font-serif font-bold text-ink-800 mb-1">关系图例</div>
      <div class="flex items-center gap-2">
        <span class="inline-block w-8 h-0.5" style="background:#9E2B25;"></span>
        <span class="text-ink-600">师徒传承（直系）</span>
      </div>
      <div class="flex items-center gap-2">
        <span class="inline-block w-8 border-t border-dashed" style="border-color:#5C7A6B;"></span>
        <span class="text-ink-600">亲属/同门/同事</span>
      </div>
      <div class="pt-2 border-t border-ink-100 text-ink-400 mt-2">
        拖拽节点可调整位置 · 滚轮缩放
      </div>
    </div>
  </div>
</template>
