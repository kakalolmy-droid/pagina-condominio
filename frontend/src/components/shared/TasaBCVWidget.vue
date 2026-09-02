<template>
  <div class="card-neu-sm flex items-center gap-3">
    <div class="text-2xl">💱</div>
    <div v-if="tasaStore.tasaActual">
      <p class="text-xs text-neu-text-light">Tasa BCV oficial</p>
      <p class="font-bold text-neu-green">{{ formatTasa(tasaStore.tasaActual) }}</p>
      <p class="text-xs text-neu-text-light">{{ formatFecha(tasaStore.fecha) }}</p>
    </div>
    <div v-else-if="tasaStore.cargando">
      <p class="text-xs text-neu-text-light">Consultando BCV...</p>
    </div>
    <div v-else>
      <p class="text-xs text-neu-danger">Tasa no disponible</p>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useTasaStore } from '@/stores'
import { formatTasa, formatFecha } from '@/utils'

const tasaStore = useTasaStore()
onMounted(() => tasaStore.cargarTasa())
</script>
