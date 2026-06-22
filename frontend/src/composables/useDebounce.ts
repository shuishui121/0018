import { ref, watch, type Ref } from 'vue'

// 对任意响应式值做防抖：延迟同步上游变化，常用于搜索框输入
export function useDebounce<T>(source: Ref<T>, delay = 300) {
  const debounced = ref(source.value) as Ref<T>
  let timer: ReturnType<typeof setTimeout> | undefined

  watch(source, (val) => {
    if (timer) clearTimeout(timer)
    timer = setTimeout(() => {
      debounced.value = val
    }, delay)
  })

  return debounced
}
