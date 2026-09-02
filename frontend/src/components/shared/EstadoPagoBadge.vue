<template>
  <NeuBadge :variant="info.variant" :label="info.label" />
</template>

<script setup>
import { computed } from 'vue'
import NeuBadge from '@/components/neumorph/NeuBadge.vue'
import { estadoPago } from '@/utils'

const props = defineProps({
  estado: { type: String, required: true },
})

const info = computed(() => estadoPago(props.estado))
</script>
