import Constants from 'expo-constants';

// Hanya URL publik; token sesi harus ditangani terpisah pada fase autentikasi.
const configuredUrl: unknown = Constants.expoConfig?.extra?.apiBaseUrl;
export const apiBaseUrl = typeof configuredUrl === 'string' ? configuredUrl : null;
