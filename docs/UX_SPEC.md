# UX SPEC — Asset-Gudang

> **Versi:** 1.0 · **Status:** acuan Fase 2–4 · **Surface utama:** *Operate + Monitor* — petugas bergerak cepat di lapangan, admin memantau dan mengambil keputusan dari desktop.

## 1. Sasaran pengalaman

Asset-Gudang membantu tim mencatat barang bekas dengan cepat, menjaga posisi asset tetap dapat diaudit, dan menghasilkan rekap yang siap dicetak/dibagikan. Semua UI berbahasa Indonesia, memakai istilah yang konsisten: **asset**, **lokasi**, **kondisi**, **mutasi**, dan **laporan**.

### Persona

| Persona | Konteks | Tujuan | Hambatan | Kebutuhan UX |
|---|---|---|---|---|
| **Raka — Petugas gudang** | Android, berdiri/berjalan, cahaya berubah, koneksi bisa tidak stabil | Input asset baru, cek stok, pindahkan barang tanpa salah lokasi | Tangan sibuk, waktu singkat, layar kecil | Tombol ≥44 px, form satu kolom, default cerdas, simpan draf, konfirmasi asal→tujuan yang tegas |
| **Sari — Admin inventaris** | Laptop/PWA, sesi kerja panjang | Memantau KPI, menyaring asset, memvalidasi data, cetak/share laporan | Data banyak, perlu jejak audit dan filter yang jelas | Tabel padat namun terbaca, filter tersimpan, bulk insight, laporan A4 konsisten |

### Prinsip
1. **Cepat sebelum lengkap:** field wajib paling sedikit; detail tambahan bisa diisi setelah simpan.
2. **Satu kebenaran lokasi:** setiap mutasi menyimpan `dari`, `ke`, waktu, pelaku, jumlah, dan catatan.
3. **Status terlihat dari jauh:** angka KPI dan badge memiliki teks, bukan warna saja.
4. **Aman saat bergerak:** destructive action selalu konfirmasi; autosave draf tidak mengubah stok.
5. **Progressive disclosure:** tampilkan inti dahulu, riwayat dan metadata di bawah.

## 2. Informasi arsitektur & navigasi

### Mobile (petugas)
- **Top bar:** logo `AG`, judul layar, status sinkronisasi, avatar.
- **Bottom tab:** Beranda · Asset · **Tambah (FAB)** · Mutasi · Laporan.
- Back selalu tersedia pada layar turunan; keyboard tidak menutup field aktif.

### Desktop/PWA (admin)
- Sidebar: Ringkasan, Asset, Mutasi, Laporan, Kategori, Pengguna.
- Header: pencarian global, status koneksi, akun aktif.
- Konten memakai grid 12 kolom; tabel adalah default untuk admin.

## 3. User flow

### Login
`Buka aplikasi → masukkan email/username + kata sandi → [Masuk] → validasi role → Beranda sesuai role`.
- Error inline di bawah field; jangan menghapus username.
- Loading: tombol menjadi “Memeriksa…” dan disabled.
- Lupa kata sandi (admin): tautan sekunder, tidak mengambil fokus utama.

### Input asset baru
`Tambah → foto opsional → nama/kode → kategori → kondisi → jumlah → lokasi → keterangan → Simpan asset → toast “Asset tersimpan” → Detail asset`.
- Kode otomatis sebagai default, dapat diubah admin.
- `Simpan draf` tersedia bila keluar di tengah jalan.
- Jumlah integer > 0; lokasi wajib; foto dikompresi di perangkat.

### Pendataan lokasi / stok eksisting
`Asset → [Tambah] → pilih “Asset sudah ada” → isi asset, jumlah terhitung, status lokasi → simpan → Detail`.
- “Dalam gudang” memilih zona/rak; “Luar gudang” meminta lokasi tujuan/penanggung jawab.
- Duplicate code dicegah dengan validasi server dan saran membuka asset yang sudah ada.

### Mutasi
`Detail asset → Pindahkan → lihat kartu DARI → pilih KE → tipe otomatis → jumlah → catatan → Tinjau perubahan → Konfirmasi mutasi → riwayat bertambah`.
- Tipe: Masuk gudang, Keluar gudang, Pindah rak/zona.
- Asal tidak boleh sama dengan tujuan; jumlah tidak boleh melebihi stok lokasi asal.
- Setelah berhasil, badge lokasi di detail langsung diperbarui.

### Laporan
`Laporan → rentang tanggal + filter → Terapkan → ringkasan + tabel → Preview cetak → Cetak / Bagikan WhatsApp`.
- Preview mengikuti A4 portrait; tombol aksi tetap jelas.
- Bagikan memakai ringkasan teks dan tautan/file PDF yang dibuat platform.

## 4. Wireframe ASCII

