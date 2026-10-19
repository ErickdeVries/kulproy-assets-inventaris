# Test Report Backend

Tanggal: 2026-10-19

Pengujian dilakukan dengan TestClient FastAPI pada mode simulasi in-memory.

Perintah nyata: `.venv/Scripts/python.exe -m pytest -q`.

Hasil nyata terakhir: **5 passed, 1 warning in 2.54s**. Cakupan mencakup health/ready, login/me, role admin, kategori, kode asset otomatis, validasi+riwayat mutasi, dan laporan print/share.

| Skenario | Hasil |
|---|---|
| `/api/v1/health` | PASS |
| Login admin JWT | PASS |
| `/auth/me` | PASS |
| Register petugas oleh admin | PASS |
| CRUD kategori | PASS |
| Buat asset + kode otomatis | PASS |
| Mutasi masuk dan riwayat | PASS |
| Rekap, print HTML, share WA | PASS |
| Soft delete asset | PASS |

MongoDB memiliki adapter pymongo menggunakan `MONGODB_URL` dan `DB_NAME`, tetapi **tidak dinyatakan lulus**: Docker daemon tidak tersedia sehingga pengujian hanya dilakukan pada mode `USE_SIMULATION=true`. Saat mode MongoDB aktif, readiness melakukan ping dan mengembalikan 503 jika database tidak tersedia.
