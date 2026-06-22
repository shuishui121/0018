import { useAuthStore } from '@/stores/auth'

export const API_BASE = import.meta.env.VITE_API_BASE || '/api'

export interface Genre {
  id: number
  name: string
  pinyin: string | null
  history: string | null
  art_features: string | null
  classic_plays: string | null
  main_schools: string | null
  distribution_areas: string | null
  cover_image: string | null
}

export interface Troupe {
  id: number
  name: string
  genre_id: number | null
  region: string | null
  description: string | null
}

export interface InheritorListItem {
  id: number
  name: string
  pinyin_initial: string | null
  gender: string | null
  birth_date: string | null
  age_group: string | null
  genre_id: number | null
  genre_name: string | null
  role_type: string | null
  region: string | null
  avatar: string | null
  master_id: number | null
  master_name: string | null
  bio: string | null
}

export interface Learning {
  id: number
  year: number | null
  title: string | null
  description: string | null
}

export interface InheritorPlay {
  id: number
  play_id: number | null
  play_name: string | null
  role_name: string | null
}

export interface Award {
  id: number
  name: string | null
  year: number | null
  level: string | null
}

export interface Media {
  id: number
  type: string | null
  title: string | null
  file_path: string | null
  description: string | null
}

export interface InheritorDetail extends InheritorListItem {
  learning: Learning[]
  plays: InheritorPlay[]
  awards: Award[]
  media: Media[]
}

export interface GenreDetail extends Genre {
  inheritors: InheritorListItem[]
  troupes: Troupe[]
}

export interface Page<T> {
  items: T[]
  total: number
  page: number
  size: number
}

export interface InheritorFilters {
  genre?: number | null
  role?: string | null
  region?: string | null
  master?: number | null
  age_group?: string | null
  pinyin?: string | null
  keyword?: string | null
  page?: number
  size?: number
}

export interface InheritorInput {
  name: string
  gender?: string | null
  birth_date?: string | null
  age_group?: string | null
  genre_id?: number | null
  role_type?: string | null
  region?: string | null
  master_id?: number | null
  avatar?: string | null
  bio?: string | null
}

export interface BatchImportResult {
  total: number
  success: number
  failed: number
  errors: string[]
  elapsed_ms: number
}

export interface UploadResult {
  url: string
  filename: string
  size: number
}

// ==================== 传承人关系 ====================
export interface InheritorRelationItem {
  inheritor: InheritorListItem
  relation_type: string
  relation_label: string
  distance: number
  shared_learning: string | null
  direction: string | null
}

export interface InheritorRelationsResponse {
  center: InheritorListItem
  relations: InheritorRelationItem[]
}

// ==================== 剧种谱系 ====================
export interface GenealogyNode {
  id: number
  name: string
  role_type: string | null
  avatar: string | null
  region: string | null
  genre_id: number | null
  master_id: number | null
  generation: number
  children: GenealogyNode[]
}

export interface GenealogyEdge {
  source: number
  target: number
  relation_type: string
  relation_label: string
}

export interface GenealogyResponse {
  genre: Genre
  nodes: GenealogyNode[]
  edges: GenealogyEdge[]
  max_generation: number
}

export interface GenealogyFilters {
  max_generations?: number
  keyword?: string
  region?: string
}

async function request<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const auth = useAuthStore()
  const headers = new Headers(options.headers)
  if (!(options.body instanceof FormData) && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json')
  }
  if (auth.token) {
    headers.set('Authorization', `Bearer ${auth.token}`)
  }

  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  })

  if (res.status === 401) {
    auth.logout()
  }

  if (!res.ok) {
    let detail = res.statusText
    try {
      const err = await res.json()
      detail = err.detail || err.message || detail
    } catch {
      /* ignore */
    }
    throw new Error(typeof detail === 'string' ? detail : JSON.stringify(detail))
  }

  if (res.status === 204) return undefined as T
  return (await res.json()) as T
}

function toQuery(filters: Record<string, unknown>): string {
  const params = new URLSearchParams()
  Object.entries(filters).forEach(([k, v]) => {
    if (v !== undefined && v !== null && v !== '') {
      params.append(k, String(v))
    }
  })
  const s = params.toString()
  return s ? `?${s}` : ''
}

export const api = {
  // 传承人
  listInheritors(filters: InheritorFilters = {}) {
    return request<Page<InheritorListItem>>(
      `/inheritors${toQuery(filters as Record<string, unknown>)}`,
    )
  },
  searchInheritors(keyword: string) {
    return request<InheritorListItem[]>(
      `/inheritors/search${toQuery({ keyword })}`,
    )
  },
  pinyinInheritors(initial: string) {
    return request<InheritorListItem[]>(
      `/inheritors/pinyin/${encodeURIComponent(initial)}`,
    )
  },
  getInheritor(id: number) {
    return request<InheritorDetail>(`/inheritors/${id}`)
  },
  createInheritor(data: InheritorInput) {
    return request<InheritorDetail>('/inheritors', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  },
  updateInheritor(id: number, data: InheritorInput) {
    return request<InheritorDetail>(`/inheritors/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    })
  },
  deleteInheritor(id: number) {
    return request<void>(`/inheritors/${id}`, { method: 'DELETE' })
  },
  batchImport(file: File) {
    const form = new FormData()
    form.append('file', file)
    return request<BatchImportResult>('/inheritors/batch', {
      method: 'POST',
      body: form,
    })
  },
  // 剧种
  listGenres() {
    return request<Genre[]>('/genres')
  },
  getGenre(id: number) {
    return request<GenreDetail>(`/genres/${id}`)
  },
  getGenreGenealogy(id: number, filters: GenealogyFilters = {}) {
    return request<GenealogyResponse>(`/genres/${id}/genealogy${toQuery(filters as Record<string, unknown>)}`)
  },
  // 传承人关系
  getInheritorRelations(id: number, filters: { relation_type?: string; max_distance?: number } = {}) {
    return request<InheritorRelationsResponse>(
      `/inheritors/${id}/relations${toQuery(filters as Record<string, unknown>)}`,
    )
  },
  // 上传
  uploadAvatar(file: File) {
    const form = new FormData()
    form.append('file', file)
    return request<UploadResult>('/upload/avatar', {
      method: 'POST',
      body: form,
    })
  },
  uploadMedia(file: File, inheritorId: number, type: string, title: string) {
    const form = new FormData()
    form.append('file', file)
    form.append('inheritor_id', String(inheritorId))
    form.append('type', type)
    form.append('title', title)
    return request<Media>('/upload/media', { method: 'POST', body: form })
  },
  // 鉴权
  login(username: string, password: string) {
    return request<{ access_token: string; token_type: string }>(
      '/auth/login',
      { method: 'POST', body: JSON.stringify({ username, password }) },
    )
  },
}

export function mediaUrl(path: string | null | undefined): string {
  if (!path) return ''
  if (path.startsWith('http')) return path
  return path.startsWith('/') ? path : `/${path}`
}
