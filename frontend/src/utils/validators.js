/**
 * Validadores de formularios para la plataforma.
 */

export function validarEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
    ? null
    : 'Ingrese un email válido'
}

export function validarCedula(cedula) {
  return cedula && cedula.length >= 6
    ? null
    : 'Cédula inválida (mínimo 6 caracteres)'
}

export function validarTelefono(tel) {
  return /^[0-9\+\-\s]{10,15}$/.test(tel)
    ? null
    : 'Teléfono inválido (10-15 dígitos)'
}

export function validarAlicuota(valor) {
  const num = parseFloat(valor)
  if (isNaN(num) || num <= 0 || num > 1)
    return 'La alícuota debe ser entre 0.001 y 1 (ej: 0.025 para 2.5%)'
  return null
}

export function validarMonto(valor) {
  const num = parseFloat(valor)
  return !isNaN(num) && num > 0 ? null : 'Ingrese un monto válido mayor a 0'
}

export function validarPeriodo(periodo) {
  return /^\d{4}-\d{2}$/.test(periodo)
    ? null
    : 'Formato inválido. Use YYYY-MM (ej: 2026-09)'
}

export function validar(valor, validadores) {
  for (const fn of validadores) {
    const error = fn(valor)
    if (error) return error
  }
  return null
}
