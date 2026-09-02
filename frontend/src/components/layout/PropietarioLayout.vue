<template>
  <div class="min-h-screen bg-neu-bg p-5 flex flex-col gap-6">
    <!-- Header Superior para el Propietario -->
    <header class="bg-neu-bg-card shadow-neu rounded-neu px-8 py-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4 border border-white/60">
      <div class="flex items-center gap-3.5">
        <div class="w-12 h-12 rounded-neu-sm bg-neu-bg shadow-neu-sm flex items-center justify-center text-2xl border border-white/60">
          🏢
        </div>
        <div>
          <h1 class="text-xl font-extrabold text-neu-green tracking-tight">Edificio Alcatraz</h1>
          <p class="text-xs text-neu-text-light font-medium">Portal de Autogestión del Residente</p>
        </div>
      </div>

      <!-- Navegación y Perfil -->
      <div class="flex items-center gap-3 flex-wrap">
        <RouterLink
          to="/mi-cuenta/inicio"
          class="px-4 py-2 rounded-neu-sm text-xs font-bold text-neu-text transition-all"
          active-class="shadow-neu-inset text-neu-green bg-neu-bg-dark border border-white/40"
        >
          🏠 Mi Cuenta
        </RouterLink>

        <RouterLink
          to="/mi-cuenta/pagar"
          class="px-4 py-2 rounded-neu-sm text-xs font-bold text-neu-text transition-all"
          active-class="shadow-neu-inset text-neu-green bg-neu-bg-dark border border-white/40"
        >
          💳 Reportar Pago
        </RouterLink>

        <RouterLink
          to="/mi-cuenta/recibos"
          class="px-4 py-2 rounded-neu-sm text-xs font-bold text-neu-text transition-all"
          active-class="shadow-neu-inset text-neu-green bg-neu-bg-dark border border-white/40"
        >
          📄 Mis Recibos
        </RouterLink>

        <!-- Botón Salir -->
        <button
          @click="cerrarSesion"
          class="w-9 h-9 rounded-neu-sm bg-neu-bg shadow-neu-sm text-neu-danger hover:shadow-neu-inset transition-all flex items-center justify-center font-bold border border-white/60 cursor-pointer ml-2"
          title="Cerrar Sesión"
        >
          🚪
        </button>
      </div>
    </header>

    <!-- Contenido -->
    <main class="flex-1">
      <slot />
    </main>

    <!-- Footer -->
    <footer class="text-center text-xs text-neu-text-light py-4">
      © {{ new Date().getFullYear() }} Edificio Alcatraz — Sistema de Gestión de Condominio
    </footer>
  </div>
</template>

<script setup>
import { RouterLink, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores'

const router = useRouter()
const authStore = useAuthStore()

function cerrarSesion() {
  authStore.logout()
  router.push('/login')
}
</script>
