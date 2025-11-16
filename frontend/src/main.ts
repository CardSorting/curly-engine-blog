import { createApp } from 'vue'
import { createPinia } from 'pinia'

import './styles/main.css'
import App from './App.vue'
import router from './router'
import { useAuthStore } from './stores/auth'
import { useTenantStore } from './stores/tenant'

const app = createApp(App)

app.use(createPinia())
app.use(router)

// Initialize stores
const authStore = useAuthStore()
const tenantStore = useTenantStore()

authStore.initializeAuth()
tenantStore.initializeTenant()

app.mount('#app')
