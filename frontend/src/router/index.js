import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    // ── Público ──────────────────────────────────────────────────
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/LoginView.vue'),
      meta: { requiresAuth: false },
    },

    // ── Panel Administrativo ─────────────────────────────────────
    {
      path: '/admin',
      redirect: '/admin/dashboard',
      meta: { requiresAuth: true, roles: ['admin', 'junta'] },
      children: [
        {
          path: 'dashboard',
          name: 'admin-dashboard',
          component: () => import('@/views/admin/DashboardAdmin.vue'),
        },
        {
          path: 'propietarios',
          name: 'admin-propietarios',
          component: () => import('@/views/admin/GestionPropietarios.vue'),
        },
        {
          path: 'apartamentos',
          name: 'admin-apartamentos',
          component: () => import('@/views/admin/GestionApartamentos.vue'),
        },
        {
          path: 'recibos',
          name: 'admin-recibos',
          component: () => import('@/views/admin/EmisionRecibos.vue'),
        },
        {
          path: 'deudas',
          name: 'admin-deudas',
          component: () => import('@/views/admin/MatrizDeudas.vue'),
        },
        {
          path: 'conciliacion',
          name: 'admin-conciliacion',
          component: () => import('@/views/admin/Conciliacion.vue'),
        },
        {
          path: 'reportes',
          name: 'admin-reportes',
          component: () => import('@/views/admin/Reportes.vue'),
        },
        {
          path: 'perfil',
          name: 'admin-perfil',
          component: () => import('@/views/propietario/MiPerfil.vue'),
        },
      ],
    },

    // ── Portal del Propietario ───────────────────────────────────
    {
      path: '/mi-cuenta',
      redirect: '/mi-cuenta/inicio',
      meta: { requiresAuth: true, roles: ['propietario', 'admin', 'junta'] },
      children: [
        {
          path: 'inicio',
          name: 'propietario-inicio',
          component: () => import('@/views/propietario/MiCuenta.vue'),
        },
        {
          path: 'pagar',
          name: 'propietario-pagar',
          component: () => import('@/views/propietario/ReportarPago.vue'),
        },
        {
          path: 'recibos',
          name: 'propietario-recibos',
          component: () => import('@/views/propietario/MisRecibos.vue'),
        },
        {
          path: 'perfil',
          name: 'propietario-perfil',
          component: () => import('@/views/propietario/MiPerfil.vue'),
        },
      ],
    },

    // ── Redireccionamiento raíz ──────────────────────────────────
    {
      path: '/',
      redirect: () => {
        const auth = useAuthStore()
        if (!auth.isAuthenticated) return '/login'
        if (auth.rol === 'propietario') return '/mi-cuenta/inicio'
        return '/admin/dashboard'
      },
    },

    // ── 404 ──────────────────────────────────────────────────────
    {
      path: '/:pathMatch(.*)*',
      redirect: '/',
    },
  ],
})

// ─── Guard de autenticación y roles ─────────────────────────────────────────
router.beforeEach((to, from, next) => {
  const auth = useAuthStore()

  if (to.meta.requiresAuth === false) {
    return next()
  }

  if (!auth.isAuthenticated) {
    return next({ name: 'login', query: { redirect: to.fullPath } })
  }

  if (to.meta.roles && !to.meta.roles.includes(auth.rol)) {
    // Redirige al área correcta según rol
    if (auth.rol === 'propietario') return next('/mi-cuenta/inicio')
    return next('/admin/dashboard')
  }

  next()
})

export default router
