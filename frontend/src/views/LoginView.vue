<template>
  <div class="min-h-screen bg-neu-bg flex items-center justify-center p-4">
    <div class="w-full max-w-md">
      <!-- Logo / Encabezado -->
      <div class="text-center mb-10">
        <div class="inline-flex items-center justify-center w-20 h-20 rounded-full shadow-neu mb-4">
          <span class="text-4xl">🏢</span>
        </div>
        <h1 class="text-3xl font-bold text-neu-green">Edificio Alcatraz</h1>
        <p class="text-neu-text-light mt-1">Portal de Administración de Condominio</p>
      </div>

      <!-- Tarjeta de login -->
      <div class="card-neu">
        <h2 class="text-xl font-semibold text-neu-text mb-6 text-center">Iniciar Sesión</h2>

        <form @submit.prevent="handleLogin" class="flex flex-col gap-5">
          <NeuInput
            id="email"
            label="Correo electrónico"
            v-model="email"
            type="email"
            placeholder="ejemplo@correo.com"
            :error="errores.email"
            required
          />

          <NeuInput
            id="password"
            label="Contraseña"
            v-model="password"
            type="password"
            placeholder="••••••••"
            :error="errores.password"
            required
          />

          <!-- Error general -->
          <div v-if="errorGeneral" class="bg-red-50 border border-neu-danger text-neu-danger text-sm px-4 py-2 rounded-neu-sm">
            {{ errorGeneral }}
          </div>

          <NeuButton variant="primary" type="submit" :loading="cargando" class="w-full justify-center mt-2">
            Entrar al Portal
          </NeuButton>
        </form>

        <!-- Indicador de tasa BCV -->
        <div v-if="tasaStore.tasaActual" class="mt-6 pt-4 border-t border-neu-shadow-dark text-center">
          <p class="text-xs text-neu-text-light">
            Tasa BCV oficial del día:
            <span class="font-semibold text-neu-green">Bs. {{ parseFloat(tasaStore.tasaActual).toLocaleString('es-VE', { minimumFractionDigits: 2 }) }} / $1</span>
          </p>
        </div>
      </div>

      <p class="text-center text-xs text-neu-text-light mt-6">
        © 2026 Edificio Alcatraz — Sistema de Gestión de Condominio
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'vue-toastification'
import { useAuthStore } from '@/stores/auth'
import { useTasaStore } from '@/stores/tasa'
import NeuInput from '@/components/neumorph/NeuInput.vue'
import NeuButton from '@/components/neumorph/NeuButton.vue'

const router = useRouter()
const toast = useToast()
const authStore = useAuthStore()
const tasaStore = useTasaStore()

const email = ref('admin@alcatraz.com')
const password = ref('admin123')
const cargando = ref(false)
const errorGeneral = ref('')
const errores = ref({ email: '', password: '' })

onMounted(() => {
  tasaStore.cargarTasa()
})

async function handleLogin() {
  errores.value = { email: '', password: '' }
  errorGeneral.value = ''

  if (!email.value) { errores.value.email = 'El email es requerido'; return }
  if (!password.value) { errores.value.password = 'La contraseña es requerida'; return }

  cargando.value = true
  try {
    const data = await authStore.login(email.value, password.value)
    toast.success(`¡Bienvenido/a, ${data.nombre}!`)

    if (data.rol === 'propietario') {
      await router.push('/mi-cuenta/inicio')
    } else {
      await router.push('/admin/dashboard')
    }
  } catch (error) {
    console.error('Error capturado en login:', error)
    const msg = error.response?.data?.detail || error.message || 'Error al iniciar sesión. Intente de nuevo.'
    errorGeneral.value = msg
  } finally {
    cargando.value = false
  }
}
</script>
