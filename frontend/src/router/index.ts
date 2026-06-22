import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '@/pages/HomePage.vue'
import DirectoryPage from '@/pages/DirectoryPage.vue'
import InheritorDetailPage from '@/pages/InheritorDetailPage.vue'
import GenresPage from '@/pages/GenresPage.vue'
import GenreDetailPage from '@/pages/GenreDetailPage.vue'
import GenealogyPage from '@/pages/GenealogyPage.vue'
import AdminPage from '@/pages/AdminPage.vue'
import AdminInheritorFormPage from '@/pages/AdminInheritorFormPage.vue'
import AdminImportPage from '@/pages/AdminImportPage.vue'
import LoginPage from '@/pages/LoginPage.vue'
import { useAuthStore } from '@/stores/auth'

const routes = [
  { path: '/', name: 'home', component: HomePage },
  { path: '/directory', name: 'directory', component: DirectoryPage },
  { path: '/inheritor/:id', name: 'inheritor', component: InheritorDetailPage },
  { path: '/genres', name: 'genres', component: GenresPage },
  { path: '/genres/:id', name: 'genre', component: GenreDetailPage },
  { path: '/genres/:id/genealogy', name: 'genealogy', component: GenealogyPage },
  { path: '/login', name: 'login', component: LoginPage },
  { path: '/admin', name: 'admin', component: AdminPage, meta: { requiresAuth: true } },
  { path: '/admin/inheritor/new', name: 'admin-new', component: AdminInheritorFormPage, meta: { requiresAuth: true } },
  { path: '/admin/inheritor/:id/edit', name: 'admin-edit', component: AdminInheritorFormPage, meta: { requiresAuth: true } },
  { path: '/admin/import', name: 'admin-import', component: AdminImportPage, meta: { requiresAuth: true } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(_to, _from, saved) {
    return saved || { top: 0 }
  },
})

router.beforeEach((to) => {
  if (to.meta.requiresAuth) {
    const auth = useAuthStore()
    if (!auth.isAuthenticated) {
      return { name: 'login', query: { redirect: to.fullPath } }
    }
  }
})

export default router
