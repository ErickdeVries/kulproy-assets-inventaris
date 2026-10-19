"""Seed mode simulasi: data awal sudah dibuat oleh app.Store."""
from app.main import store
print(f'Seed siap: {len(store.users)} user, {len(store.categories)} kategori')
