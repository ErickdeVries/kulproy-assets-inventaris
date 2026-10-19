# PROJECT PLAN — Asset-Gudang

## Visi
Aplikasi inventarisasi asset penyimpanan barang bekas di gudang, multi-device
(React Native Android + PWA dari satu codebase Expo), dipakai admin & petugas
gudang untuk mencatat, memantau, dan melaporkan asset.

## Kebutuhan fungsional (disepakati user — versi lengkap)
1. **Pertambahan asset baru**: input asset (kode unik otomatis/manual, nama,
   kategori, kondisi, jumlah, foto, lokasi, keterangan).
2. **Pendataan asset eksisting**: inventarisasi stok yang sudah ada —
   termasuk yang **di dalam gudang** maupun **di luar gudang** (status lokasi).
3. **Perpindahan lokasi**: mutasi asset antar lokasi:
   - luar gudang → dalam gudang (barang masuk)
   - dalam gudang → luar gudang (barang keluar)
   - antar zona/rak di dalam gudang
   Semua mutasi tercatat riwayatnya.
4. **Laporan**: rekap inventaris (jumlah, kondisi, lokasi, kategori) —
   **print out dengan preview** dan **share via WhatsApp**.

## Kebutuhan non-fungsional
- Login sederhana multi-user: role `admin` (semua akses) & `petugas_gudang`
  (input mutasi, lihat laporan).
- Backend terpisah dari frontend, REST API, konfigurasi via env var.
- Mode simulasi lokal untuk pengembangan tanpa kredensial eksternal.
- Tidak ada secret di frontend / git / dokumentasi.
- Dokumentasi progres di `docs/PROGRESS.md` setelah tiap fase.

## Keputusan stack (disepakati user 2026-10-19)
| Lapisan   | Pilihan |
|-----------|---------|
| Backend   | Python FastAPI + MongoDB (Docker), gaya dianastuff |
| Frontend  | React Native (Expo) satu codebase → Android + PWA |
| Auth      | JWT, role admin & petugas_gudang |
| DB        | MongoDB (Docker Compose), simpanan dokumen per asset + riwayat mutasi |

## Roadmap fase
- **Fase 0 — Fondasi**: repo, docker-compose, arsitektur, kontrak API, UX spec. ✅
- **Fase 1 — Backend**: auth, CRUD asset/kategori, mutasi, laporan, health. 
- **Fase 2 — Frontend mobile**: Expo app, layar login, dashboard, list asset,
  form tambah, detail + mutasi, laporan + share WA.
- **Fase 3 — PWA**: build web dari codebase Expo, installable, preview print.
- **Fase 4 — Integrasi & QA**: tes end-to-end, print preview, share WhatsApp,
  uji di device/emulator.

## Lingkup NON-versi-pertama
- Role tambahan (supervisor multi-gudang), multi-cabang.
- Barcode/QR scanner.
- Approval workflow per mutasi.
- Sync offline penuh.