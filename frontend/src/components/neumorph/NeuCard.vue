<template>
  <div :class="['card-neu', small ? 'card-neu-sm' : '', className]">
    <slot />
  </div>
</template>

<script setup>
defineProps({
  small: { type: Boolean, default: false },
  className: { type: String, default: '' },
})
</script>
