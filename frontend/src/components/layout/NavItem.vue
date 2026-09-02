<template>
  <RouterLink
    :to="to"
    class="flex items-center gap-3.5 px-4 py-3 rounded-neu-sm text-neu-text-light font-medium text-sm
           transition-all duration-200 hover:text-neu-green hover:shadow-neu-sm hover:bg-neu-bg/60 cursor-pointer"
    active-class="shadow-neu-inset !text-neu-green !font-bold bg-neu-bg-dark border border-white/40"
  >
    <span class="text-lg opacity-90">{{ icon }}</span>
    <span>{{ label }}</span>
  </RouterLink>
</template>

<script setup>
import { RouterLink } from 'vue-router'
defineProps({
  to: String,
  icon: String,
  label: String,
})
</script>
