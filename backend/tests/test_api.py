import os

os.environ.setdefault("USE_SIMULATION", "true")
os.environ.setdefault("JWT_EXPIRE_MINUTES", "60")

from fastapi.testclient import TestClient
from app.main import app, store

client = TestClient(app)


def auth_headers():
    response = client.post("/api/v1/auth/login", json={"username": "admin", "password": "admin123"})
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_health_and_ready():
    assert client.get("/api/v1/health").json() == {"status": "ok"}


def test_mutation_approval_status_export_import_and_print():
    headers = auth_headers()
    category = client.post("/api/v1/categories", json={"nama": "Mutasi Test"}, headers=headers)
    assert category.status_code in (201, 409)
    category_id = category.json().get("id") or store.categories[0]["id"]
    created_asset = client.post("/api/v1/assets", json={
        "nama": "Asset Mutasi Test", "kategori_id": category_id,
        "kondisi": "baik", "jumlah": 1,
        "lokasi": {"tipe": "dalam_gudang", "zona": "A", "rak": "1"},
    }, headers=headers)
    assert created_asset.status_code == 201
    asset = created_asset.json()
    approval_payload = {
        "asset_id": asset["id"], "tipe": "mutasi", "status": "pending",
        "pic_approver_id": "u-supervisor", "pihak_pengaju": "Petugas",
        "tanda_tangan_pengaju": "data:image/png;base64,signature", "keterangan": "uji",
        "payload": {"tipe": "pindah_zona", "jumlah": 1, "tujuan": "Area Sortir"},
    }
    created = client.post("/api/v1/approvals", json=approval_payload, headers=headers)
    assert created.status_code == 201
    approval = created.json()
    assert client.get("/api/v1/approvals", headers=headers).json()[-1]["id"] == approval["id"]
    updated = client.put(f"/api/v1/approvals/{approval['id']}", json={
        "status": "approved", "pihak_approver": "Supervisor",
        "tanda_tangan_approver": "data:image/png;base64,approver",
    }, headers=headers)
    assert updated.status_code == 200
    exported = client.get(f"/api/v1/approvals/{approval['id']}/export", headers=headers)
    assert exported.status_code == 200 and exported.json()["approval"]["id"] == approval["id"]
    imported = client.post("/api/v1/approvals/import", json=exported.json(), headers=headers)
    assert imported.status_code == 201
    printable = client.get("/api/v1/laporan/rekap/print", headers=headers)
    assert printable.status_code == 200 and "Rekap Asset Gudang" in printable.text
    assert client.get("/api/v1/ready").json()["mode"] == "simulation"


def test_login_and_me():
    headers = auth_headers()
    response = client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["username"] == "admin"
    assert response.json()["role"] == "admin"


def test_admin_role_required():
    headers = auth_headers()
    created = client.post("/api/v1/auth/register", headers=headers, json={
        "nama": "Petugas", "username": "petugas-test", "password": "secret123", "role": "petugas_gudang"
    })
    assert created.status_code == 201
    login = client.post("/api/v1/auth/login", json={"username": "petugas-test", "password": "secret123"})
    user_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    assert client.post("/api/v1/categories", headers=user_headers, json={"nama": "Ditolak"}).status_code == 403


def test_category_asset_auto_code_and_reports():
    headers = auth_headers()
    category = client.post("/api/v1/categories", headers=headers, json={"nama": "Elektronik", "deskripsi": "Perangkat"})
    assert category.status_code == 201
    category_id = category.json()["id"]
    asset = client.post("/api/v1/assets", headers=headers, json={
        "nama": "Laptop", "kategori_id": category_id, "kondisi": "baik", "jumlah": 3,
        "lokasi": {"tipe": "dalam_gudang", "zona": "A1", "rak": "R1"}
    })
    assert asset.status_code == 201
    asset_data = asset.json()
    assert asset_data["kode"].startswith("AG-")
    assert len(asset_data["kode"].split("-")[-1]) == 4
    assert client.get("/api/v1/categories", headers=headers).status_code == 200
    assert client.get("/api/v1/laporan/rekap", headers=headers).json()["total_unit"] >= 3
    assert client.get("/api/v1/laporan/rekap/print", headers=headers).headers["content-type"].startswith("text/html")
    assert "Total unit" in client.get("/api/v1/laporan/rekap/print", headers=headers).text
    assert "Total unit" in client.get("/api/v1/laporan/rekap/share-wa", headers=headers).json()["text"]


def test_mutation_validation_and_history():
    headers = auth_headers()
    category_id = next(iter(store.categories))
    asset = client.post("/api/v1/assets", headers=headers, json={
        "nama": "Kursi", "kategori_id": category_id, "kondisi": "baik", "jumlah": 2,
        "lokasi": {"tipe": "dalam_gudang", "zona": "B1", "rak": "R2"}
    }).json()
    aid = asset["id"]
    invalid = client.post(f"/api/v1/assets/{aid}/mutasi", headers=headers, json={
        "tipe": "keluar_gudang", "ke": {"tipe": "luar_gudang", "zona": "X", "rak": "Y"}, "jumlah": 3
    })
    assert invalid.status_code == 400
    moved = client.post(f"/api/v1/assets/{aid}/mutasi", headers=headers, json={
        "tipe": "pindah_zona", "ke": {"tipe": "dalam_gudang", "zona": "B2", "rak": "R3"}, "jumlah": 1
    })
    assert moved.status_code == 200
    history = client.get(f"/api/v1/assets/{aid}/riwayat", headers=headers)
    assert history.status_code == 200
    assert len(history.json()) == 1


def test_phase1_admin_endpoints_and_non_admin_forbidden():
    admin = auth_headers()
    settings = client.get("/api/v1/settings", headers=admin)
    assert settings.status_code == 200
    updated = client.put("/api/v1/settings", headers=admin, json={"title":"TEST-ASSETS","subtitle":"TEST INVENTORY"})
    assert updated.status_code == 200 and updated.json()["title"] == "TEST-ASSETS"
    users = client.get("/api/v1/users", headers=admin)
    assert users.status_code == 200
    created = client.post("/api/v1/users", headers=admin, json={"nama":"Operator Test","jabatan":"Ops","id_type":"KTP","id_number":"T-1","username":"operator-test","password":"secret123","role":"non_admin","active":True,"allowed_menus":["dashboard"]})
    assert created.status_code == 201
    user_id = created.json()["id"]
    changed = client.put(f"/api/v1/users/{user_id}", headers=admin, json={"nama":"Operator Updated","active":True})
    assert changed.status_code == 200
    perms = client.get(f"/api/v1/users/{user_id}/permissions", headers=admin)
    assert perms.status_code == 200
    assert client.put(f"/api/v1/users/{user_id}/permissions", headers=admin, json={"allowed_menus":["dashboard","assets"]}).status_code == 200
    assert client.get("/api/v1/auth/session", headers=admin).status_code == 200
    assert client.post("/api/v1/auth/change-password", headers=admin, json={"current_password":"admin123","new_password":"admin456"}).status_code == 200

    login = client.post("/api/v1/auth/login", json={"username":"operator-test","password":"secret123"})
    assert login.status_code == 200
    non_admin = {"Authorization": f"Bearer {login.json()['access_token']}"}
    assert client.get("/api/v1/settings", headers=non_admin).status_code == 403
    assert client.get("/api/v1/users", headers=non_admin).status_code == 403

    # Keep simulation state isolated for subsequent tests.
    store.__init__()
