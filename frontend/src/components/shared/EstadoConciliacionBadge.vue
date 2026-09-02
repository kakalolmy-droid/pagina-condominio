<template>
  <NeuBadge :variant="info.variant" :label="info.label" />
</template>

<script setup>
import { computed } from 'vue'
import NeuBadge from '@/components/neumorph/NeuBadge.vue'
import { estadoConciliacion } from '@/utils'

const props = defineProps({
  estado: { type: String, required: true },
})

const info = computed(() => estadoConciliacion(props.estado))
</script>
