<script setup lang="ts">
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { LogIn, LoaderCircle, ShieldCheck } from 'lucide-vue-next'
import { api } from '@/lib/api'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const username = ref('')
const password = ref('')
const loading = ref(false)
const errorMsg = ref<string | null>(null)

async function submit() {
  errorMsg.value = null
  if (!username.value.trim() || !password.value) {
    errorMsg.value = '请输入用户名与密码'
    return
  }
  loading.value = true
  try {
    const res = await api.login(username.value.trim(), password.value)
    auth.setAuth(res.access_token, username.value.trim())
    const redirect = (route.query.redirect as string) || '/admin'
    router.push(redirect)
  } catch (err) {
    errorMsg.value = err instanceof Error ? err.message : '登录失败'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="container flex min-h-[70vh] items-center justify-center py-12">
    <div class="w-full max-w-md">
      <!-- 顶部印章 -->
      <div class="mb-6 flex flex-col items-center text-center">
        <span class="seal-stamp animate-seal-stamp h-14 w-14 rounded-sm font-seal text-xl">梨</span>
        <span class="label-eyebrow mt-4">ADMIN LOGIN · 管理员登录</span>
        <h1 class="display-serif mt-2 text-3xl text-ink-900">进入后台</h1>
        <div class="vermilion-divider mt-3" />
      </div>

      <form class="paper-card space-y-4" @submit.prevent="submit">
        <label class="block">
          <span class="label-eyebrow !text-[10px]">用户名</span>
          <input
            v-model="username"
            class="input-field mt-1"
            placeholder="请输入管理员账号"
            autocomplete="username"
            style="min-height: 48px"
          />
        </label>

        <label class="block">
          <span class="label-eyebrow !text-[10px]">密码</span>
          <input
            v-model="password"
            type="password"
            class="input-field mt-1"
            placeholder="请输入密码"
            autocomplete="current-password"
            style="min-height: 48px"
          />
        </label>

        <p v-if="errorMsg" class="text-sm text-vermilion">{{ errorMsg }}</p>

        <button type="submit" class="btn-primary w-full" :disabled="loading">
          <LoaderCircle v-if="loading" class="h-4 w-4 animate-spin" />
          <LogIn v-else class="h-4 w-4" />
          {{ loading ? '登录中…' : '登录' }}
        </button>

        <p class="flex items-center justify-center gap-1 text-xs text-ink-400">
          <ShieldCheck class="h-3 w-3" />仅授权管理员可访问后台
        </p>
      </form>
    </div>
  </div>
</template>
