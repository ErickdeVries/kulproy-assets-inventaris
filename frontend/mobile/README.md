# Asset-Gudang Mobile — fase 1

Aplikasi Expo / React Native TypeScript **terpisah** dari `../pwa`. Tidak mengganti PWA atau backend. Dibuat dari template resmi `expo-template-blank-typescript@58.0.23` dengan `create-expo-app@5.0.0`, menggunakan Expo SDK 58 stabil, React 19.3, React Native 0.88, dan npm lockfile tersendiri.

## Cakupan

- Beranda Bahasa Indonesia, safe area, scroll, dan tombol interaktif untuk melihat rencana login/dashboard.
- Login/dashboard masih placeholder rencana, **bukan** fitur autentikasi/inventaris yang berfungsi.
- Tidak ada request backend, sesi, data palsu inventaris, credential, OTA update, atau EAS project ID.
- Ikon masih aset bawaan template; ganti dengan branding sebelum distribusi resmi.

## Jalankan lokal

Gunakan Node yang didukung Expo SDK 58: `^22.13.0 || ^24.3.0 || ^26.0.0 || >=27.0.0`. Validasi awal memakai Windows, Node **26.7.0**, npm **11.19.0**.

```sh
cd frontend/mobile
npm ci
# Opsional, gunakan template publik tanpa rahasia:
cp .env.example .env
npm start
```

Scan QR dengan **Expo Go yang mendukung SDK 58** pada ponsel di jaringan sama. `npm run android` membuka emulator Android yang sudah diinstal; `npm run ios` memerlukan simulator/macOS. Android Studio/SDK dan JDK dibutuhkan untuk build native lokal, bukan untuk bundling Metro. Preview web tidak dikonfigurasi; gunakan PWA yang sudah ada jika memerlukan web.

```sh
npm test                 # uji aturan konfigurasi API
npm run typecheck        # TypeScript tanpa emit
npm run validate         # test + typecheck + expo install --check
npx expo-doctor
npm run export:android   # bundle Hermes Android di dist/android, BUKAN APK
```

## URL API publik

`.env.example` menyediakan `EXPO_PUBLIC_API_URL`, default kosong. `app.config.js` memvalidasi HTTP(S), menolak user/password, query, dan fragment, lalu meneruskannya sebagai `extra.apiBaseUrl`. `src/config/api.ts` membacanya lewat `expo-constants`. Restart Metro (`npm start -- --clear`) atau rebuild setelah mengganti konfigurasi.

Contoh untuk backend dengan prefix `/api/v1`:

- Emulator Android: `http://10.0.2.2:8000/api/v1`
- Ponsel fisik: `http://<IP-LAN-PC>:8000/api/v1`, Wi-Fi sama, backend harus dapat diakses dari LAN.
- Server publik/preview distribusi: gunakan `https://.../api/v1`.

`localhost` pada ponsel menunjuk ponsel itu sendiri. HTTP lokal mungkin dibatasi kebijakan native; HTTPS adalah pilihan aman untuk APK. Fase ini tidak menambahkan pengecualian cleartext ke Android.

**Semua `EXPO_PUBLIC_*` dan `extra` dapat dibaca pengguna aplikasi. Jangan simpan token, password, signing key, atau rahasia API.** Konfigurasi URL tidak membuktikan konektivitas backend. Tidak ada fetch pada fase ini.

## EAS: preview APK Android

`eas.json` berisi profile `preview` (`distribution: internal`, `buildType: apk`, environment `preview`) dan `production` (Android App Bundle/AAB). `android.package` awal: `com.assetgudang.mobile`; pastikan nama ini sesuai kepemilikan sebelum rilis store.

Belum ada project Expo dibuat/ditautkan oleh fondasi ini. Pilih akun/pemilik dahulu; jangan menebak project ID. Perintah berikut dijalankan pengguna setelah menyetujui pembuatan project dan penggunaan kuota EAS:

```sh
npx eas-cli@latest login
npx eas-cli@latest whoami
npx eas-cli@latest init
# init membuat/menautkan proyek dan menulis extra.eas.projectId ke konfigurasi.
# Jika CLI meminta edit konfigurasi dinamis secara manual, tambahkan projectId
# yang BENAR ke extra.eas pada app.json; app.config.js mempertahankan extra.
npx eas-cli@latest build:configure --platform android
# Pastikan eas.json tetap memakai profile preview APK yang disediakan.

# Opsional: isi URL server HTTPS publik, bukan secret, pada environment preview:
npx eas-cli@latest env:create --environment preview --name EXPO_PUBLIC_API_URL --value https://example.com/api/v1 --visibility plaintext

npm run build:preview
# Setara: npx eas-cli@latest build --platform android --profile preview
npx eas-cli@latest build:list --platform android
```

`.env` lokal diabaikan Git/upload EAS; jangan mengandalkannya untuk build cloud. Atur URL pada environment EAS `preview`; bila kosong aplikasi tetap dalam mode fondasi. Signing Android dikelola EAS melalui prompt build, jangan commit credential. APK diunduh dari URL hasil build; build cloud memerlukan akses internet dan dapat memakai kuota akun.

Tidak perlu `expo prebuild` untuk cloud build managed ini. Jangan menjalankan build lokal Windows dengan asumsi toolchain sudah tersedia. EAS local build resmi memerlukan macOS/Linux; gunakan cloud atau siapkan toolchain Android native secara terpisah.

## Struktur lanjutan

```text
App.tsx                      # provider dan entry layar
src/screens/HomeScreen.tsx   # beranda dan rencana fase selanjutnya
src/config/api.ts            # URL backend publik (belum ada API client)
app.json                    # identitas/platform
app.config.js               # validasi konfigurasi environment publik
...
```

Fase selanjutnya: tambahkan layar Login dan navigasi; implementasikan API client, penanganan error/offline, penyimpanan sesi aman, lalu dashboard berbasis API. Jangan menghubungkan placeholder ke data produksi tanpa kontrak backend dan pengujian.

## Hasil validasi awal

- `npm install`: berhasil. `npm run validate`: 3/3 test lulus, TypeScript lulus, dependensi SDK cocok.
- `npx expo-doctor`: **20/20** pemeriksaan lulus.
- `npm run export:android`: berhasil, **626 modul**, bundle Hermes sekitar **1.6 MB**.
- `CI=1 npx expo start --localhost --port 8083`: Metro berjalan; `/status` dan manifest Android di `http://localhost:8083` memberi HTTP 200. Manifest menyebut Asset-Gudang/SDK 58 dan launch asset. Pada host ini localhost bind IPv6 (`::1`); `127.0.0.1` ditolak. Server validasi dihentikan setelah pemeriksaan.
- Belum diuji visual di perangkat/emulator dan **belum menghasilkan APK**. Host tidak menyediakan `java`/`adb` di PATH maupun `ANDROID_HOME`/`ANDROID_SDK_ROOT`.
- EAS CLI tersedia dan akun sudah login, tetapi `npx eas-cli@latest project:info` gagal: `EAS project not configured. This command cannot configure it in non-interactive mode.` Akun memiliki beberapa pilihan pemilik; tidak dibuat project, signing key, atau job build tanpa pilihan pemilik/otorisasi lanjutan.
- `npm audit`: **22 temuan transitif (7 moderate, 15 high)** pada graph toolchain Expo/React Native. Tidak menjalankan `npm audit fix --force` karena saran audit mengganti Expo lintas major ke versi lama dan dapat merusak kompatibilitas SDK. Tinjau pembaruan patch resmi sebelum distribusi; kelulusan doctor bukan jaminan bebas kerentanan.
