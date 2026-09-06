<template>
  <Teleport to="body">
    <Transition name="modal">
      <div
        v-if="modelValue"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/30 backdrop-blur-sm"
        @click.self="$emit('update:modelValue', false)"
      >
        <div class="card-neu w-full mx-4 relative" :class="modalSizeClass">
          <!-- Header -->
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-bold text-neu-green">{{ title }}</h3>
            <button
              @click="$emit('update:modelValue', false)"
              class="text-neu-text-light hover:text-neu-danger transition-colors cursor-pointer text-lg font-bold"
            >
              ✕
            </button>
          </div>

          <!-- Content -->
          <slot />
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: { type: Boolean, required: true },
  title: { type: String, default: '' },
  size: { type: String, default: 'lg' }, // 'sm' | 'md' | 'lg' | 'xl' | '2xl' | '3xl' | '4xl'
})
defineEmits(['update:modelValue'])

const modalSizeClass = computed(() => {
  switch (props.size) {
    case 'sm': return 'max-w-sm'
    case 'md': return 'max-w-md'
    case 'xl': return 'max-w-xl'
    case '2xl': return 'max-w-2xl'
    case '3xl': return 'max-w-3xl'
    case '4xl': return 'max-w-4xl'
    case '5xl': return 'max-w-5xl'
    default: return 'max-w-lg'
  }
})
</script>

<style scoped>
.modal-enter-active, .modal-leave-active {
  transition: opacity 0.2s ease;
}
.modal-enter-from, .modal-leave-to {
  opacity: 0;
}
</style>
