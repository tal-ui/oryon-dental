// @vitest-environment node
import { describe, expect, it } from 'vitest'
import {
  defaultWorkingScheduleWeekdays,
  orderedScheduleWeekdays,
  startOfWeek,
  weekStartForCountry
} from '../../app/utils/week'

describe('weekStartForCountry', () => {
  it('starts on Sunday for Israel, Monday elsewhere or when unknown', () => {
    expect(weekStartForCountry('IL')).toBe(0)
    expect(weekStartForCountry('il')).toBe(0)
    expect(weekStartForCountry('ES')).toBe(1)
    expect(weekStartForCountry(null)).toBe(1)
    expect(weekStartForCountry(undefined)).toBe(1)
  })
})

describe('startOfWeek', () => {
  // 2026-10-29 is a Thursday.
  const thursday = new Date(2026, 9, 29, 15, 42, 7)

  it('returns the preceding Monday at midnight for a Monday-start week', () => {
    const start = startOfWeek(thursday, 1)
    expect([start.getFullYear(), start.getMonth(), start.getDate()]).toEqual([2026, 9, 26])
    expect(start.getDay()).toBe(1)
    expect([start.getHours(), start.getMinutes(), start.getSeconds()]).toEqual([0, 0, 0])
  })

  it('returns the preceding Sunday for a Sunday-start week', () => {
    const start = startOfWeek(thursday, 0)
    expect(start.getDate()).toBe(25)
    expect(start.getDay()).toBe(0)
  })

  it('keeps a Sunday in its own week when the week starts on Sunday, and in the previous one otherwise', () => {
    const sunday = new Date(2026, 10, 1, 9, 0) // 2026-11-01
    expect(startOfWeek(sunday, 0).getDate()).toBe(1)
    const mondayStart = startOfWeek(sunday, 1)
    expect([mondayStart.getMonth(), mondayStart.getDate()]).toEqual([9, 26])
  })

  it('does not mutate its argument', () => {
    const copy = new Date(thursday)
    startOfWeek(thursday, 0)
    expect(thursday.getTime()).toBe(copy.getTime())
  })
})

describe('schedule weekday ordering (Mon = 0 .. Sun = 6)', () => {
  it('rotates Sunday to the front for a Sunday-start week', () => {
    expect(orderedScheduleWeekdays(1)).toEqual([0, 1, 2, 3, 4, 5, 6])
    expect(orderedScheduleWeekdays(0)).toEqual([6, 0, 1, 2, 3, 4, 5])
  })

  it('defaults the working days to Mon–Fri or Sun–Thu', () => {
    expect(defaultWorkingScheduleWeekdays(1)).toEqual([0, 1, 2, 3, 4])
    expect(defaultWorkingScheduleWeekdays(0)).toEqual([6, 0, 1, 2, 3])
  })
})
