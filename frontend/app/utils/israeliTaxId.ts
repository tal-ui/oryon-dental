/**
 * Israeli dealer-number check digit (ת.ז. for individuals, ח.פ. for
 * companies — both 9 digits with the same Luhn-style check digit).
 * Advisory only, like the Spanish NIF: the wizard shows a warning, the
 * server (`country_presets.IL`) enforces just the 9-digit format.
 *
 * Algorithm: weight the digits 1,2,1,2,… left to right, sum the digits of
 * each product (a two-digit product contributes its digit sum), and the
 * total must be a multiple of 10. Five to nine digits are accepted and
 * left-padded with zeros, as the Population Registry does; fewer is a typo.
 */
export function normalizeIsraeliTaxId(value: string): string {
  return value.trim().replace(/[\s\-.]/g, '')
}

export function isValidIsraeliTaxId(value: string | null | undefined): boolean {
  if (!value) return false
  const digits = normalizeIsraeliTaxId(value)
  if (!/^\d{5,9}$/.test(digits)) return false
  const padded = digits.padStart(9, '0')
  let total = 0
  for (let i = 0; i < 9; i++) {
    const product = Number(padded[i]) * (i % 2 === 0 ? 1 : 2)
    total += product > 9 ? product - 9 : product
  }
  return total % 10 === 0
}
