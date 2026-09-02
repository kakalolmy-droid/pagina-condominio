import { ref } from 'vue'

export function useConfirm() {
  const visible = ref(false)
  const titulo = ref('')
  const mensaje = ref('')
  let resolver = null

  function confirmar(tituloMsg, mensajeMsg = '') {
    titulo.value = tituloMsg
    mensaje.value = mensajeMsg
    visible.value = true
    return new Promise((resolve) => {
      resolver = resolve
    })
  }

  function aceptar() {
    visible.value = false
    resolver?.(true)
  }

  function cancelar() {
    visible.value = false
    resolver?.(false)
  }

  return { visible, titulo, mensaje, confirmar, aceptar, cancelar }
}