```text
LOGIN                         DASHBOARD MOBILE
┌──────────────────────┐      ┌──────────────────────┐
│ AG  ASSET-GUDANG     │      │ Selamat pagi, Raka   │
│ Inventaris lebih     │      │ Gudang Utama  •  ●  │
│ tertib, setiap hari  │      ├──────────────────────┤
│ [ Username          ] │      │ TOTAL ASSET         │
│ [ Kata sandi      ◉ ] │      │ 1.248               │
│ [      MASUK       ] │      │ +12 minggu ini      │
│ □ Ingat perangkat    │      ├──────────┬───────────┤
│ Lupa kata sandi?     │      │ DALAM    │ LUAR      │
└──────────────────────┘      │ 1.084    │ 164       │
                              ├──────────────────────┤
                              │ Mutasi terbaru       │
                              │ #AST-0241  Rak B-03  │
                              │ Hari ini, 09.42  ›   │
                              ├──────────────────────┤
                              │ Beranda Asset ＋ Mutasi│
                              └──────────────────────┘

DAFTAR ASSET                    FORM TAMBAH ASSET
┌──────────────────────┐      ┌──────────────────────┐
│ ‹ Asset        🔎    │      │ ‹ Tambah asset       │
│ [Cari kode/nama…]    │      │ Foto asset  [+ Foto] │
│ [Kategori⌄][Kondisi]│      │ Nama asset *         │
│ 1.248 asset  Filter  │      │ [Kursi lipat       ] │
│ ┌──────────────────┐ │      │ Kategori * [Pilih⌄] │
│ │ Kursi lipat       │ │      │ Kondisi  [Baik  ⌄]  │
│ │ AST-0241 • 24 pcs │ │      │ Jumlah   [24      ] │
│ │ Dalam gudang      │ │      │ Lokasi   [Gudang A] │
│ │ Baik          ›   │ │      │ [ Simpan asset   ] │
│ └──────────────────┘ │      │ Disimpan otomatis   │
│ Beranda Asset ＋ ...  │      └──────────────────────┘
└──────────────────────┘

DETAIL + MUTASI                  LAPORAN / PREVIEW CETAK
┌──────────────────────┐      ┌──────────────────────┐
│ ‹ Detail asset  ⋮    │      │ Laporan inventaris   │
│ Kursi lipat          │      │ [01 Okt]—[19 Okt]    │
│ AST-0241             │      │ [ Terapkan filter ]  │
│ 24 pcs  •  Baik      │      │ Total 1.248 | Baik  │
│ ● Dalam gudang       │      │ [ PREVIEW CETAK ]    │
│ [ Pindahkan ] [Edit] │      │ [ Bagikan WhatsApp ] │
│ ──────────────────── │      │ ───── PREVIEW A4 ─── │
│ Riwayat mutasi       │      │ ASSET-GUDANG         │
│ 19 Okt 09.42  Masuk  │      │ Rekap 01–19 Okt      │
│ Luar → Gudang A      │      │ Total asset 1.248    │
│ 12 Okt 14.10  Pindah │      │ tabel rekap kategori │
│ Rak A → Rak B        │      └──────────────────────┘
└──────────────────────┘
```

## 5. UI kit — industrial amber

### Warna (hex)
| Token | Hex | Pemakaian |
|---|---|---|
| `ink-950` | `#171A1C` | teks utama / sidebar gelap |
| `ink-800` | `#293034` | surface gelap, header |
| `canvas` | `#F5F3EE` | latar utama hangat |
| `surface` | `#FFFFFF` | kartu, form, modal |
| `line` | `#D9D5CC` | border, divider |
| `muted` | `#6B7475` | helper text, metadata |
| `amber-500` | `#F2A900` | CTA, fokus, accent industrial |
| `amber-700` | `#B87500` | teks amber pada latar terang |
| `amber-050` | `#FFF5D6` | highlight, luar gudang |
| `green-700` | `#177245` | dalam gudang / baik |
| `green-050` | `#E5F4EA` | badge success |
| `red-700` | `#B42318` | rusak berat, error |
| `red-050` | `#FDE8E7` | badge danger |
| `blue-700` | `#175CD3` | info/sinkronisasi |

Kontras teks normal minimum 4.5:1. Jangan gunakan amber-500 sebagai teks kecil; gunakan amber-700. Warna badge selalu disertai label dan/atau ikon.

