export const googleMapsConfig = {
  apiKey: import.meta.env.VITE_GOOGLE_MAPS_API_KEY?.trim() || '',
} as const

export const isGoogleMapsConfigured = Boolean(googleMapsConfig.apiKey)
