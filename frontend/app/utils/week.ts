/**
 * Working-week helpers.
 *
 * The agenda's week view and the clinic-hours grid used to hardcode
 * Monday as the first day. That hides Sunday — a full working day in
 * Israel (Sunday–Thursday week) — at the far end of the grid. The first
 * day of the week is derived from the clinic's country, never from the
 * browser locale: a Hebrew UI on a Spanish clinic still starts on Monday.
 *
 * ``WeekStartDay`` follows JavaScript's ``Date#getDay`` (0 = Sunday,
 * 1 = Monday). The schedules API keeps its own ``weekday`` numbering
 * (Mon = 0 .. Sun = 6); ``orderedScheduleWeekdays`` bridges the two.
 */

export type WeekStartDay = 0 | 1

/** ISO-3166 alpha-2 codes whose working week starts on Sunday. */
export const SUNDAY_START_COUNTRIES: ReadonlySet<string> = new Set(['IL'])

export function weekStartForCountry(country: string | null | undefined): WeekStartDay {
  return country && SUNDAY_START_COUNTRIES.has(country.toUpperCase()) ? 0 : 1
}

/**
 * Midnight of the first day of ``date``'s week. Pure: returns a new
 * ``Date``, never mutates the argument.
 */
export function startOfWeek(date: Date, weekStartsOn: WeekStartDay = 1): Date {
  const d = new Date(date)
  const diff = (d.getDay() - weekStartsOn + 7) % 7
  d.setDate(d.getDate() - diff)
  d.setHours(0, 0, 0, 0)
  return d
}

/**
 * Schedules-API weekdays (Mon = 0 .. Sun = 6) in display order for the
 * given week start: ``[0..6]`` for Monday, ``[6, 0, 1, 2, 3, 4, 5]`` for
 * Sunday.
 */
export function orderedScheduleWeekdays(weekStartsOn: WeekStartDay = 1): number[] {
  const days = [0, 1, 2, 3, 4, 5, 6]
  return weekStartsOn === 0 ? [6, ...days.slice(0, 6)] : days
}

/**
 * The five default working days in schedules-API numbering: Mon–Fri for a
 * Monday-start week, Sun–Thu for a Sunday-start one. Used by the quick
 * hours presets; Friday in a Sunday-start market is left to the clinic.
 */
export function defaultWorkingScheduleWeekdays(weekStartsOn: WeekStartDay = 1): number[] {
  return orderedScheduleWeekdays(weekStartsOn).slice(0, 5)
}
