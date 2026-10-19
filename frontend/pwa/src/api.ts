export type AssetStatus = 'Dalam gudang' | 'Di luar gudang'
export type BrandingSettings = { id?: string; title: string; subtitle: string; updated_at?: string }
export type SessionUser = { id: string; nama: string; jabatan?: string; id_type?: string; id_number?: string; username: string; role: 'admin' | 'non_admin' | string; aktif?: boolean; active?: boolean; allowed_menus?: string[] }
export type WhitelistUser = SessionUser & { password?: string }
export type Permissions = { user_id: string; allowed_menus: string[] }
export type ApprovalStatus = 'draft' | 'pending' | 'approved' | 'rejected'
export type AuditLog = { id:string; aktor:string; aksi:string; asset_id?:string; dokumen_id?:string; status:string; keterangan:string; timestamp:string }
export type Approval = { id:string; asset_id:string; tipe:'mutasi'|'perubahan_asset'; status:ApprovalStatus; pic_approver_id:string; pihak_pengaju:string; pihak_approver?:string; tanda_tangan_pengaju:string; tanda_tangan_approver?:string; keterangan:string; payload?:Record<string, unknown> }
export type Asset = {
  id: string; name: string; category: string; location: string; condition: string;
  status: AssetStatus; updated: string; code: string; date: string;
  volume?: number; unit?: string; area?: string;
  gps?: { latitude: number; longitude: number };
  notes?: string; photoUrl?: string;
}

export const API_URL = import.meta.env.VITE_API_URL || import.meta.env.EXPO_PUBLIC_API_URL || ''
export const demoMode = !API_URL
// Demo identity is metadata only; authentication secrets stay server-side.
export const DEMO_SESSION: SessionUser = {
  id: 'u-demo-admin', nama: 'Demo Administrator', jabatan: 'Administrator',
  id_type: 'demo', id_number: 'DEMO-ADMIN', username: 'demo-admin', role: 'admin',
  active: true, aktif: true, allowed_menus: ['dashboard', 'assets', 'report', 'approvals', 'audit', 'settings'],
}
const authHeaders = () => {
  const token = localStorage.getItem('asset-gudang-token')
  return token ? { Authorization: `Bearer ${token}` } : {}
}

const demoAssets: Asset[] = [
  { id:'AST-24001', code:'AST-24001', name:'Kursi lipat besi', category:'Furniture', location:'Gudang Utama · Rak A-03', condition:'Baik', status:'Dalam gudang', updated:'Hari ini, 09:12', date:'2026-10-19' },
  { id:'AST-24002', code:'AST-24002', name:'Proyektor Epson EB-X06', category:'Elektronik', location:'Dipinjam · Ruang Rapat 2', condition:'Baik', status:'Di luar gudang', updated:'Kemarin, 14:35', date:'2026-10-18' },
  { id:'AST-24003', code:'AST-24003', name:'Meja kerja modular', category:'Furniture', location:'Gudang Utama · Rak B-01', condition:'Perlu perbaikan', status:'Dalam gudang', updated:'18 Okt 2026, 16:08', date:'2026-10-18' },
  { id:'AST-24004', code:'AST-24004', name:'Laptop Lenovo ThinkPad', category:'Elektronik', location:'Dipinjam · Tim Operasional', condition:'Baik', status:'Di luar gudang', updated:'18 Okt 2026, 11:20', date:'2026-10-18' },
  { id:'AST-24005', code:'AST-24005', name:'Kabel roll 25 meter', category:'Peralatan', location:'Gudang Utama · Rak C-02', condition:'Baik', status:'Dalam gudang', updated:'17 Okt 2026, 10:44', date:'2026-10-17' },
  { id:'AST-24006', code:'AST-24006', name:'Papan tulis whiteboard', category:'Furniture', location:'Gudang Utama · Rak A-01', condition:'Rusak', status:'Dalam gudang', updated:'16 Okt 2026, 08:50', date:'2026-10-16' },
]

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const headers = new Headers(options?.headers)
  headers.set('Content-Type', 'application/json')
  const token = localStorage.getItem('asset-gudang-token')
  if (token) headers.set('Authorization', `Bearer ${token}`)
  const response = await fetch(`${API_URL}${path}`, { ...options, headers })
  if (!response.ok) throw new Error(`API ${response.status}`)
  return response.json()
}
export const api = {
  login: (body: unknown) => request<{access_token:string; user:SessionUser}>('/auth/login', { method:'POST', body:JSON.stringify(body) }),
  settings: (): Promise<BrandingSettings> => request<BrandingSettings>('/settings'),
  updateSettings: (body: BrandingSettings): Promise<BrandingSettings> => request<BrandingSettings>('/settings', { method:'PUT', body:JSON.stringify(body) }),
  session: (): Promise<SessionUser> => request('/auth/session'),
  users: (): Promise<WhitelistUser[]> => request('/users'),
  createUser: (body: unknown) => request('/users', { method:'POST', body:JSON.stringify(body) }),
  updateUser: (id: string, body: unknown) => request(`/users/${id}`, { method:'PUT', body:JSON.stringify(body) }),
  permissions: (id: string): Promise<Permissions> => request(`/users/${id}/permissions`),
  updatePermissions: (id: string, body: { allowed_menus: string[] }) => request(`/users/${id}/permissions`, { method:'PUT', body:JSON.stringify(body) }),
  changePassword: (body: { current_password: string; new_password: string }) => request('/auth/change-password', { method:'POST', body:JSON.stringify(body) }),
  logout: () => localStorage.removeItem('asset-gudang-token'),
  assets: async (): Promise<Asset[]> => demoMode ? demoAssets : (await request<{items: Asset[]}>('/assets')).items,
  categories: async (): Promise<string[]> => demoMode ? ['Furniture','Elektronik','Peralatan','Kendaraan'] : (await request<Array<{nama:string}>>('/categories')).map(c=>c.nama),
  mutasi: (assetId: string, body: unknown) => request(`/assets/${assetId}/mutasi`, { method:'POST', body:JSON.stringify(body) }),
  approvals: async (): Promise<Approval[]> => demoMode ? [] : request('/approvals'),
  auditLogs: async (): Promise<AuditLog[]> => demoMode ? JSON.parse(localStorage.getItem('asset-gudang-audit') || '[]') : request('/audit-logs'),
  evidence: (assetId:string, body:unknown) => demoMode ? Promise.resolve(body) : request(`/assets/${assetId}/evidence`, { method:'POST', body:JSON.stringify(body) }),
  createApproval: (body: unknown) => demoMode ? Promise.resolve(body as Approval) : request('/approvals', { method:'POST', body:JSON.stringify(body) }),
  updateApproval: (id: string, body: unknown) => request(`/approvals/${id}`, { method:'PUT', body:JSON.stringify(body) }),
  exportApproval: (id:string) => request(`/approvals/${id}/export`),
  importApproval: (body: unknown) => request('/approvals/import', { method:'POST', body:JSON.stringify(body) }),
  laporan: async () => demoMode ? { total: demoAssets.length, dalam: demoAssets.filter(a=>a.status==='Dalam gudang').length, luar: demoAssets.filter(a=>a.status==='Di luar gudang') .length } : request('/laporan'),
}
