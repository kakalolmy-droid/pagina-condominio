<template>
  <div class="min-h-screen bg-neu-bg flex items-center justify-center p-3 sm:p-6 overflow-x-hidden">
    <div class="w-full" :class="modo === 'login' ? 'max-w-md' : 'max-w-xl'">
      <!-- Logo / Encabezado -->
      <div class="text-center mb-6 sm:mb-8">
        <div class="inline-flex items-center justify-center w-16 h-16 sm:w-20 sm:h-20 rounded-full shadow-neu mb-3 border border-white/60">
          <span class="text-3xl sm:text-4xl">🏢</span>
        </div>
        <h1 class="text-2xl sm:text-3xl font-extrabold text-neu-green tracking-tight">Edificio Alcatraz</h1>
        <p class="text-neu-text-light text-xs sm:text-sm mt-1">Portal de Administración y Autogestión de Condominio</p>
      </div>

      <!-- Tarjeta Neumórfica -->
      <div class="card-neu p-5 sm:p-8">
        <!-- Selector Neumórfico de Pestaña: Iniciar Sesión vs Registro -->
        <div class="flex rounded-neu-sm bg-neu-bg-dark p-1.5 mb-6 border border-neu-shadow-dark gap-1">
          <button
            type="button"
            @click="cambiarModo('login')"
            class="flex-1 py-2 text-xs sm:text-sm font-bold rounded-neu-sm transition-all cursor-pointer text-center"
            :class="modo === 'login' ? 'bg-neu-bg shadow-neu-sm text-neu-green' : 'text-neu-text-light hover:text-neu-text'"
          >
            🔑 Iniciar Sesión
          </button>
          <button
            type="button"
            @click="cambiarModo('registro')"
            class="flex-1 py-2 text-xs sm:text-sm font-bold rounded-neu-sm transition-all cursor-pointer text-center"
            :class="modo === 'registro' ? 'bg-neu-bg shadow-neu-sm text-neu-green' : 'text-neu-text-light hover:text-neu-text'"
          >
            📝 Registrarme
          </button>
        </div>

        <!-- ──────────────── MODO 1: INICIAR SESIÓN ──────────────── -->
        <div v-if="modo === 'login'">
          <h2 class="text-lg font-bold text-neu-text mb-4 text-center">Acceso al Sistema</h2>

          <form @submit.prevent="handleLogin" class="flex flex-col gap-4">
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
            <div v-if="errorGeneral" class="bg-red-50 border border-neu-danger text-neu-danger text-xs px-4 py-2.5 rounded-neu-sm">
              {{ errorGeneral }}
            </div>

            <NeuButton variant="primary" type="submit" :loading="cargando" class="w-full justify-center mt-2">
              Entrar al Portal
            </NeuButton>

            <div class="text-center mt-2">
              <button
                type="button"
                @click="cambiarModo('registro')"
                class="text-xs text-neu-green hover:underline font-semibold cursor-pointer"
              >
                ¿Eres nuevo propietario o residente? Regístrate aquí
              </button>
            </div>
          </form>
        </div>

        <!-- ──────────────── MODO 2: REGISTRO DE PROPIETARIOS ──────────────── -->
        <div v-else>
          <div class="text-center mb-4">
            <h2 class="text-lg font-bold text-neu-green">Registro de Copropietario / Residente</h2>
            <p class="text-xs text-neu-text-light mt-0.5">
              Registra tu apartamento y crea tu acceso para consultar y reportar tus pagos
            </p>
          </div>

          <form @submit.prevent="handleRegistro" class="flex flex-col gap-4">
            <!-- Fila 1: Nombre y Apellido -->
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <NeuInput
                id="reg_nombre"
                label="Nombre"
                v-model="formRegistro.nombre"
                placeholder="Ej. Carlos"
                required
              />
              <NeuInput
                id="reg_apellido"
                label="Apellido"
                v-model="formRegistro.apellido"
                placeholder="Ej. Pérez"
                required
              />
            </div>

            <!-- Fila 2: Cédula y Teléfono WhatsApp con ejemplo claro solicitado -->
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <NeuInput
                id="reg_cedula"
                label="Cédula de Identidad"
                v-model="formRegistro.cedula"
                placeholder="Ej. V-12345678"
                required
              />

              <div>
                <label class="block text-xs font-semibold text-neu-text mb-1">
                  WhatsApp / Teléfono <span class="text-neu-danger">*</span>
                </label>
                <input
                  id="reg_telefono"
                  v-model="formRegistro.telefono_whatsapp"
                  type="text"
                  placeholder="+584120000000"
                  class="input-neu text-xs py-2 w-full"
                  required
                />
                <span class="text-[10px] text-neu-green font-semibold mt-1 block">
                  💡 Ejemplo: +584120000000 (Incluye el prefijo +58)
                </span>
              </div>
            </div>

            <!-- Fila 3: Datos del Apartamento -->
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <NeuInput
                id="reg_apto"
                label="N° Apartamento"
                v-model="formRegistro.numero_apto"
                placeholder="Ej. 2-5, 1-A"
                required
              />
              <NeuInput
                id="reg_piso"
                label="Piso"
                v-model="formRegistro.piso"
                placeholder="Ej. 2"
              />
              <NeuInput
                id="reg_torre"
                label="Torre"
                v-model="formRegistro.torre"
                placeholder="Ej. A o Principal"
              />
            </div>

            <!-- Fila 4: Correo y Contraseña -->
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <NeuInput
                id="reg_email"
                label="Correo electrónico"
                v-model="formRegistro.email"
                type="email"
                placeholder="propietario@correo.com"
                required
              />

              <NeuInput
                id="reg_password"
                label="Contraseña"
                v-model="formRegistro.password"
                type="password"
                placeholder="Mínimo 6 caracteres"
                required
              />
            </div>

            <!-- Banner Informativo: Entran con 0 deudas -->
            <div class="p-3.5 bg-neu-bg-dark rounded-neu-sm border border-emerald-600/30 flex items-start gap-2.5 text-xs text-neu-text">
              <span class="text-lg leading-none">📌</span>
              <div class="leading-relaxed">
                <span class="font-bold text-neu-green">Información de tu Estado de Cuenta:</span>
                <p class="text-neu-text-light text-[11px] mt-0.5">
                  Al registrarte, tu cuenta se creará inicialmente con <strong>$0.00 de deuda</strong>. La administración revisará tus datos y registrará la cuota mensual y meses adeudados correspondientes en el sistema.
                </p>
              </div>
            </div>

            <!-- Error general -->
            <div v-if="errorGeneral" class="bg-red-50 border border-neu-danger text-neu-danger text-xs px-4 py-2.5 rounded-neu-sm">
              {{ errorGeneral }}
            </div>

            <NeuButton variant="primary" type="submit" :loading="cargando" class="w-full justify-center mt-1">
              Completar Registro y Entrar
            </NeuButton>

            <div class="text-center mt-1">
              <button
                type="button"
                @click="cambiarModo('login')"
                class="text-xs text-neu-green hover:underline font-semibold cursor-pointer"
              >
                ¿Ya estás registrado? Inicia sesión aquí
              </button>
            </div>
          </form>
        </div>

        <!-- Indicador de tasa BCV Oficial -->
        <div v-if="tasaStore.tasaActual" class="mt-6 pt-4 border-t border-neu-shadow-dark text-center">
          <p class="text-xs text-neu-text-light">
            Tasa BCV oficial del día:
            <span class="font-semibold text-neu-green">Bs. {{ parseFloat(tasaStore.tasaActual).toLocaleString('es-VE', { minimumFractionDigits: 2 }) }} / $1</span>
          </p>
        </div>
      </div>

      <p class="text-center text-xs text-neu-text-light mt-6">
        © {{ new Date().getFullYear() }} Edificio Alcatraz — Sistema de Gestión de Condominio
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

