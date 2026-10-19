# UX SPEC — Asset-Gudang (arah desain untuk agent UX)

Ringkasan arah desain untuk agent UX Designer. Agent UX WAJIB membaca file ini,
lalu menghasilkan `docs/UX_SPEC.md` lengkap + HTML high-fidelity preview di
`docs/ux-preview/`.

## Produk
Aplikasi inventarisasi asset barang bekas di gudang. Pengguna harian: **petugas
gudang** (input cepat, di lapangan, pakai HP Android) dan **admin** (kelola
kategori/akun, pantau, laporan via laptop/desktop PWA). Multi-device: mobile
utama, desktop sekunder.

## Tujuan pengalaman
1. **Cepat & minim klik**: petugas mencatat barang di gudang — form singkat,
   default cerdas, auto-save ide.
2. **Satu pandangan status**: tahu persis berapa asset di dalam vs di luar
   gudang, kondisi, kategori — dashboard dengan angka besar.
3. **Mutasi jelas & tercatat**: alur "pindahkan lokasi" yang jelas (dari/ke),
   tanpa kehilangan posisi asal.
4. **Laporan yang benar-benar dipakai**: rekap rapi → preview cetak → share
   WhatsApp dalam 2-3 ketukan.

## Prinsip desain
- Bahasa **Indonesia** untuk semua label & teks UI.
- Tema industrial/warehouse: netral + aksen (mis. jingga/amber) — kontras baik
  untuk pemakaian luar ruangan.
- Tipografi besar untuk data kunci, jarak antar-elemen lega untuk jari.
- Navigasi bottom tab (mobile): Beranda, Asset, Tambah (FAB), Mutasi, Laporan.
- Status lokasi & kondisi memakai **badge warna** yang konsisten:
  - dalam gudang = hijau; luar gudang = amber; kondisi baik = hijau,
    rusak ringan = amber, rusak berat = merah.

## Layar wajib (mobile, high-fidelity)
1. Login
2. Dashboard (KPI: total asset, dalam gudang, luar gudang, mutasi terbaru)
3. Daftar Asset (filter: kategori, kondisi, lokasi; search; badge status)
4. Form Tambah Asset (foto, kategori, kondisi, jumlah, lokasi)
5. Detail Asset (info + riwayat mutasi + tombol Pindahkan/Edit)
6. Form Mutasi (dari→ke, tipe, jumlah, keterangan)
7. Laporan (rekap + preview cetak + share WhatsApp + kirim ke printer)

## Layar desktop/PWA (hi-fi atau wireframe)
1. Dashboard admin
2. Tabel asset dengan filter
3. Preview laporan cetak

## Deliverable agent UX
1. `docs/UX_SPEC.md` — spek lengkap: user flow, wireframe ASCII, UI kit warna
   (hex), tipografi, komponen (button/badge/form/card/table print), states.
2. `docs/ux-preview/index.html` — **satu file HTML** preview UI mobile
   (beberapa layar) dan desktop, visual high-fidelity, self-contained
   (CSS inline, font sistem), tema gelap/terang sesuai konteks, tanpa gambar
   eksternal (pakai ikon emoji/SVG inline). Bisa dibuka langsung di browser.
3. Kesimpulan singkat + rekomendasi untuk developer (komponen React yang
   diusulkan).

## Catatan untuk developer (hasil desain dipakai di Fase 2)
- Agent UX menghasilkan spesifikasi warna/komponen → developer React Native
  menerjemahkannya → konsistensi antar platform.
- Preview HTML adalah acuan visual; struktur data mengikuti kontrak API di
  ARCHITECTURE.md.