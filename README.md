# Asset-Gudang — Inventarisasi Asset Penyimpanan Barang Bekas

Aplikasi fullstack multi-device untuk inventarisasi asset barang bekas di gudang:
pencatatan asset baru, pendataan asset eksisting (di dalam & di luar gudang),
perpindahan lokasi asset (luar → dalam, dalam → luar), laporan yang bisa
di-print (dengan preview) dan di-share ke WhatsApp.

- **Frontend Mobile**: React Native (Expo) — Android & PWA dari satu codebase
- **Backend**: Python FastAPI + MongoDB (Docker Compose)
- **Auth**: JWT — role `admin` dan `petugas_gudang`
- **Dokumentasi proyek**: `docs/` (PLAN, ARCHITECTURE, PROGRESS, DECISIONS, TEST_REPORT)

## Struktur repositori

```
asset-gudang/
├── backend/            # FastAPI + MongoDB (Docker)
├── frontend/
│   ├── mobile/         # Expo React Native (Android + PWA)
│   └── pwa/            # Referensi/turunan web (opsional)
├── docs/
│   ├── PROJECT_PLAN.md
│   ├── ARCHITECTURE.md   # termasuk kontrak API (sumber kebenaran)
│   ├── UX_SPEC.md        # hasil desain agent UX (UX_SPEC + HTML preview)
│   ├── ux-preview/       # HTML preview hasil desain UX
│   └── PROGRESS.md
└── docker-compose.yml
```

## Cara menjalankan (ringkas)

```bash
# Backend (perlu Docker Desktop aktif)
docker compose up -d mongo
cd backend && pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend mobile (Expo)
cd frontend/mobile && npm install && npx expo start
```

Detail lengkap: `docs/PROJECT_PLAN.md`, `docs/ARCHITECTURE.md`.