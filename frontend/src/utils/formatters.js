/**
 * Formateadores de datos para la UI de Edificio Alcatraz.
 * Funciones puras — sin dependencias externas.
 */

/**
 * Formatea un número como moneda USD.
 * @param {number|string} monto
 * @returns {string} '$1,234.56'
 */
export function formatUSD(monto) {
  const num = parseFloat(monto) || 0
  return new Intl.NumberFormat('es-VE', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
  }).format(num)
}

/**
 * Formatea un número como moneda VES (Bolívares).
 * @param {number|string} monto
 * @returns {string} 'Bs. 1.234.567,89'
 */
export function formatVES(monto) {
  const num = parseFloat(monto) || 0
  return `Bs. ${new Intl.NumberFormat('es-VE', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(num)}`
}

/**
 * Formatea la tasa BCV.
 * @param {number|string} tasa
 * @returns {string} 'Bs. 36.50 / $1'
 */
export function formatTasa(tasa) {
  const num = parseFloat(tasa) || 0
  return `Bs. ${num.toFixed(4)} / $1`
}

/**
 * Formatea una fecha ISO a formato legible en español.
 * @param {string} fecha - ISO date string
 * @returns {string} '1 sep. 2026'
 */
export function formatFecha(fecha) {
  if (!fecha) return '—'
  if (typeof fecha === 'string') {
    const soloFecha = fecha.split('T')[0]
    const partes = soloFecha.split('-')
    if (partes.length === 3) {
      const year = parseInt(partes[0], 10)
      const month = parseInt(partes[1], 10) - 1
      const day = parseInt(partes[2], 10)
      return new Date(year, month, day).toLocaleDateString('es-VE', {
        day: 'numeric',
        month: 'short',
        year: 'numeric',
      })
    }
  }
  return new Date(fecha).toLocaleDateString('es-VE', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  })
}

/**
 * Formatea un período '2026-09' como 'Septiembre 2026'.
 * @param {string} periodo - 'YYYY-MM'
 * @returns {string}
 */
export function formatPeriodo(periodo) {
  if (!periodo) return '—'
  const [year, month] = periodo.split('-')
  const fecha = new Date(parseInt(year), parseInt(month) - 1, 1)
  return fecha.toLocaleDateString('es-VE', { month: 'long', year: 'numeric' })
}

/**
 * Genera el período actual en formato 'YYYY-MM'.
 * @returns {string}
 */
export function periodoActual() {
  const ahora = new Date()
  return `${ahora.getFullYear()}-${String(ahora.getMonth() + 1).padStart(2, '0')}`
}

/**
 * Convierte USD a VES usando la tasa BCV.
 * @param {number} montoUSD
 * @param {number} tasa
 * @returns {number}
 */
export function usdAves(montoUSD, tasa) {
  return parseFloat(((parseFloat(montoUSD) || 0) * (parseFloat(tasa) || 0)).toFixed(2))
}

/**
 * Mapea el estado de conciliación a etiqueta y variante del badge.
 */
export function estadoConciliacion(estado) {
  const mapa = {
    en_revision: { label: 'En Revisión', variant: 'warning' },
    aprobado:    { label: 'Aprobado',    variant: 'success' },
    rechazado:   { label: 'Rechazado',   variant: 'danger'  },
  }
  return mapa[estado] || { label: estado, variant: 'info' }
}

/**
 * Mapea el estado de pago del recibo a etiqueta y variante.
 */
export function estadoPago(estado) {
  if (!estado) return { label: '—', variant: 'info' }
  const normalizado = String(estado).toLowerCase().trim()
  const mapa = {
    pendiente: { label: 'Pendiente', variant: 'danger' },
    parcial:   { label: 'Parcial',   variant: 'warning' },
    pagado:    { label: 'Pagado',    variant: 'success' },
    moroso:    { label: 'Moroso',    variant: 'danger' },
    solvente:  { label: 'Solvente',  variant: 'success' },
  }
  return mapa[normalizado] || { label: estado, variant: 'info' }
}
