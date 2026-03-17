// frontend/src/stores/message.js
import { defineStore } from 'pinia'

export const useMessageStore = defineStore('message', {
  state: () => ({
    errorMessages: null,
    successMessages: null
  }),
  
  actions: {
    updateErrorMessages(message) {
      this.errorMessages = message
      setTimeout(() => { this.errorMessages = null }, 5000)
    },
    
    updateSuccessMessages(message) {
      this.successMessages = message
      setTimeout(() => { this.successMessages = null }, 5000)
    },
    
    clearMessages() {
      this.errorMessages = null
      this.successMessages = null
    }
  }
})