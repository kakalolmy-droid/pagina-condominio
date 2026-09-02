<template>
  <span :class="['text-xs font-semibold px-3 py-1 rounded-full', clases[variant]]">
    {{ label }}
  </span>
</template>

<script setup>
const props = defineProps({
  variant: {
    type: String,
    default: 'info', // 'success' | 'danger' | 'warning' | 'info'
  },
  label: { type: String, required: true },
})

const clases = {
  success: 'badge-success',
  danger:  'badge-danger',
  warning: 'badge-warning',
  info:    'badge-info',
}
</script>
