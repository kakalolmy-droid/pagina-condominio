<template>
  <div class="flex min-h-screen bg-neu-bg overflow-x-hidden">
    <!-- Sidebar Neumórfico (Desktop estático + Mobile Drawer con animaciones) -->
    <NavSidebar :abierto="menuMovilAbierto" @cerrar="menuMovilAbierto = false" />

    <!-- Contenido principal (100% de ancho en móviles y tablets) -->
    <main class="flex-1 w-full min-w-0 p-3 sm:p-5 lg:p-6 flex flex-col gap-5">
      <!-- Header Superior Flotante Neumórfico -->
      <header class="bg-neu-bg-card shadow-neu rounded-neu p-4 sm:px-6 sm:py-4 flex flex-col md:flex-row md:items-center justify-between gap-4 border border-white/60">
        <!-- Fila superior en móvil: Hamburguesa + Título -->
        <div class="flex items-center gap-3">
          <!-- Botón Hamburguesa Móvil (Visible solo en pantallas < 1024px) -->
          <button
            @click="menuMovilAbierto = true"
            class="lg:hidden w-10 h-10 rounded-neu-sm bg-neu-bg shadow-neu-sm hover:shadow-neu-inset flex items-center justify-center text-xl text-neu-green border border-white/60 cursor-pointer shrink-0 transition-all"
            title="Abrir Menú de Navegación"
          >
            ☰
          </button>

          <div>
            <h1 class="text-lg sm:text-2xl font-extrabold text-neu-green tracking-tight leading-tight">{{ titulo }}</h1>
            <p v-if="subtitulo" class="text-xs font-medium text-neu-text-light mt-0.5 line-clamp-2 sm:line-clamp-none">{{ subtitulo }}</p>
          </div>
        </div>

        <!-- Badges y Perfil en Header -->
        <div class="flex items-center gap-2 sm:gap-4 flex-wrap justify-between sm:justify-end">
          <!-- Widget Tasa Oficial BCV -->
          <div v-if="tasaStore.tasaActual" class="bg-neu-bg shadow-neu-sm rounded-neu-sm px-3 py-1.5 sm:px-4 sm:py-2 border border-white/60 flex items-center gap-2 shrink-0">
            <span class="text-sm sm:text-base">💱</span>
            <div class="text-xs">
              <span class="text-neu-text-light block text-[9px] sm:text-[10px] leading-none uppercase font-semibold">Tasa BCV</span>
              <span class="font-extrabold text-neu-green text-xs sm:text-sm">Bs. {{ parseFloat(tasaStore.tasaActual).toFixed(2) }}</span>
            </div>
          </div>

          <div class="flex items-center gap-2">
            <!-- Perfil de Usuario Neumórfico -->
            <RouterLink
              to="/admin/perfil"
              class="bg-neu-bg shadow-neu-sm hover:shadow-neu-inset rounded-neu-sm px-3 py-1.5 sm:px-4 sm:py-2 border border-white/60 flex items-center gap-2 sm:gap-3 shrink-0 cursor-pointer transition-all"
              title="Ver y editar mis datos"
            >
              <div class="w-7 h-7 sm:w-8 sm:h-8 rounded-full bg-neu-green text-white font-bold flex items-center justify-center text-xs shadow-sm">
                {{ authStore.nombre?.charAt(0) || 'A' }}
              </div>
              <div class="text-left hidden sm:block">
                <span class="text-xs font-bold text-neu-text block leading-tight">{{ authStore.nombre }}</span>
                <span class="text-[10px] font-semibold text-neu-green uppercase tracking-wider">{{ authStore.rol }}</span>
              </div>
            </RouterLink>

            <!-- Botón Salir -->
            <button
              @click="cerrarSesion"
              class="w-9 h-9 sm:w-10 sm:h-10 rounded-neu-sm bg-neu-bg shadow-neu-sm text-neu-danger hover:shadow-neu-inset hover:bg-neu-bg-dark transition-all duration-150 flex items-center justify-center font-bold border border-white/60 cursor-pointer shrink-0"
              title="Cerrar Sesión"
            >
              🚪
            </button>
          </div>
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
