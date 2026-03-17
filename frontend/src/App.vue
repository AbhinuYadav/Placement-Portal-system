<!-- frontend/src/App.vue -->
<script setup>
import { RouterView } from 'vue-router'
import { useMessageStore } from '@/stores/message'
import { computed } from 'vue'

const message_store = useMessageStore()

const ErrorMessages = computed(() => {
  return message_store.errorMessages
})

const SuccessMessages = computed(() => {
  return message_store.successMessages
})
</script>

<template>
  <!-- Global messages -->
  <div v-if="ErrorMessages" class="position-fixed top-0 start-50 translate-middle-x mt-3 z-3" style="z-index: 9999;">
    <div class="alert alert-danger alert-dismissible fade show shadow-lg">
      {{ ErrorMessages }}
      <button type="button" class="btn-close" @click="message_store.clearMessages()"></button>
    </div>
  </div>
  
  <div v-if="SuccessMessages" class="position-fixed top-0 start-50 translate-middle-x mt-3 z-3" style="z-index: 9999;">
    <div class="alert alert-success alert-dismissible fade show shadow-lg">
      {{ SuccessMessages }}
      <button type="button" class="btn-close" @click="message_store.clearMessages()"></button>
    </div>
  </div>

  <!-- Main content -->
  <RouterView />
</template>

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body, #app {
  width: 100%;
  min-height: 100vh;
  font-family: 'Inter', sans-serif;
}
</style>