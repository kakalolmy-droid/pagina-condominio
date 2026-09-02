/**
 * Constantes globales de la plataforma Edificio Alcatraz.
 */

export const CONDOMINIO = {
  nombre: 'Edificio Alcatraz',
  año: 2026,
}

export const ROLES = {
  ADMIN: 'admin',
  JUNTA: 'junta',
  PROPIETARIO: 'propietario',
}

export const METODOS_PAGO = [
  { value: 'pago_movil',       label: 'Pago Móvil' },
  { value: 'transferencia_ves', label: 'Transferencia Bancaria (VES)' },
  { value: 'zelle',            label: 'Zelle (USD)' },
  { value: 'efectivo_usd',     label: 'Efectivo USD' },
]

export const MONEDAS = [
  { value: 'VES', label: 'Bolívares (VES)' },
  { value: 'USD', label: 'Dólares (USD)' },
]

export const ESTADOS_PAGO = {
  PENDIENTE: 'pendiente',
  PARCIAL:   'parcial',
  PAGADO:    'pagado',
}

export const ESTADOS_CONCILIACION = {
  EN_REVISION: 'en_revision',
  APROBADO:    'aprobado',
  RECHAZADO:   'rechazado',
}

export const ROLES_ADMIN = [ROLES.ADMIN, ROLES.JUNTA]

export const FORMATOS_COMPROBANTE = ['image/jpeg', 'image/png', 'image/webp', 'application/pdf']
export const TAMANO_MAX_COMPROBANTE_MB = 5
