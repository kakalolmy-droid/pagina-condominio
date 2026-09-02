<template>
  <div class="flex flex-col gap-1">
    <label v-if="label" :for="id" class="text-sm font-medium text-neu-text-light">
      {{ label }}
    </label>
    <input
      :id="id"
      class="input-neu"
      v-bind="$attrs"
      :value="modelValue"
      @input="$emit('update:modelValue', $event.target.value)"
    />
    <span v-if="error" class="text-xs text-neu-danger">{{ error }}</span>
  </div>
</template>

<script setup>
defineProps({
  id: String,
  label: String,
  modelValue: [String, Number],
  error: String,
})
defineEmits(['update:modelValue'])
</script>
