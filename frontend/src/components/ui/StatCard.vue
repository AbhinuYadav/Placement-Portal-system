<!-- src/components/ui/StatCard.vue -->
<template>
  <div class="col-md-3 mb-3">
    <div class="card h-100" :class="bgClass">
      <div class="card-body py-4">
        <div class="d-flex justify-content-between align-items-center">
          <div>
            <h6 class="card-title text-white-50">{{ title }}</h6>
            <h2 class="text-white mb-0">{{ value }}</h2>
          </div>
          <i :class="[icon, 'fs-1 text-white-50']"></i>
        </div>
      </div>
      <div class="card-footer d-flex text-white" :class="footerClass">
        {{ footerText }}
        <span class="ms-auto">
          <i class="bi bi-chevron-right"></i>
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  title: String,
  value: [String, Number],
  icon: String,
  color: {
    type: String,
    default: 'primary'
  },
  footerText: {
    type: String,
    default: 'View Details'
  }
})

const bgClass = computed(() => `bg-${props.color}`)
const footerClass = computed(() => `bg-${props.color} border-${props.color}`)
</script>