<script setup lang="ts">
import { ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { Menu, X, LogOut, ShieldCheck } from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()
const open = ref(false)

const nav = [
  { to: '/directory', label: '名录查询' },
  { to: '/genres', label: '剧种百科' },
]

function handleAuth() {
  if (auth.isAuthenticated) {
    auth.logout()
    router.push('/')
  } else {
    router.push('/login')
  }
}
</script>

<template>
  <header
    class="sticky top-0 z-40 border-b border-ink-200/60 bg-paper/90 backdrop-blur supports-[backdrop-filter]:bg-paper/75"
  >
    <div class="container flex h-16 items-center justify-between gap-4">
      <RouterLink to="/" class="flex items-center gap-3">
        <span
          class="seal-stamp h-9 w-9 rounded-sm text-lg leading-none"
          aria-hidden="true"
        >
          梨
        </span>
        <span class="flex flex-col leading-none">
          <span class="display-serif text-lg text-ink-900">梨园典藏</span>
          <span class="text-[10px] tracking-[0.3em] text-ink-400"
            >OPERA HERITAGE</span
          >
        </span>
      </RouterLink>

      <nav class="hidden items-center gap-1 md:flex">
        <RouterLink
          v-for="item in nav"
          :key="item.to"
          :to="item.to"
          class="rounded-sm px-4 py-2 text-sm text-ink-600 transition-colors hover:bg-ink-50 hover:text-ink-900"
          active-class="!text-vermilion"
        >
          {{ item.label }}
        </RouterLink>
        <RouterLink
          to="/admin"
          class="flex items-center gap-1.5 rounded-sm px-4 py-2 text-sm text-ink-600 transition-colors hover:bg-ink-50 hover:text-ink-900"
          active-class="!text-vermilion"
        >
          <ShieldCheck class="h-4 w-4" />
          后台管理
        </RouterLink>
      </nav>

      <div class="flex items-center gap-2">
        <button
          v-if="auth.isAuthenticated"
          class="hidden items-center gap-1.5 rounded-sm px-3 py-2 text-sm text-ink-600 transition-colors hover:text-vermilion md:flex"
          @click="handleAuth"
        >
          <LogOut class="h-4 w-4" />
          退出
        </button>
        <button
          class="inline-flex h-10 w-10 items-center justify-center rounded-sm text-ink-700 md:hidden"
          aria-label="菜单"
          @click="open = !open"
        >
          <component :is="open ? X : Menu" class="h-5 w-5" />
        </button>
      </div>
    </div>

    <transition name="drawer">
      <div v-if="open" class="border-t border-ink-200/60 bg-paper md:hidden">
        <nav class="container flex flex-col py-2">
          <RouterLink
            v-for="item in [...nav, { to: '/admin', label: '后台管理' }]"
            :key="item.to"
            :to="item.to"
            class="rounded-sm px-3 py-3 text-sm text-ink-700 hover:bg-ink-50"
            active-class="!text-vermilion"
            @click="open = false"
          >
            {{ item.label }}
          </RouterLink>
          <button
            class="flex items-center gap-1.5 rounded-sm px-3 py-3 text-left text-sm text-ink-700 hover:bg-ink-50"
            @click="open = false; handleAuth()"
          >
            <LogOut class="h-4 w-4" />
            {{ auth.isAuthenticated ? '退出登录' : '管理员登录' }}
          </button>
        </nav>
      </div>
    </transition>
  </header>
</template>

<style scoped>
.drawer-enter-active,
.drawer-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.drawer-enter-from,
.drawer-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}
</style>
