declare const require: (name: string) => any;
export type SecureStoreLike = { getItemAsync: (key: string) => Promise<string | null>; setItemAsync: (key: string, value: string) => Promise<void>; deleteItemAsync: (key: string) => Promise<void> };
function nativeStore(): SecureStoreLike { return require('expo-secure-store'); }

export type Session = { baseUrl: string; token: string; user: User };
export type User = { id: string; nama: string; username: string; role: string; [key: string]: unknown };
export type AssetForm = { nama: string; kategori_id: string; jumlah: string | number; satuan: string; kondisi: string; tipe: string; zona: string; rak: string; catatan: string; keterangan: string; kode?: string };
const KEY = 'asset-gudang.session';

export function normalizeUrl(input: string): string {
  const value = input.trim().replace(/\/+$/, '');
  let url: URL;
  try { url = new URL(value); } catch { throw new Error('URL API tidak valid. Gunakan http(s)://host/api/v1.'); }
  if (!['http:', 'https:'].includes(url.protocol) || url.username || url.password || url.search || url.hash || !/\/api\/v1$/.test(url.pathname)) throw new Error('URL harus HTTP(S) dan berakhiran /api/v1, tanpa kredensial/query.');
  return url.toString().replace(/\/+$/, '');
}

export function assetPayload(form: AssetForm, categories: Array<{id: string}>): Record<string, unknown> {
  const nama = form.nama.trim(), jumlah = Number(form.jumlah);
  if (!nama || !categories.some(c => c.id === form.kategori_id) || !Number.isInteger(jumlah) || jumlah <= 0 || !['baik','rusak_ringan','rusak_berat'].includes(form.kondisi) || !['dalam_gudang','luar_gudang'].includes(form.tipe)) throw new Error('Lengkapi data asset sesuai schema backend.');
  const result: Record<string, unknown> = { nama, kategori_id: form.kategori_id, jumlah, satuan: form.satuan.trim() || 'unit', kondisi: form.kondisi, lokasi: { tipe: form.tipe, zona: form.zona.trim(), rak: form.rak.trim(), catatan: form.catatan.trim() }, keterangan: form.keterangan.trim(), foto: [] };
  if (form.kode?.trim()) result.kode = form.kode.trim();
  return result;
}

export class Client {
  baseUrl: string | null = null; token: string | null = null; user: User | null = null;
  constructor(private store: SecureStoreLike = nativeStore(), private onUnauthorized = () => {}) {}
  private async save() { if (this.baseUrl && this.token && this.user) await this.store.setItemAsync(KEY, JSON.stringify({baseUrl:this.baseUrl,token:this.token,user:this.user})); }
  private async clear() { await this.store.deleteItemAsync(KEY); this.baseUrl = this.token = null; this.user = null; }
  async connect(url: string) { this.baseUrl = normalizeUrl(url); }
  async login(username: string, password: string) { if (!this.baseUrl) throw new Error('Masukkan URL API terlebih dahulu.'); const data = await this.request('/auth/login','POST',{username,password},false); this.token = data.access_token; this.user = data.user; await this.save(); return this.user; }
  async restore() { const raw = await this.store.getItemAsync(KEY); if (!raw) return false; try { const s = JSON.parse(raw) as Session; this.baseUrl=normalizeUrl(s.baseUrl); this.token=s.token; this.user=s.user; this.user=await this.request('/auth/me'); await this.save(); return true; } catch (e) { if (e instanceof SyntaxError) await this.clear(); else if (!(e instanceof Error && /server|jaringan/i.test(e.message))) await this.clear(); if (e instanceof Error && /server|jaringan/i.test(e.message)) throw e; return false; } }
  async logout() { await this.clear(); }
  private async request(path: string, method='GET', body?: unknown, auth=true): Promise<any> { if (!this.baseUrl) throw new Error('URL API belum diatur.'); let response: Response; try { response = await fetch(this.baseUrl + path, {method, headers:{'Content-Type':'application/json', ...(auth && this.token ? {Authorization:`Bearer ${this.token}`} : {})}, body: body === undefined ? undefined : JSON.stringify(body)}); } catch { throw new Error('Server tidak dapat dihubungi. Periksa URL dan koneksi jaringan.'); } if (response.status === 401) { await this.clear(); this.onUnauthorized(); throw new Error('Sesi berakhir. Silakan login kembali.'); } const data = await response.json().catch(()=>({})); if (!response.ok) throw new Error(data.detail || 'Permintaan gagal.'); return data; }
  report() { return this.request('/laporan/rekap'); }
  categories() { return this.request('/categories'); }
  assets(q='', page=1) { return this.request(`/assets?q=${encodeURIComponent(q)}&page=${page}&limit=20`); }
  asset(id: string) { return this.request(`/assets/${encodeURIComponent(id)}`); }
  createAsset(payload: Record<string, unknown>) { return this.request('/assets','POST',payload); }
  changePassword(current_password: string, new_password: string) { return this.request('/auth/change-password','POST',{current_password,new_password}); }
}
