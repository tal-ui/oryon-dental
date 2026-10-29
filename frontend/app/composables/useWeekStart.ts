import { startOfWeek, weekStartForCountry, type WeekStartDay } from '~/utils/week'

/**
 * First day of the week for the current clinic — Sunday for countries with
 * a Sunday–Thursday working week (Israel), Monday otherwise. Lives in the
 * host so the agenda and schedules layers share one answer without a
 * cross-module import. Derived from ``useClinicCountry`` (server-side
 * country), so it is stable across devices and UI languages.
 */
export function useWeekStart() {
  const country = useClinicCountry()
  const weekStartsOn = computed<WeekStartDay>(() => weekStartForCountry(country.value))
  return {
    weekStartsOn,
    /** Midnight of the first day of ``date``'s week for this clinic. */
    startOfWeek: (date: Date) => startOfWeek(date, weekStartsOn.value)
  }
}
