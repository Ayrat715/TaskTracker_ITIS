import { defineStore } from 'pinia'

export const useErrorStore = defineStore('error', {
  state: () => ({
    allowedErrorPages: []
  }),
  actions: {
    allowErrorPage(name) {
      if (!this.allowedErrorPages.includes(name)) {
        this.allowedErrorPages.push(name)
      }
    },
    isErrorPageAllowed(name) {
      return this.allowedErrorPages.includes(name)
    },
    reset() {
      this.allowedErrorPages = []
    }
  }
})