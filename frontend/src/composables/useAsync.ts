import { ref, shallowRef, type Ref } from 'vue'

interface UseAsyncOptions {
  immediate?: boolean
}

// 统一的异步数据获取封装：管理 loading/error/data 与手动刷新
export function useAsync<T>(
  fn: () => Promise<T>,
  options: UseAsyncOptions = {},
) {
  const data = shallowRef<T | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function run() {
    loading.value = true
    error.value = null
    try {
      data.value = await fn()
    } catch (e) {
      error.value = e instanceof Error ? e.message : '请求失败'
    } finally {
      loading.value = false
    }
  }

  if (options.immediate !== false) {
    run()
  }

  return { data, loading, error, run, refresh: run }
}

export type UseAsyncReturn<T> = ReturnType<typeof useAsync<T>>
