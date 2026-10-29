// @vitest-environment node
import { describe, expect, it } from 'vitest'
import { isValidIsraeliTaxId, normalizeIsraeliTaxId } from '../../app/utils/israeliTaxId'

describe('isValidIsraeliTaxId', () => {
  it('accepts numbers whose Luhn-style check digit matches', () => {
    // Well-known synthetic examples that satisfy the check digit.
    expect(isValidIsraeliTaxId('000000018')).toBe(true)
    expect(isValidIsraeliTaxId('123456782')).toBe(true)
    expect(isValidIsraeliTaxId('512345679')).toBe(true)
    expect(isValidIsraeliTaxId('512345678')).toBe(false)
  })

  it('left-pads short numbers like the Population Registry does', () => {
    expect(isValidIsraeliTaxId('0000018')).toBe(true)
    // Fewer than five digits is a typo, not a short ID.
    expect(isValidIsraeliTaxId('18')).toBe(false)
  })

  it('rejects wrong check digits, letters and empty input', () => {
    expect(isValidIsraeliTaxId('000000019')).toBe(false)
    expect(isValidIsraeliTaxId('B12345678')).toBe(false)
    expect(isValidIsraeliTaxId('')).toBe(false)
    expect(isValidIsraeliTaxId(null)).toBe(false)
  })

  it('ignores separators', () => {
    expect(normalizeIsraeliTaxId(' 51-234567.9 ')).toBe('512345679')
    expect(isValidIsraeliTaxId('51-234567-9')).toBe(true)
  })
})
