<template>
  <div class="flex min-h-screen bg-neu-bg overflow-x-hidden">
    <!-- Sidebar Neumórfico (Desktop estático + Mobile Drawer con animaciones) -->
    <NavSidebar :abierto="menuMovilAbierto" @cerrar="menuMovilAbierto = false" />

    <!-- Contenido principal (100% de ancho en móviles y tablets) -->
    <main class="flex-1 w-full min-w-0 p-3 sm:p-5 lg:p-6 flex flex-col gap-5">
      <!-- Header Superior Flotante Neumórfico -->
      <header class="bg-neu-bg-card shadow-neu rounded-neu px-4 py-3 sm:px-6 sm:py-3.5 flex flex-col md:flex-row md:items-center justify-between gap-3 sm:gap-4 border border-white/60">
        <!-- Fila superior / Izquierda: Hamburguesa + Título y Subtítulo -->
        <div class="flex items-center gap-3 min-w-0">
          <!-- Botón Hamburguesa Móvil (Visible solo en pantallas < 1024px) -->
          <button
            @click="menuMovilAbierto = true"
            class="lg:hidden w-10 h-10 rounded-neu-sm bg-neu-bg shadow-neu-sm hover:shadow-neu-inset flex items-center justify-center text-xl text-neu-green border border-white/60 cursor-pointer shrink-0 transition-all"
            title="Abrir Menú de Navegación"
          >
            ☰
          </button>

          <div class="min-w-0">
            <h1 class="text-base sm:text-xl md:text-2xl font-extrabold text-neu-green tracking-tight leading-tight truncate">{{ titulo }}</h1>
            <p v-if="subtitulo" class="text-xs font-medium text-neu-text-light mt-0.5 line-clamp-1 sm:line-clamp-none">{{ subtitulo }}</p>
          </div>
        </div>

        <!-- Derecha: Tasa BCV, Perfil y Botón de Salir perfectamente simétricos en una sola línea -->
        <div class="flex items-center gap-2.5 sm:gap-3 shrink-0 self-end md:self-center">
          <!-- Widget Tasa Oficial BCV -->
          <div v-if="tasaStore.tasaActual" class="bg-neu-bg shadow-neu-sm rounded-neu-sm px-3 py-1.5 border border-white/60 flex items-center gap-2 shrink-0">
            <span class="text-sm">💱</span>
            <div class="text-xs leading-none">
              <span class="text-neu-text-light block text-[9px] uppercase font-bold tracking-wider">Tasa BCV</span>
              <span class="font-extrabold text-neu-green text-xs sm:text-sm mt-0.5 block">Bs. {{ parseFloat(tasaStore.tasaActual).toFixed(2) }}</span>
            </div>
          </div>

          <!-- Perfil de Usuario Neumórfico -->
          <RouterLink
            to="/admin/perfil"
            class="bg-neu-bg shadow-neu-sm hover:shadow-neu-inset rounded-neu-sm px-3 py-1.5 border border-white/60 flex items-center gap-2 sm:gap-2.5 shrink-0 cursor-pointer transition-all"
            title="Ver y editar mis datos"
          >
            <div class="w-8 h-8 rounded-full bg-neu-green text-white font-extrabold flex items-center justify-center text-xs shadow-sm shrink-0">
              {{ authStore.nombre?.charAt(0) || 'A' }}
            </div>
            <div class="text-left hidden sm:block">
              <span class="text-xs font-bold text-neu-text block leading-tight truncate max-w-[120px]">{{ authStore.nombre }}</span>
              <span class="text-[10px] font-semibold text-neu-green uppercase tracking-wider">{{ authStore.rol }}</span>
            </div>
          </RouterLink>

          <!-- Botón Salir con Icono Normal SVG -->
          <button
            @click="cerrarSesion"
            class="group w-9 h-9 sm:w-10 sm:h-10 rounded-neu-sm bg-neu-bg shadow-neu-sm text-neu-danger hover:shadow-neu-inset hover:bg-rose-50/60 transition-all duration-150 flex items-center justify-center font-bold border border-white/60 cursor-pointer shrink-0"
            title="Cerrar Sesión"
          >
            <svg class="w-4 h-4 text-neu-danger transition-transform group-hover:translate-x-0.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 9V5.25A2.25 2.25 0 0013.5 3h-6a2.25 2.25 0 00-2.25 2.25v13.5A2.25 2.25 0 007.5 21h6a2.25 2.25 0 002.25-2.25V15m3 0l3-3m0 0l-3-3m3 3H9" />
            </svg>
          </button>
        </div>
      </header>

      <!-- Slot de Contenido de las Vistas (100% responsivo y adaptable) -->
      <div class="flex-1 flex flex-col gap-6 min-w-0">
        <slot />
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import NavSidebar from './NavSidebar.vue'
import { useAuthStore, useTasaStore } from '@/stores'

defineProps({
  titulo: { type: String, default: 'Panel Administrativo' },
  subtitulo: { type: String, default: '' },
})

const router = useRouter()
const authStore = useAuthStore()
const tasaStore = useTasaStore()
const menuMovilAbierto = ref(false)

onMounted(() => {
  tasaStore.cargarTasa()
})

function cerrarSesion() {
  authStore.logout()
  router.push('/login')
}
</script>
