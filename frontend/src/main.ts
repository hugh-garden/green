import { createApp } from 'vue'
// theme tokens must load before base so base can reference them
import './styles/theme.css'
import './styles/base.css'
import './styles/panel.css'
import './styles/globe.css'
import App from './App.vue'

createApp(App).mount('#app')
