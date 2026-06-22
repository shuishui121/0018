<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft, Save, UploadCloud, LoaderCircle, Check } from 'lucide-vue-next'
import { api, mediaUrl, type Genre, type InheritorListItem, type InheritorInput } from '@/lib/api'
import { ROLE_OPTIONS, REGION_OPTIONS, AGE_GROUP_OPTIONS, GENDER_OPTIONS } from '@/lib/options'
import SectionHeader from '@/components/SectionHeader.vue'
import Loading from '@/components/Loading.vue'

const route = useRoute()
const router = useRouter()

const isEdit = computed(() => route.params.id !== undefined)
const editId = computed(() => (isEdit.value ? Number(route.params.id) : null))

const genres = ref<Genre[]>([])
const masters = ref<InheritorListItem[]>([])
const pageLoading = ref(false)
const saving = ref(false)
const errorMsg = ref<string | null>(null)
const done = ref(false)

// 表单数据
const form = reactive<InheritorInput>({
  name: '',
  gender: null,
  birth_date: null,
  age_group: null,
  genre_id: null,
  role_type: null,
  region: null,
  master_id: null,
  avatar: null,
  bio: null,
})

// 头像上传
const localPreview = ref<string | null>(null)
const uploading = ref(false)
const avatarPreview = computed(() => localPreview.value || mediaUrl(form.avatar))

async function onAvatarChange(e: Event) {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  localPreview.value = URL.createObjectURL(file)
  uploading.value = true
  try {
    const res = await api.uploadAvatar(file)
    form.avatar = res.url
  } catch (err) {
    errorMsg.value = err instanceof Error ? err.message : '头像上传失败'
  } finally {
    uploading.value = false
  }
}

async function submit() {
  errorMsg.value = null
  done.value = false
  if (!form.name?.trim()) {
    errorMsg.value = '请填写姓名'
    return
  }
  saving.value = true
  try {
    if (isEdit.value && editId.value) {
      await api.updateInheritor(editId.value, { ...form })
    } else {
      await api.createInheritor({ ...form })
    }
    done.value = true
    setTimeout(() => router.push('/admin'), 600)
  } catch (err) {
    errorMsg.value = err instanceof Error ? err.message : '保存失败'
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  pageLoading.value = true
  try {
    const [g, m] = await Promise.all([
      api.listGenres(),
      api.listInheritors({ size: 200 }),
    ])
    genres.value = g
    masters.value = m.items
    // 编辑模式回填
    if (isEdit.value && editId.value) {
      const d = await api.getInheritor(editId.value)
      Object.assign(form, {
        name: d.name,
        gender: d.gender,
        birth_date: d.birth_date?.slice(0, 10) || null,
        age_group: d.age_group,
        genre_id: d.genre_id,
        role_type: d.role_type,
        region: d.region,
        master_id: d.master_id,
        avatar: d.avatar,
        bio: d.bio,
      })
    }
  } catch (err) {
    errorMsg.value = err instanceof Error ? err.message : '数据加载失败'
  } finally {
    pageLoading.value = false
  }
})
</script>

