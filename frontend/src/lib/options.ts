// 共享下拉与单选选项，供 FilterBar 与后台表单复用，保证口径一致

// 行当：戏曲四大行当
export const ROLE_OPTIONS = ['生', '旦', '净', '末', '丑'] as const

// 地区：中国七大地理分区
export const REGION_OPTIONS = [
  '华北',
  '东北',
  '华东',
  '华中',
  '华南',
  '西南',
  '西北',
] as const

// 年龄段
export const AGE_GROUP_OPTIONS = ['青年', '中年', '老年'] as const

// 性别
export const GENDER_OPTIONS = ['男', '女'] as const

// 拼音首字母索引（含 # 兜底）
export const PINYIN_INITIALS = [
  'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
  'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
  '#',
] as const