### Tipografi
- **Keluarga:** `Arial, Helvetica, sans-serif` (file:// aman, tidak bergantung network).
- Display KPI: 32 px / 700 / line-height 1.05; heading layar: 24 px / 700; section: 16 px / 700; body: 14–16 px / 400–500; caption: 12 px / 500; angka tabel: tabular-nums.
- Letter spacing label uppercase `0.08em`; hindari paragraf lebih dari 70 karakter per baris.

### Spacing, shape, elevation
- Skala 4 px: `4, 8, 12, 16, 20, 24, 32, 40`.
- Radius: 8 px kontrol, 12 px kartu, 16 px sheet; desktop maksimal 12 px.
- Border 1 px `line`; shadow hanya `0 8px 24px rgba(23,26,28,.08)` untuk sheet/modal.
- Hit target minimum 44×44 px; gutter mobile 20 px, desktop 32 px.

## 6. Komponen & states aksesibel

- **Button:** primary amber, secondary outline, ghost, danger. States default/hover/focus-visible (outline 3 px `#F2A900`)/pressed/disabled/loading. Label aksi + verb (“Simpan asset”), bukan “OK”.
- **Badge:** Dalam gudang (hijau), Luar gudang (amber), Baik (hijau), Rusak ringan (amber), Rusak berat (merah). Bentuk pill, teks selalu hadir.
- **Text input/select:** label selalu terlihat, helper/error di bawah, `aria-invalid`, placeholder bukan label. Error fokus pertama secara otomatis.
- **Card:** header ringkas, konten, aksi; jangan menjadikan seluruh kartu tombol tanpa affordance.
- **Table:** header sticky desktop, sort dengan `aria-sort`, row focus, empty state, skeleton loading, pagination dan jumlah hasil.
- **Filter chip:** removable dengan label yang menyebut nilai; “Reset filter” terlihat saat aktif.
- **Toast:** region `role=status`, tidak menghilang sebelum 4 detik untuk pesan penting; selalu sediakan cara membatalkan jika relevan.
- **Modal konfirmasi mutasi:** focus trap, judul menyebut dampak (“Pindahkan 12 pcs?”), tombol batal sekunder, escape menutup.
- **FAB:** label terlihat di layar tambah, tooltip/accessible label pada ikon, tidak menutup tab bar.
- **Loading:** skeleton mempertahankan layout; tombol loading tidak dapat diklik ulang.
- **Empty/error/offline:** pesan sebab + langkah pemulihan (“Coba lagi”, “Buat asset pertama”); offline menampilkan banner dan status draf.

## 7. Layout cetak A4

- Ukuran target `210 × 297 mm`, portrait; margin 14 mm atas/bawah, 16 mm kiri/kanan.
- Header: logo AG, judul “Laporan Inventaris Asset”, rentang tanggal, lokasi, waktu cetak, filter aktif.
- Ringkasan 3 kolom: total asset, dalam gudang, luar gudang.
- Tabel: No, Kode, Nama asset, Kategori, Kondisi, Lokasi, Jumlah; header amber pucat, baris zebra halus.
- Footer: “Dokumen dihasilkan Asset-Gudang” + nomor halaman; `@page { size: A4; margin: 14mm 16mm; }`, `thead { display: table-header-group; }`.
- Teks cetak minimal 10 pt, label/angka utama 12 pt+. Sembunyikan navigasi, tombol, dan filter saat print.

## 8. Mapping React Native / Expo / PWA

| UX | React Native / Expo | PWA Web |
|---|---|---|
| Layout | `SafeAreaView`, `View`, `ScrollView`, `useWindowDimensions` | CSS grid/container, breakpoint 768 px |
| Navigasi | Expo Router tabs + stack; FAB di tab Asset | React Navigation Web / route setara, sidebar desktop |
| Form | `TextInput`, `Pressable`, `Picker`; keyboard-aware scroll | `<input>`, `<select>`, label native, validation constraint |
| Data | TanStack Query; cache + mutation invalidation; AsyncStorage draf | Query cache; IndexedDB untuk draf ringan |
| Foto | `expo-image-picker`, kompresi sebelum upload | input file/capture; preview object URL |
| Ikon | ikon inline/`@expo/vector-icons`, tetap punya label | inline SVG dengan `aria-hidden` + label |
| Tabel | FlatList dengan kolom adaptif/kartu mobile | HTML `<table>` semantik, sticky header |
| Print/share | `expo-print` + `expo-sharing` | `window.print()` + Web Share API fallback download |
| Aksesibilitas | `accessibilityRole`, `accessibilityLabel`, Dynamic Type | semantic HTML, focus ring, `aria-*`, keyboard flow |

Kontrak data mengikuti API: asset menyimpan kode/nama/kategori/kondisi/jumlah/foto/lokasi/keterangan; mutasi menyimpan dari/ke/tipe/jumlah/catatan/pelaku/waktu. Jangan menyimpan secret di frontend. Role `admin` melihat semua menu; `petugas_gudang` tidak melihat Pengguna/Kategori kecuali diberi hak.

## 9. Checklist developer

- [ ] Semua field wajib punya label dan error yang dapat dibaca screen reader.
- [ ] Simulasi loading, kosong, error, offline, sukses, dan duplicate code.
- [ ] Uji satu tangan pada Android 360×800; hit target tidak bertumpuk.
- [ ] Uji desktop 1280×800 dan cetak A4 dengan data panjang.
- [ ] Uji mutasi tidak dapat mengurangi stok di bawah nol dan jejak asal tetap ada.
- [ ] Uji keyboard desktop: tab order, enter submit, escape modal.