const modo = ref('login') // 'login' | 'registro'
const cargando = ref(false)
const errorGeneral = ref('')
const errores = ref({ email: '', password: '' })

// Campos de Login
const email = ref('')
const password = ref('')

// Campos de Registro
const formRegistro = ref({
  nombre: '',
  apellido: '',
  cedula: '',
  telefono_whatsapp: '',
  numero_apto: '',
  piso: '1',
  torre: 'Principal',
  email: '',
  password: '',
})

onMounted(() => {
  tasaStore.cargarTasa()
})

function cambiarModo(nuevoModo) {
  modo.value = nuevoModo
  errorGeneral.value = ''
  errores.value = { email: '', password: '' }
}

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
    const msg = error.response?.data?.detail || error.message || 'Error al iniciar sesión. Verifique sus credenciales.'
    errorGeneral.value = msg
  } finally {
    cargando.value = false
  }
}

async function handleRegistro() {
  errorGeneral.value = ''

  if (!formRegistro.value.nombre || !formRegistro.value.apellido) {
    errorGeneral.value = 'Por favor ingresa tu nombre y apellido completos.'
    return
  }
  if (!formRegistro.value.cedula) {
    errorGeneral.value = 'Por favor ingresa tu cédula de identidad.'
    return
  }
  if (!formRegistro.value.telefono_whatsapp) {
    errorGeneral.value = 'Por favor ingresa tu número de teléfono WhatsApp (+584120000000).'
    return
  }
  if (!formRegistro.value.numero_apto) {
    errorGeneral.value = 'Por favor indica el número de tu apartamento.'
    return
  }
  if (!formRegistro.value.email || !formRegistro.value.password) {
    errorGeneral.value = 'Por favor completa tu correo electrónico y contraseña.'
    return
  }
  if (formRegistro.value.password.length < 6) {
    errorGeneral.value = 'La contraseña debe tener al menos 6 caracteres.'
    return
  }

  cargando.value = true
  try {
    const data = await authStore.registro(formRegistro.value)
    toast.success(`¡Registro exitoso! Bienvenido/a, ${data.nombre}`)
    await router.push('/mi-cuenta/inicio')
  } catch (error) {
    console.error('Error capturado en registro:', error)
    const msg = error.response?.data?.detail || error.message || 'Error al completar el registro.'
    errorGeneral.value = msg
  } finally {
    cargando.value = false
  }
}
</script>
