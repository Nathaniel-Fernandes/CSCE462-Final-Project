import { createApp } from 'vue'
import App from './App.vue'
import { createClient } from '@supabase/supabase-js'

export const supabase = createClient(import.meta.env.VITE_API_SUPABASE_URL, import.meta.env.VITE_API_SUPABASE_KEY)

import './assets/main.css'


createApp(App).mount('#app')
