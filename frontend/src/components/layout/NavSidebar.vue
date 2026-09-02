<template>
  <aside class="w-68 min-h-screen bg-neu-bg p-5 flex flex-col justify-between select-none">
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
</template>

<script setup>
import NavItem from './NavItem.vue'

const menuItems = [
  { to: '/admin/dashboard',     icon: '📊', label: 'Dashboard' },
  { to: '/admin/propietarios',  icon: '👥', label: 'Propietarios' },
  { to: '/admin/apartamentos',  icon: '🏢', label: 'Apartamentos' },
  { to: '/admin/recibos',       icon: '📄', label: 'Recibos' },
  { to: '/admin/deudas',        icon: '💵', label: 'Matriz de Deudas' },
  { to: '/admin/conciliacion',  icon: '⚖️', label: 'Conciliación' },
  { to: '/admin/reportes',      icon: '📱', label: 'Avisos WhatsApp' },
]
</script>
