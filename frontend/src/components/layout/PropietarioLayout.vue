<template>
  <div class="min-h-screen bg-neu-bg p-3 sm:p-5 flex flex-col gap-5 overflow-x-hidden">
    <!-- Header Superior para el Propietario -->
    <header class="bg-neu-bg-card shadow-neu rounded-neu p-4 sm:px-8 sm:py-5 flex flex-col md:flex-row md:items-center justify-between gap-4 border border-white/60">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="w-11 h-11 sm:w-12 sm:h-12 rounded-neu-sm bg-neu-bg shadow-neu-sm flex items-center justify-center text-xl sm:text-2xl border border-white/60 shrink-0">
            🏢
          </div>
          <div>
            <h1 class="text-lg sm:text-xl font-extrabold text-neu-green tracking-tight leading-tight">Edificio Alcatraz</h1>
            <p class="text-xs text-neu-text-light font-medium">Portal de Autogestión del Residente</p>
          </div>
        </div>

        <!-- Botón Salir Móvil (visible solo en pantallas chicas) -->
        <button
          @click="cerrarSesion"
          class="md:hidden w-9 h-9 rounded-neu-sm bg-neu-bg shadow-neu-sm text-neu-danger hover:shadow-neu-inset transition-all flex items-center justify-center font-bold border border-white/60 cursor-pointer"
          title="Cerrar Sesión"
        >
          🚪
        </button>
      </div>

      <!-- Navegación y Perfil -->
      <div class="flex items-center gap-2 sm:gap-3 flex-wrap justify-between sm:justify-end">
        <div class="flex items-center gap-1.5 sm:gap-2 flex-wrap">
          <RouterLink
            to="/mi-cuenta/inicio"
            class="px-3 py-1.5 sm:px-4 sm:py-2 rounded-neu-sm text-xs font-bold text-neu-text transition-all"
            active-class="shadow-neu-inset text-neu-green bg-neu-bg-dark border border-white/40"
          >
            🏠 Mi Cuenta
          </RouterLink>

          <RouterLink
            to="/mi-cuenta/pagar"
            class="px-3 py-1.5 sm:px-4 sm:py-2 rounded-neu-sm text-xs font-bold text-neu-text transition-all"
            active-class="shadow-neu-inset text-neu-green bg-neu-bg-dark border border-white/40"
          >
            💳 Reportar Pago
          </RouterLink>

          <RouterLink
            to="/mi-cuenta/recibos"
            class="px-3 py-1.5 sm:px-4 sm:py-2 rounded-neu-sm text-xs font-bold text-neu-text transition-all"
            active-class="shadow-neu-inset text-neu-green bg-neu-bg-dark border border-white/40"
          >
            📄 Mis Recibos
          </RouterLink>
        </div>

        <!-- Botón Salir Desktop -->
        <button
          @click="cerrarSesion"
          class="hidden md:flex w-9 h-9 rounded-neu-sm bg-neu-bg shadow-neu-sm text-neu-danger hover:shadow-neu-inset transition-all items-center justify-center font-bold border border-white/60 cursor-pointer ml-2"
          title="Cerrar Sesión"
        >
          🚪
        </button>
      </div>
    </header>

    <!-- Contenido -->
    <main class="flex-1 min-w-0">
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
