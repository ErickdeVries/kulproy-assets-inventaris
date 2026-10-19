# ARCHITECTURE — Asset-Gudang

## Arsitektur keseluruhan

```
[Expo React Native app]  --HTTPS/REST-->  [FastAPI]  --pymongo-->  [MongoDB]
   Android + PWA          (JWT Bearer)    (Docker)     (Docker)
```

- **Satu codebase Expo** menghasilkan Android APK dan PWA (web build).
- Backend REST API stateless; auth pakai JWT (access token).
- Frontend tidak pernah menyimpan secret; base URL via env (`EXPO_PUBLIC_API_URL`).
- Mode simulasi lokal: backend bisa dijalankan dengan data seed tanpa layanan eksternal.

## Database (MongoDB)

Collection: `users`, `categories`, `assets`, `movements`, `reports` (metadata laporan, opsional).

### `assets` — dokumen asset
```json
{
  "_id": "ObjectId",
  "kode": "AG-2026-0001",
  "nama": "Kursi kantor rotan",
  "kategori_id": "ObjectId",
  "kondisi": "baik | rusak_ringan | rusak_berat",
  "jumlah": 5,
  "satuan": "unit",
  "lokasi": {"tipe": "dalam_gudang | luar_gudang", "zona": "A1", "rak": "R-02", "catatan": "…"},
  "foto": ["url1", "url2"],
  "keterangan": "…",
  "status": "aktif | nonaktif",
  "dibuat_oleh": "ObjectId(user)",
  "created_at": "ISO",
  "updated_at": "ISO"
}
```

### `movements` — riwayat mutasi
```json
{
  "_id": "ObjectId",
  "asset_id": "ObjectId",
  "tipe": "masuk_gudang | keluar_gudang | pindah_zona | adjustment",
  "dari": {"tipe": "…", "zona": "…", "rak": "…"},
  "ke": {"tipe": "…", "zona": "…", "rak": "…"},
  "jumlah": 5,
  "keterangan": "…",
  "oleh": "ObjectId(user)",
  "created_at": "ISO"
}
```

### `categories`, `users`
`categories`: {nama, deskripsi, created_at}
`users`: {nama, username (unik), password_hash (bcrypt), role: "admin"|"petugas_gudang", aktif, created_at}

## KONTRAK API (sumber kebenaran — backend WAJIB sesuai)

Base: `/api/v1`. Semua endpoint selain `/auth/login`, `/health`, `/ready` butuh
`Authorization: Bearer <token>`.

### Auth
| Method | Path | Body/Query | Respon | Role |
|---|---|---|---|---|
| POST | `/auth/login` | {username, password} | {access_token, user:{id,nama,username,role}} | publik |
| GET | `/auth/me` | - | {id,nama,username,role} | semua |
| POST | `/auth/register` | {nama, username, password, role:"petugas_gudang"} | 201 {id,…} | admin |

### Kategori
| Method | Path | Respon | Role |
|---|---|---|---|
| GET | `/categories` | list {id,nama,deskripsi} | semua |
| POST | `/categories` | 201 | admin |
| PUT | `/categories/{id}` | 200 | admin |
| DELETE | `/categories/{id}` | 204 | admin |

### Asset
| Method | Path | Keterangan |
|---|---|---|
| GET | `/assets` | query: `kategori_id`, `kondisi`, `lokasi_tipe` (dalam_gudang/luar_gudang), `q` (cari nama/kode), `page`, `limit` → {items, total, page, limit} |
| POST | `/assets` | body sesuai skema asset; `kode` otomatis `AG-YYYY-NNNN` bila kosong |
| GET | `/assets/{id}` | detail asset + riwayat mutasinya |
| PUT | `/assets/{id}` | update data master (bukan mutasi lokasi) |
| POST | `/assets/{id}/foto` | upload foto (multipart) → simpan path/URL, return {foto: url} |
| DELETE | `/assets/{id}` | hanya admin; soft-delete status=nonaktif |

### Mutasi / perpindahan lokasi
| Method | Path | Body | Efek |
|---|---|---|---|
| POST | `/assets/{id}/mutasi` | {tipe, ke:{tipe,zona,rak,catatan}, jumlah, keterangan} | update lokasi asset (atau pecah jumlah), tulis dokumen `movements` |
| GET | `/assets/{id}/riwayat` | - | list movements asset |

Aturan mutasi:
- `masuk_gudang`: dari luar → dalam (atau pencatatan awal dalam gudang).
- `keluar_gudang`: dari dalam → luar.
- `pindah_zona`: dalam → dalam (zona/rak berubah).
- Setiap mutasi WAJIB menulis `movements`.
- Jumlah mutasi tidak boleh melebihi jumlah asset (bila asset dipecah → kurangi stok sumber, catat ke lokasi baru).

### Laporan (untuk print & share WhatsApp)
| Method | Path | Keterangan |
|---|---|---|
| GET | `/laporan/rekap` | query: `lokasi_tipe`, `kategori_id`, `kondisi`, `tanggal_awal`, `tanggal_akhir` → rekap jumlah/per-kategori + ringkasan |
| GET | `/laporan/rekap/print` | sama, tapi respon HTML siap cetak (print preview browser) |
| GET | `/laporan/rekap/share-wa` | respon {text} — teks ringkasan siap share; frontend buka `https://wa.me/?text=…` |
| GET | `/laporan/mutasi` | query tanggal → riwayat mutasi periode tertentu |

Alur print: frontend ambil data rekap → render layout cetak (mobile/desktop) →
`window.print()` (PWA) / print service (Android). Preview = halaman/layar
sebelum print yang menampilkan layout persis.

Alur share WA (Android): `Linking.openURL("https://wa.me/?text=" + encodeURIComponent(text))`
atau `Share.share({message})`; PWA: buka URL wa.me.

### Health
| Method | Path | Respon |
|---|---|---|
| GET | `/health` | 200 {status:"ok"} — liveness, tanpa dependensi |
| GET | `/ready` | 200 {status:"ready"} bila MongoDB reachable, else 503 |

## Struktur backend
```
backend/
├── app/
│   ├── main.py            # FastAPI app, middleware CORS, router mount
│   ├── config.py          # env: MONGODB_URL, DB_NAME, JWT_SECRET, dst.
│   ├── models/            # pydantic schemas (asset, movement, user, category)
│   ├── routers/           # auth, categories, assets, movements, laporan, health
│   ├── services/          # logika bisnis (kode generator, mutasi, laporan)
│   └── auth/              # hashing password, JWT create/decode, dependency
├── requirements.txt
├── .env.example
├── Dockerfile
└── seed.py                # data awal: admin default + kategori contoh (hanya dev)
```

## Standar
- Pydantic v2 untuk validasi; FastAPI auto docs di `/docs`.
- Password di-hash bcrypt; JWT expiry (contoh 12 jam); secret via env, tidak di repo.
- CORS diizinkan untuk dev (asl frontend).
- Semua timestamp ISO 8601 UTC; frontend tampilkan zona lokal.