<template>
  <div class="container py-8 md:py-12">
    <button class="btn-ghost mb-6" @click="router.push('/admin')">
      <ArrowLeft class="h-4 w-4" /> 返回列表
    </button>

    <header class="mb-8">
      <span class="label-eyebrow">{{ isEdit ? 'EDIT · 编辑档案' : 'NEW · 新建档案' }}</span>
      <h1 class="section-title mt-2">{{ isEdit ? '编辑传承人' : '新增传承人' }}</h1>
      <div class="vermilion-divider mt-3" />
    </header>

    <Loading v-if="pageLoading" text="加载中…" />

    <form v-else class="space-y-8" @submit.prevent="submit">
      <!-- 基本信息 -->
      <section>
        <SectionHeader index="01" eyebrow="PROFILE" title="基本信息" />
        <div class="paper-card mt-4 grid grid-cols-1 gap-4 md:grid-cols-2">
          <label class="flex flex-col gap-1">
            <span class="label-eyebrow !text-[10px]">姓名 *</span>
            <input v-model="form.name" class="input-field" placeholder="传承人姓名" />
          </label>
          <label class="flex flex-col gap-1">
            <span class="label-eyebrow !text-[10px]">性别</span>
            <select v-model="form.gender" class="input-field">
              <option :value="null">未填写</option>
              <option v-for="g in GENDER_OPTIONS" :key="g" :value="g">{{ g }}</option>
            </select>
          </label>
          <label class="flex flex-col gap-1">
            <span class="label-eyebrow !text-[10px]">出生日期</span>
            <input v-model="form.birth_date" type="date" class="input-field" />
          </label>
          <label class="flex flex-col gap-1">
            <span class="label-eyebrow !text-[10px]">年龄段</span>
            <select v-model="form.age_group" class="input-field">
              <option :value="null">未填写</option>
              <option v-for="a in AGE_GROUP_OPTIONS" :key="a" :value="a">{{ a }}</option>
            </select>
          </label>
        </div>
      </section>

      <!-- 专业归属 -->
      <section>
        <SectionHeader index="02" eyebrow="CRAFT" title="专业归属" />
        <div class="paper-card mt-4 grid grid-cols-1 gap-4 md:grid-cols-2">
          <label class="flex flex-col gap-1">
            <span class="label-eyebrow !text-[10px]">剧种</span>
            <select v-model="form.genre_id" class="input-field">
              <option :value="null">未选择</option>
              <option v-for="g in genres" :key="g.id" :value="g.id">{{ g.name }}</option>
            </select>
          </label>
          <label class="flex flex-col gap-1">
            <span class="label-eyebrow !text-[10px]">行当</span>
            <select v-model="form.role_type" class="input-field">
              <option :value="null">未选择</option>
              <option v-for="r in ROLE_OPTIONS" :key="r" :value="r">{{ r }}</option>
            </select>
          </label>
          <label class="flex flex-col gap-1">
            <span class="label-eyebrow !text-[10px]">地区</span>
            <select v-model="form.region" class="input-field">
              <option :value="null">未选择</option>
              <option v-for="r in REGION_OPTIONS" :key="r" :value="r">{{ r }}</option>
            </select>
          </label>
          <label class="flex flex-col gap-1">
            <span class="label-eyebrow !text-[10px]">师承</span>
            <select v-model="form.master_id" class="input-field">
              <option :value="null">无</option>
              <option
                v-for="m in masters"
                :key="m.id"
                :value="m.id"
                :disabled="isEdit && m.id === editId"
              >
                {{ m.name }}<span v-if="m.genre_name"> · {{ m.genre_name }}</span>
              </option>
            </select>
          </label>
        </div>
      </section>

      <!-- 头像与简介 -->
      <section>
        <SectionHeader index="03" eyebrow="ARCHIVE" title="头像与简介" />
        <div class="paper-card mt-4 grid grid-cols-1 gap-4 md:grid-cols-3">
          <div class="flex flex-col gap-2">
            <span class="label-eyebrow !text-[10px]">头像</span>
            <div
              class="flex aspect-square w-full items-center justify-center overflow-hidden rounded-sm border border-ink-200 bg-paper-warm"
            >
              <img v-if="avatarPreview" :src="avatarPreview" alt="头像预览" class="h-full w-full object-cover" />
              <span v-else class="font-serif text-3xl text-ink-300">像</span>
            </div>
            <label class="btn-ghost cursor-pointer justify-center">
              <UploadCloud class="h-4 w-4" />
              {{ uploading ? '上传中…' : '选择头像' }}
              <input type="file" accept="image/*" class="hidden" @change="onAvatarChange" />
            </label>
          </div>
          <label class="flex flex-col gap-1 md:col-span-2">
            <span class="label-eyebrow !text-[10px]">个人简介</span>
            <textarea
              v-model="form.bio"
              rows="6"
              class="input-field resize-y"
              placeholder="简述传承人的艺术经历与成就…"
            />
          </label>
        </div>
      </section>

      <!-- 操作区 -->
      <div class="flex flex-col items-center gap-3">
        <p v-if="errorMsg" class="text-sm text-vermilion">{{ errorMsg }}</p>
        <p v-if="done" class="flex items-center gap-1 text-sm text-celadon">
          <Check class="h-4 w-4" /> 保存成功，正在返回…
        </p>
        <button type="submit" class="btn-primary min-w-40" :disabled="saving">
          <LoaderCircle v-if="saving" class="h-4 w-4 animate-spin" />
          <Save v-else class="h-4 w-4" />
          {{ saving ? '保存中…' : '保存档案' }}
        </button>
      </div>
    </form>
  </div>
</template>
