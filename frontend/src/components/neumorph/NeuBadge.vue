<template>
  <span :class="['text-xs font-semibold px-3 py-1 rounded-full whitespace-nowrap inline-flex items-center justify-center min-w-[80px]', clases[variant]]">
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
