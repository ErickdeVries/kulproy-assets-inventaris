# Asset-Gudang PWA

Frontend Vite + React + TypeScript untuk operasional inventaris asset. UI berbahasa Indonesia dan responsif untuk desktop maupun petugas lapangan.

## Menjalankan

```bash
npm install
npm run dev
npm run build
```

Tanpa `VITE_API_URL` aplikasi berjalan dalam **mode demo** memakai data lokal. Salin `.env.example` ke `.env` untuk menghubungkan backend. Service layer di `src/api.ts` menyiapkan endpoint `login`, `assets`, `categories`, `mutasi`, dan `laporan`, dengan base URL `VITE_API_URL` atau `EXPO_PUBLIC_API_URL`.

## Konfigurasi Google Maps

Frontend telah menyiapkan `VITE_GOOGLE_MAPS_API_KEY` melalui `src/config.ts` untuk fase integrasi berikutnya. Isi variabel tersebut hanya di `.env` lokal atau konfigurasi environment deployment; jangan commit key asli. Karena variabel `VITE_*` tersedia di bundle browser, batasi key di Google Cloud berdasarkan domain aplikasi dan API yang diperlukan. Preview peta saat ini tetap lokal dan belum memuat Google Maps maupun melakukan request ke layanannya.
