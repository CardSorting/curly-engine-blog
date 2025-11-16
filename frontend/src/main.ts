import { createApp } from 'vue'
import { createPinia } from 'pinia'
import './styles/main.css'
import App from './App.vue'
import router from './router'
import { registerServiceWorker } from './composables/useServiceWorker'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

// Initialize stores after Pinia and router setup
import { useAuthStore } from './stores/auth'
import { useTenantStore } from './stores/tenant'

const authStore = useAuthStore()
const tenantStore = useTenantStore()

// Register service worker
registerServiceWorker()

app.mount('#app')

// Initialize store data
authStore.initializeAuth()
tenantStore.initializeTenant()
