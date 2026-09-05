<template>
  <div>
    <!-- Desktop Sidebar Estático (Visible solo en pantallas grandes lg >= 1024px) -->
    <aside class="hidden lg:flex w-68 min-h-screen bg-neu-bg p-5 pr-0 flex-col justify-between select-none shrink-0 sticky top-0 h-screen">
      <!-- Contenedor flotante curvado estilo Neumórfico -->
      <div class="bg-neu-bg-card shadow-neu rounded-neu p-5 flex flex-col gap-6 border border-white/60">
        <!-- Logo y Branding -->
        <div class="flex items-center gap-3.5 pb-4 border-b border-neu-shadow-dark/40">
          <div class="w-12 h-12 rounded-neu-sm bg-neu-bg shadow-neu-sm flex items-center justify-center text-2xl border border-white/60">
            🏢
          </div>
          <div>
            <h2 class="font-extrabold text-neu-green text-base tracking-tight leading-none">Edificio Alcatraz</h2>
            <span class="text-[11px] font-semibold text-neu-text-light uppercase tracking-wider block mt-1">Panel de Control</span>
          </div>
        </div>

        <!-- Navegación Neumórfica -->
        <nav class="flex flex-col gap-2">
          <NavItem
            v-for="item in menuItems"
            :key="item.to"
            v-bind="item"
          />
        </nav>
      </div>

      <!-- Footer Neumórfico -->
      <div class="mt-4 px-4 py-3 bg-neu-bg-card/70 shadow-neu-sm rounded-neu-sm border border-white/50 text-center">
        <p class="text-[11px] font-medium text-neu-text-light">
          © {{ new Date().getFullYear() }} Edificio Alcatraz
        </p>
      </div>
    </aside>

    <!-- Mobile Drawer Neumórfico Flotante (Para teléfonos y tablets < 1024px) -->
    <Teleport to="body">
      <!-- Fondo Oscuro / Backdrop -->
      <Transition name="fade">
        <div
          v-if="abierto"
          class="fixed inset-0 bg-black/50 backdrop-blur-xs z-50 lg:hidden"
          @click="$emit('cerrar')"
        />
      </Transition>

      <!-- Panel Deslizante Lateral -->
      <Transition name="slide">
        <aside
          v-if="abierto"
          class="fixed inset-y-0 left-0 w-72 max-w-[85vw] bg-neu-bg z-50 p-4 flex flex-col justify-between select-none shadow-2xl lg:hidden overflow-y-auto"
        >
          <div class="bg-neu-bg-card shadow-neu rounded-neu p-4 flex flex-col gap-4 border border-white/60">
            <!-- Header con botón cerrar -->
            <div class="flex items-center justify-between pb-3 border-b border-neu-shadow-dark/40">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-neu-sm bg-neu-bg shadow-neu-sm flex items-center justify-center text-xl border border-white/60">
                  🏢
                </div>
                <div>
                  <h2 class="font-extrabold text-neu-green text-sm tracking-tight leading-none">Edificio Alcatraz</h2>
                  <span class="text-[10px] font-semibold text-neu-text-light uppercase tracking-wider block mt-0.5">Menú Principal</span>
                </div>
              </div>

              <button
                @click="$emit('cerrar')"
                class="w-8 h-8 rounded-full bg-neu-bg shadow-neu-sm hover:shadow-neu-inset flex items-center justify-center text-neu-text-light hover:text-neu-danger font-bold text-sm border border-white/60 cursor-pointer"
                title="Cerrar menú"
              >
                ✕
              </button>
            </div>

            <!-- Navegación Móvil -->
            <nav class="flex flex-col gap-2">
              <NavItem
                v-for="item in menuItems"
                :key="item.to"
                v-bind="item"
                @click="$emit('cerrar')"
              />
            </nav>
          </div>

          <!-- Footer Móvil -->
          <div class="mt-4 px-4 py-3 bg-neu-bg-card/70 shadow-neu-sm rounded-neu-sm border border-white/50 text-center">
            <p class="text-[11px] font-medium text-neu-text-light">
              © {{ new Date().getFullYear() }} Edificio Alcatraz
            </p>
          </div>
        </aside>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import NavItem from './NavItem.vue'

defineProps({
  abierto: {
    type: Boolean,
    default: false,
  },
})

defineEmits(['cerrar'])

const menuItems = [
  { to: '/admin/dashboard',     icon: '📊', label: 'Dashboard' },
  { to: '/admin/propietarios',  icon: '👥', label: 'Propietarios' },
  { to: '/admin/apartamentos',  icon: '🏢', label: 'Apartamentos' },
  { to: '/admin/recibos',       icon: '📄', label: 'Recibos' },
  { to: '/admin/deudas',        icon: '💵', label: 'Matriz de Deudas' },
  { to: '/admin/conciliacion',  icon: '⚖️', label: 'Conciliación' },
  { to: '/admin/reportes',      icon: '📱', label: 'Avisos WhatsApp' },
  { to: '/admin/perfil',        icon: '👤', label: 'Mi Perfil' },
]
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.25s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-enter-active,
.slide-leave-active {
  transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}
.slide-enter-from,
.slide-leave-to {
  transform: translateX(-100%);
}
</style>
