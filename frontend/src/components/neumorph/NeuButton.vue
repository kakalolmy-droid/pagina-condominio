<template>
  <button
    :class="[
      variant === 'primary' ? 'btn-neu-primary' : '',
      variant === 'danger'  ? 'btn-neu-danger'  : '',
      variant === 'default' ? 'btn-neu'         : '',
      'inline-flex items-center gap-2',
      disabled ? 'opacity-50 cursor-not-allowed' : '',
    ]"
    :disabled="disabled || loading"
    v-bind="$attrs"
  >
    <span v-if="loading" class="animate-spin h-4 w-4 border-2 border-current border-t-transparent rounded-full" />
    <slot />
  </button>
</template>

<script setup>
defineProps({
  variant: { type: String, default: 'default' }, // 'default' | 'primary' | 'danger'
  disabled: { type: Boolean, default: false },
  loading: { type: Boolean, default: false },
})
</script>
