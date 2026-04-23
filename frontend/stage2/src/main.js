import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'
import { useTheme } from './composables/useTheme'

// Initialize theme
useTheme()

createApp(App).use(router).mount('#app')
