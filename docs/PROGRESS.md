# Progress Backend

- [x] FastAPI app dengan mode simulasi in-memory (`USE_SIMULATION=true`)
- [x] JWT login/me/register admin dan role admin/petugas_gudang
- [x] CRUD kategori
- [x] CRUD asset, kode AG-YYYY-NNNN, foto, soft-delete
- [x] Mutasi masuk/keluar/pindah zona/adjustment dan riwayat
- [x] Rekap, HTML print, share WhatsApp, laporan mutasi
- [x] Health dan readiness
- [x] Dockerfile, compose root, requirements, env example, seed

- [x] Adapter MongoDB nyata berbasis pymongo dengan `MONGODB_URL` dan `DB_NAME`; simulasi tetap fallback.
- [x] Kontrak `JWT_EXPIRE_MINUTES` dengan kompatibilitas `JWT_EXPIRE_HOURS`.
- [x] pytest/TestClient dan laporan pengujian.

Catatan pengujian: 5 test lulus pada mode `USE_SIMULATION=true`. MongoDB belum diverifikasi karena Docker daemon tidak tersedia.
