import { ref, computed } from 'vue'

export function usePaginacion(items, porPagina = 10) {
  const pagina = ref(1)

  const total = computed(() => items.value?.length || 0)
  const totalPaginas = computed(() => Math.ceil(total.value / porPagina))

  const itemsPagina = computed(() => {
    const inicio = (pagina.value - 1) * porPagina
    return (items.value || []).slice(inicio, inicio + porPagina)
  })

  function irA(n) {
    if (n >= 1 && n <= totalPaginas.value) pagina.value = n
  }

  function siguiente() { irA(pagina.value + 1) }
  function anterior()  { irA(pagina.value - 1) }

  return { pagina, total, totalPaginas, itemsPagina, irA, siguiente, anterior }
}
