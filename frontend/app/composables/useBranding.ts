/**
 * White-label branding of the app shell (login page, sidebar, document
 * title, public layout). Values come from ``runtimeConfig.public`` so a
 * deployment renames the product with ``NUXT_PUBLIC_APP_NAME`` /
 * ``NUXT_PUBLIC_APP_LOGO`` and no rebuild. Patient-facing documents and
 * emails are branded with the *clinic* name, never with these.
 */
export function useBranding() {
  const config = useRuntimeConfig().public
  const appName = computed(() => String(config.appName || 'DentalPin'))
  const appLogo = computed(() => String(config.appLogo || '/logo-icon.svg'))
  return { appName, appLogo }
}
