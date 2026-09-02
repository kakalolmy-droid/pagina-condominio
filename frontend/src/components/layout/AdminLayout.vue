<template>
  <div class="flex min-h-screen bg-neu-bg">
    <!-- Sidebar Flotante Neumórfico -->
    <NavSidebar />

    <!-- Contenido principal -->
    <main class="flex-1 overflow-auto p-5 pl-0 flex flex-col gap-6">
      <!-- Header Superior Flotante Estilo Smart Dashboard -->
      <header class="bg-neu-bg-card shadow-neu rounded-neu px-8 py-5 flex flex-col md:flex-row md:items-center justify-between gap-4 border border-white/60">
        <div>
          <h1 class="text-2xl font-extrabold text-neu-green tracking-tight">{{ titulo }}</h1>
          <p v-if="subtitulo" class="text-xs font-medium text-neu-text-light mt-0.5">{{ subtitulo }}</p>
        </div>

        <div class="flex items-center gap-4">
          <!-- Widget Tasa Oficial BCV -->
          <div v-if="tasaStore.tasaActual" class="bg-neu-bg shadow-neu-sm rounded-neu-sm px-4 py-2 border border-white/60 flex items-center gap-2">
            <span class="text-base">💱</span>
            <div class="text-xs">
              <span class="text-neu-text-light block text-[10px] leading-none uppercase font-semibold">Tasa Oficial BCV</span>
              <span class="font-extrabold text-neu-green">Bs. {{ parseFloat(tasaStore.tasaActual).toFixed(2) }} / $1</span>
            </div>
          </div>

          <!-- Perfil de Usuario Neumórfico -->
          <div class="bg-neu-bg shadow-neu-sm rounded-neu-sm px-4 py-2 border border-white/60 flex items-center gap-3">
            <div class="w-8 h-8 rounded-full bg-neu-green text-white font-bold flex items-center justify-center text-xs shadow-sm">
              {{ authStore.nombre?.charAt(0) || 'A' }}
            </div>
            <div class="text-left">
              <span class="text-xs font-bold text-neu-text block leading-tight">{{ authStore.nombre }}</span>
              <span class="text-[10px] font-semibold text-neu-green uppercase tracking-wider">{{ authStore.rol }}</span>
            </div>
          </div>

          <!-- Botón Salir -->
          <button
            @click="cerrarSesion"
            class="w-10 h-10 rounded-neu-sm bg-neu-bg shadow-neu-sm text-neu-danger hover:shadow-neu-inset hover:bg-neu-bg-dark transition-all duration-150 flex items-center justify-center font-bold border border-white/60 cursor-pointer"
            title="Cerrar Sesión"
          >
            🚪
          </button>
        </div>
      </header>

      <!-- Slot de Contenido de las Vistas -->
      <div class="flex-1 flex flex-col gap-6">
        <slot />
      </div>
    </main>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import NavSidebar from './NavSidebar.vue'
import { useAuthStore, useTasaStore } from '@/stores'

defineProps({
  titulo: { type: String, default: 'Panel Administrativo' },
  subtitulo: { type: String, default: '' },
})

const router = useRouter()
const authStore = useAuthStore()
const tasaStore = useTasaStore()

onMounted(() => {
  tasaStore.cargarTasa()
})

function cerrarSesion() {
  authStore.logout()
  router.push('/login')
}
</script>
