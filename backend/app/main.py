import os, re, html, base64
from datetime import datetime, timedelta, timezone
from typing import Optional, Literal, Any
from pymongo import MongoClient
from fastapi import FastAPI, HTTPException, Depends, Header, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field, ConfigDict
import bcrypt, jwt

SECRET=os.getenv('JWT_SECRET','dev-secret-change-me')
# Kontrak utama menggunakan menit; HOURS dipertahankan untuk kompatibilitas lama.
EXPIRE_MINUTES=int(os.getenv('JWT_EXPIRE_MINUTES', str(int(os.getenv('JWT_EXPIRE_HOURS','12')) * 60)))
USE_SIM=os.getenv('USE_SIMULATION','true').lower() in {'1','true','yes'}
now=lambda: datetime.now(timezone.utc).isoformat()

def uid(prefix=''): return prefix+base64.urlsafe_b64encode(os.urandom(9)).decode().rstrip('=')
def hashpw(p): return bcrypt.hashpw(p.encode(),bcrypt.gensalt()).decode()
def verify(p,h): return bcrypt.checkpw(p.encode(),h.encode())

class Store:
 def __init__(self):
  self.users={}; self.categories={}; self.assets={}; self.movements=[]; self.approvals=[]; self.mutation_evidence=[]; self.audit_logs=[]
  self.app_settings={'id':'app','title':'KULPROY-ASSETS','subtitle':'INVENTARIS OPERASIONAL','updated_at':now()}
  self.users['u-admin']={'id':'u-admin','nama':'Administrator','jabatan':'Administrator','id_type':'internal','id_number':'ADMIN','username':'admin','password_hash':hashpw('admin123'),'role':'admin','aktif':True,'active':True,'allowed_menus':['dashboard','assets','report','approvals','audit','settings'],'created_at':now()}
  self.categories['c-general']={'id':'c-general','nama':'Umum','deskripsi':'Kategori umum','created_at':now()}
class MongoDict:
 def __init__(self, collection): self.collection=collection
 def get(self, key, default=None):
  doc=self.collection.find_one({'id':key}); return {k:v for k,v in doc.items() if k!='_id'} if doc else default
 def __getitem__(self,key):
  value=self.get(key)
  if value is None: raise KeyError(key)
  return value
 def __setitem__(self,key,value): self.collection.replace_one({'id':key},{**value,'id':key},upsert=True)
 def __contains__(self,key): return self.get(key) is not None
 def values(self): return [dict(x) for x in self.collection.find({}, {'_id':0})]
 def update(self, values):
  for key,value in values.items(): self[key]=value
 def __delitem__(self,key): self.collection.delete_one({'id':key})

class MongoStore(Store):
 def __init__(self):
  self.client=MongoClient(os.getenv('MONGODB_URL','mongodb://localhost:27017'), serverSelectionTimeoutMS=1500)
  self.db=self.client[os.getenv('DB_NAME','asset_gudang')]
  self.users=MongoDict(self.db.users); self.categories=MongoDict(self.db.categories); self.assets=MongoDict(self.db.assets)
  self.movements=MongoList(self.db.movements)
  if not self.users.get('u-admin'): self.users['u-admin']={'id':'u-admin','nama':'Administrator','username':'admin','password_hash':hashpw('admin123'),'role':'admin','aktif':True,'created_at':now()}
  if not self.categories.get('c-general'): self.categories['c-general']={'id':'c-general','nama':'Umum','deskripsi':'Kategori umum','created_at':now()}
 def ping(self): self.client.admin.command('ping')

class MongoList:
 def __init__(self, collection): self.collection=collection
 def append(self,value): self.collection.insert_one(value)
 def __iter__(self): return iter([dict(x) for x in self.collection.find({}, {'_id':0})])
 def __len__(self): return self.collection.count_documents({})
 def __getitem__(self,index): return list(self)[index]

store=Store() if USE_SIM else MongoStore()

def public_user(u):
 return {k:u.get(k) for k in ('id','nama','jabatan','id_type','id_number','username','role','aktif','active','allowed_menus')}
def safe_user(u): return {k:v for k,v in u.items() if k!='password_hash'}
def audit_change(u, aksi, detail): audit(u, aksi, 'success', detail)

def ensure_settings():
 if not hasattr(store, 'app_settings'): store.app_settings={'id':'app','title':'KULPROY-ASSETS','subtitle':'INVENTARIS OPERASIONAL','updated_at':now()}
 return store.app_settings
def token(u): return jwt.encode({'sub':u['id'],'exp':datetime.now(timezone.utc)+timedelta(minutes=EXPIRE_MINUTES)},SECRET,algorithm='HS256')
def auth(authorization: Optional[str]=Header(None)):
 if not authorization or not authorization.lower().startswith('bearer '): raise HTTPException(401,'Token diperlukan')
 try: p=jwt.decode(authorization.split()[1],SECRET,algorithms=['HS256']); u=store.users.get(p['sub'])
 except Exception: raise HTTPException(401,'Token tidak valid')
 if not u or not u.get('aktif', u.get('active', True)): raise HTTPException(401,'Pengguna tidak aktif')
 return u
def admin(u=Depends(auth)):
 if u['role']!='admin': raise HTTPException(403,'Akses admin diperlukan')
 return u

class Login(BaseModel): username:str; password:str
class Register(BaseModel): nama:str; username:str; password:str=Field(min_length=6); role:Literal['petugas_gudang']
class CategoryIn(BaseModel): nama:str=Field(min_length=1); deskripsi:str=''
class Location(BaseModel): tipe:Literal['dalam_gudang','luar_gudang']; zona:str=''; rak:str=''; catatan:str=''
class AssetIn(BaseModel):
 nama:str; kategori_id:str; kondisi:Literal['baik','rusak_ringan','rusak_berat']; jumlah:int=Field(gt=0); satuan:str='unit'; lokasi:Location; foto:list[str]=[]; keterangan:str=''; kode:Optional[str]=None
class MovementIn(BaseModel):
 tipe:Literal['masuk_gudang','keluar_gudang','pindah_zona','adjustment']; ke:Location; jumlah:int=Field(gt=0); keterangan:str=''
class AssetChangeIn(BaseModel):
 nama:str; kategori_id:str; kondisi:Literal['baik','rusak_ringan','rusak_berat']; jumlah:int=Field(gt=0); satuan:str='unit'; lokasi:Location; foto:list[str]=[]; keterangan:str=''; kode:Optional[str]=None; pic_id:str=Field(min_length=1); alasan_perubahan:str=Field(min_length=1)
class ApprovalIn(BaseModel):
 asset_id:str; tipe:Literal['perubahan_asset','mutasi']; status:Literal['draft','pending','approved','rejected']='draft'; pic_approver_id:str=Field(min_length=1); pihak_pengaju:str=Field(min_length=1); tanda_tangan_pengaju:str=Field(min_length=1); pihak_approver:str=''; tanda_tangan_approver:str=''; keterangan:str=''; payload:dict[str,Any]={}
class ApprovalStatusIn(BaseModel):
 status:Literal['draft','pending','approved','rejected']; pihak_approver:str=''; tanda_tangan_approver:str=''
class EvidenceIn(BaseModel):
 alasan_perubahan:str=Field(min_length=1); tipe:Literal['edit','delete','mutasi']='edit'; pic_pengaju:str=Field(min_length=1); pic_approver:str=''; tanda_tangan_pengaju:str=''; tanda_tangan_approver:str=''; bukti:str=''; status:Literal['draft','pending','approved','rejected']='pending'
class SettingsIn(BaseModel): title:str=Field(min_length=1); subtitle:str=Field(min_length=1)
class UserIn(BaseModel):
 nama:str=Field(min_length=1); jabatan:str=''; id_type:str=''; id_number:str=''; username:str=Field(min_length=1); password:Optional[str]=Field(default=None,min_length=6); role:Literal['admin','non_admin']='non_admin'; active:bool=True; allowed_menus:list[str]=[]
class UserUpdate(BaseModel):
 nama:Optional[str]=None; jabatan:Optional[str]=None; id_type:Optional[str]=None; id_number:Optional[str]=None; username:Optional[str]=None; password:Optional[str]=Field(default=None,min_length=6); role:Optional[Literal['admin','non_admin']]=None; active:Optional[bool]=None; allowed_menus:Optional[list[str]]=None
class PermissionsIn(BaseModel): allowed_menus:list[str]
class PasswordIn(BaseModel): current_password:str; new_password:str=Field(min_length=6)

app=FastAPI(title='Asset Gudang API',version='1.0.0')
app.add_middleware(CORSMiddleware,allow_origins=['*'],allow_methods=['*'],allow_headers=['*'])

def audit(u, aksi, status, keterangan='', asset_id=None, dokumen_id=None):
 d={'id':uid('audit-'),'aktor_id':u.get('id') if u else None,'aktor':u.get('nama') if u else 'system','aksi':aksi,'asset_id':asset_id,'dokumen_id':dokumen_id,'status':status,'keterangan':keterangan,'timestamp':now()}
 store.audit_logs.append(d); return d
def item(a): return {k:v for k,v in a.items() if k!='_deleted'}
def next_code():
 y=datetime.now().year; nums=[int(x['kode'][-4:]) for x in store.assets.values() if re.match(r'^AG-\d{4}-\d{4}$',x['kode']) and x['kode'].startswith(f'AG-{y}-')]
 return f'AG-{y}-{(max(nums,default=0)+1):04d}'
def require_cat(cid):
 if cid not in store.categories: raise HTTPException(400,'Kategori tidak ditemukan')

@app.get('/api/v1/health')
def health(): return {'status':'ok'}
@app.get('/api/v1/ready')
def ready():
 if not USE_SIM:
  try: store.ping()
  except Exception: raise HTTPException(503,'MongoDB tidak tersedia')
 return {'status':'ready','mode':'simulation' if USE_SIM else 'mongodb'}
@app.post('/api/v1/auth/login')
def login(x:Login):
 u=next((u for u in store.users.values() if u['username']==x.username),None)
 if not u or not verify(x.password,u['password_hash']): raise HTTPException(401,'Username atau password salah')
 audit(u,'login','success','Login berhasil')
 return {'access_token':token(u),'token_type':'bearer','user':public_user(u)}
@app.get('/api/v1/auth/me')
def me(u=Depends(auth)): return public_user(u)
@app.post('/api/v1/auth/register',status_code=201)
def register(x:Register,_=Depends(admin)):
 if any(u['username']==x.username for u in store.users.values()): raise HTTPException(409,'Username sudah digunakan')
 u={'id':uid('u-'),'nama':x.nama,'username':x.username,'password_hash':hashpw(x.password),'role':x.role,'aktif':True,'active':True,'allowed_menus':[],'created_at':now()}; store.users[u['id']]=u; return public_user(u)

@app.get('/api/v1/auth/session')
def session(u=Depends(auth)): return public_user(u)
@app.post('/api/v1/auth/change-password')
def change_password(x:PasswordIn,u=Depends(auth)):
 if not verify(x.current_password,u['password_hash']): raise HTTPException(400,'Password saat ini salah')
 store.users[u['id']]['password_hash']=hashpw(x.new_password); audit(u,'password_change','success','Password diperbarui'); return {'status':'ok'}

@app.get('/api/v1/settings')
def get_settings(_:Any=Depends(admin)): return ensure_settings()
@app.put('/api/v1/settings')
def update_settings(x:SettingsIn,u=Depends(admin)):
 s=ensure_settings(); s.update(x.model_dump(),updated_at=now()); audit_change(u,'settings_update','Branding aplikasi diperbarui'); return s
@app.get('/api/v1/users')
def users(_:Any=Depends(admin)): return [safe_user(u) for u in store.users.values()]
@app.post('/api/v1/users',status_code=201)
def create_user(x:UserIn,u=Depends(admin)):
 if any(v.get('username')==x.username for v in store.users.values()): raise HTTPException(409,'Username sudah digunakan')
 if not x.password: raise HTTPException(422,'Password wajib untuk user baru')
 d=x.model_dump(); d['id']=uid('u-'); d['password_hash']=hashpw(x.password); d['aktif']=d['active']; d['created_at']=now(); del d['password']; store.users[d['id']]=d; audit_change(u,'user_create','Whitelist user dibuat'); return safe_user(d)
@app.put('/api/v1/users/{user_id}')
def update_user(user_id:str,x:UserUpdate,u=Depends(admin)):
 d=store.users.get(user_id)
 if not d: raise HTTPException(404,'User tidak ditemukan')
 vals=x.model_dump(exclude_unset=True); password=vals.pop('password',None); d.update(vals)
 if password: d['password_hash']=hashpw(password)
 if 'active' in vals: d['aktif']=vals['active']
 store.users[user_id]=d; audit_change(u,'user_update','Whitelist user diperbarui'); return safe_user(d)
@app.get('/api/v1/users/{user_id}/permissions')
def get_permissions(user_id:str,_=Depends(admin)):
 d=store.users.get(user_id)
 if not d: raise HTTPException(404,'User tidak ditemukan')
 return {'user_id':user_id,'allowed_menus':d.get('allowed_menus',[])}
@app.put('/api/v1/users/{user_id}/permissions')
def update_permissions(user_id:str,x:PermissionsIn,u=Depends(admin)):
 d=store.users.get(user_id)
 if not d: raise HTTPException(404,'User tidak ditemukan')
 d['allowed_menus']=x.allowed_menus; store.users[user_id]=d; audit_change(u,'permissions_update','Menu user diperbarui'); return {'user_id':user_id,'allowed_menus':d['allowed_menus']}

@app.get('/api/v1/categories')
def categories(_:Any=Depends(auth)): return [item(x) for x in store.categories.values()]
@app.post('/api/v1/categories',status_code=201)
def create_cat(x:CategoryIn,_=Depends(admin)):
 if any(c['nama'].lower()==x.nama.lower() for c in store.categories.values()): raise HTTPException(409,'Kategori sudah ada')
 c={'id':uid('c-'),'nama':x.nama,'deskripsi':x.deskripsi,'created_at':now()}; store.categories[c['id']]=c; return c
@app.put('/api/v1/categories/{cid}')
def update_cat(cid:str,x:CategoryIn,_=Depends(admin)):
 if cid not in store.categories: raise HTTPException(404,'Kategori tidak ditemukan')
 store.categories[cid].update(x.model_dump()); return store.categories[cid]
@app.delete('/api/v1/categories/{cid}',status_code=204)
def delete_cat(cid:str,_=Depends(admin)):
 if cid not in store.categories: raise HTTPException(404,'Kategori tidak ditemukan')
 del store.categories[cid]

def filtered_assets(kategori_id=None,kondisi=None,lokasi_tipe=None,q=None):
 arr=[a for a in store.assets.values() if not a.get('_deleted')]
 if kategori_id: arr=[a for a in arr if a['kategori_id']==kategori_id]
 if kondisi: arr=[a for a in arr if a['kondisi']==kondisi]
 if lokasi_tipe: arr=[a for a in arr if a['lokasi']['tipe']==lokasi_tipe]
 if q: arr=[a for a in arr if q.lower() in a['nama'].lower() or q.lower() in a['kode'].lower()]
 return arr
@app.get('/api/v1/assets')
def assets(kategori_id:str=None,kondisi:str=None,lokasi_tipe:str=None,q:str=None,page:int=Query(1,ge=1),limit:int=Query(20,ge=1,le=100),_:Any=Depends(auth)):
 arr=filtered_assets(kategori_id,kondisi,lokasi_tipe,q); start=(page-1)*limit
 return {'items':[item(a) for a in arr[start:start+limit]],'total':len(arr),'page':page,'limit':limit}
@app.post('/api/v1/assets',status_code=201)
def create_asset(x:AssetIn,u=Depends(auth)):
 require_cat(x.kategori_id); d=x.model_dump(); d.update(id=uid('a-'),kode=x.kode or next_code(),status='aktif',dibuat_oleh=u['id'],created_at=now(),updated_at=now());
 if any(a['kode']==d['kode'] for a in store.assets.values()): raise HTTPException(409,'Kode asset sudah digunakan')
 store.assets[d['id']]=d; audit(u,'asset_create','success','Asset dibuat',d['id']); return d
@app.get('/api/v1/assets/{aid}')
def get_asset(aid:str,_=Depends(auth)):
 a=store.assets.get(aid)
 if not a or a.get('_deleted'): raise HTTPException(404,'Asset tidak ditemukan')
 return {**item(a),'riwayat':store.movements_for(aid)}
@app.put('/api/v1/assets/{aid}')
def update_asset(aid:str,x:AssetIn,u=Depends(auth)):
 a=store.assets.get(aid)
 if not a or a.get('_deleted'): raise HTTPException(404,'Asset tidak ditemukan')
 require_cat(x.kategori_id); d=x.model_dump(); d['kode']=a['kode']; d['updated_at']=now(); store.assets[aid].update(d); audit(u,'asset_update','success','Asset diperbarui',aid); return store.assets[aid]
@app.post('/api/v1/assets/{aid}/foto')
async def photo(aid:str,file:UploadFile=File(...),_=Depends(auth)):
 if aid not in store.assets or store.assets[aid].get('_deleted'): raise HTTPException(404,'Asset tidak ditemukan')
 data=await file.read(); os.makedirs(os.getenv('UPLOAD_DIR','uploads'),exist_ok=True); name=f'{aid}-{uid()}{os.path.splitext(file.filename or "foto.jpg")[1]}'; path=os.path.join(os.getenv('UPLOAD_DIR','uploads'),name)
 with open(path,'wb') as f:f.write(data)
 url=f'/uploads/{name}'; store.assets[aid]['foto'].append(url); return {'foto':url}
@app.delete('/api/v1/assets/{aid}',status_code=204)
def delete_asset(aid:str,u=Depends(admin)):
 if aid not in store.assets or store.assets[aid].get('_deleted'): raise HTTPException(404,'Asset tidak ditemukan')
 store.assets[aid].update(status='nonaktif',_deleted=True,updated_at=now()); audit(u,'asset_delete','success','Asset dihapus',aid)

def movements_for(aid): return [m for m in store.movements if m['asset_id']==aid]
Store.movements_for=movements_for
@app.post('/api/v1/assets/{aid}/mutasi')
def movement(aid:str,x:MovementIn,u=Depends(auth)):
 a=store.assets.get(aid)
 if not a or a.get('_deleted'): raise HTTPException(404,'Asset tidak ditemukan')
 old=a['lokasi']; valid={'masuk_gudang':('luar_gudang','dalam_gudang'),'keluar_gudang':('dalam_gudang','luar_gudang'),'pindah_zona':('dalam_gudang','dalam_gudang')}
 if x.tipe in valid and old['tipe']!=valid[x.tipe][0]: raise HTTPException(400,'Lokasi awal tidak sesuai tipe mutasi')
 if x.tipe=='pindah_zona' and old.get('zona')==x.ke.zona and old.get('rak')==x.ke.rak: raise HTTPException(400,'Zona/rak tujuan harus berbeda')
 if x.jumlah>a['jumlah']: raise HTTPException(400,'Jumlah mutasi melebihi stok asset')
 m={'id':uid('m-'),'asset_id':aid,'tipe':x.tipe,'dari':old,'ke':x.ke.model_dump(),'jumlah':x.jumlah,'keterangan':x.keterangan,'oleh':u['id'],'created_at':now()}; store.movements.append(m); a['lokasi']=x.ke.model_dump(); a['updated_at']=now(); return m
@app.get('/api/v1/assets/{aid}/riwayat')
def history(aid:str,_=Depends(auth)):
 if aid not in store.assets: raise HTTPException(404,'Asset tidak ditemukan')
 return movements_for(aid)

@app.post('/api/v1/assets/{aid}/perubahan', status_code=201)
def request_asset_change(aid:str,x:AssetChangeIn,u=Depends(auth)):
 a=store.assets.get(aid)
 if not a or a.get('_deleted'): raise HTTPException(404,'Asset tidak ditemukan')
 require_cat(x.kategori_id)
 approval={'id':uid('ap-'),'asset_id':aid,'tipe':'perubahan_asset','status':'pending','pic_approver_id':x.pic_id,'pihak_pengaju':u['nama'],'tanda_tangan_pengaju':'','pihak_approver':'','tanda_tangan_approver':'','keterangan':x.alasan_perubahan,'payload':x.model_dump(),'created_at':now(),'updated_at':now()}
 store.approvals.append(approval); return approval

@app.post('/api/v1/assets/{aid}/evidence',status_code=201)
def create_evidence(aid:str,x:EvidenceIn,u=Depends(auth)):
 if aid not in store.assets or store.assets[aid].get('_deleted'): raise HTTPException(404,'Asset tidak ditemukan')
 d=x.model_dump(); d.update(id=uid('ev-'),asset_id=aid,created_at=now(),created_by=u['id'])
 if isinstance(store.mutation_evidence,dict): store.mutation_evidence[d['id']]=d
 else: store.mutation_evidence.append(d)
 audit(u,'evidence_create','success',d['alasan_perubahan'],aid,d['id']); return d
@app.get('/api/v1/assets/{aid}/evidence')
def list_evidence(aid:str,_=Depends(auth)):
 vals=store.mutation_evidence.values() if isinstance(store.mutation_evidence,dict) else store.mutation_evidence
 return [x for x in vals if x.get('asset_id')==aid]
@app.get('/api/v1/audit-logs')
def audit_logs(q:str='',_ = Depends(auth)):
 return [x for x in store.audit_logs if not q or q.lower() in str(x).lower()]
@app.get('/api/v1/approvals')
def approvals(status:Optional[str]=None,_=Depends(auth)):
 return [a for a in store.approvals if not status or a['status']==status]
@app.post('/api/v1/approvals', status_code=201)
def create_approval(x:ApprovalIn,u=Depends(auth)):
 if x.asset_id not in store.assets or store.assets[x.asset_id].get('_deleted'): raise HTTPException(404,'Asset tidak ditemukan')
 d=x.model_dump(); d.update(id=uid('ap-'),dibuat_oleh=u['id'],created_at=now(),updated_at=now()); store.approvals.append(d); audit(u,'approval_create','success','Dokumen approval dibuat',x.asset_id,d['id']); return d
@app.get('/api/v1/approvals/{approval_id}')
def get_approval(approval_id:str,_=Depends(auth)):
 a=next((x for x in store.approvals if x['id']==approval_id),None)
 if not a: raise HTTPException(404,'Approval tidak ditemukan')
 return a
@app.put('/api/v1/approvals/{approval_id}')
def update_approval(approval_id:str,x:ApprovalStatusIn,u=Depends(auth)):
 a=next((v for v in store.approvals if v['id']==approval_id),None)
 if not a: raise HTTPException(404,'Approval tidak ditemukan')
 if x.status=='approved' and (not x.pihak_approver or not x.tanda_tangan_approver): raise HTTPException(400,'Tanda tangan approver wajib untuk approval')
 a.update(x.model_dump(),updated_at=now(),disetujui_oleh=u['id'])
 if a['status']=='approved' and a['tipe']=='perubahan_asset':
  asset=store.assets[a['asset_id']]; payload=a.get('payload',{}); payload.pop('pic_id',None); payload.pop('alasan_perubahan',None); asset.update(payload,updated_at=now())
 return a
@app.get('/api/v1/approvals/{approval_id}/export')
def export_approval(approval_id:str,_=Depends(auth)):
 a=next((x for x in store.approvals if x['id']==approval_id),None)
 if not a: raise HTTPException(404,'Approval tidak ditemukan')
 return {'schema':'asset-gudang.approval.v1','approval':a}

@app.post('/api/v1/approvals/import', status_code=201)
def import_approval(x:dict[str,Any],u=Depends(auth)):
 a=x.get('approval',x)
 required={'asset_id','tipe','status','pic_approver_id','pihak_pengaju','tanda_tangan_pengaju'}
 if not required.issubset(a) or a.get('status') not in {'draft','pending','approved','rejected'}: raise HTTPException(422,'Schema dokumen approval tidak valid')
 if a['asset_id'] not in store.assets: raise HTTPException(422,'Asset pada dokumen tidak ditemukan')
 imported={**a,'id':uid('ap-'),'diimpor_oleh':u['id'],'updated_at':now()}; store.approvals.append(imported); return imported

@app.get('/api/v1/laporan/rekap')
def recap(lokasi_tipe:str=None,kategori_id:str=None,kondisi:str=None, tanggal_awal:str=None,tanggal_akhir:str=None,_=Depends(auth)):
 arr=filtered_assets(kategori_id,kondisi,lokasi_tipe); by={}
 for a in arr: by[a['kategori_id']]=by.get(a['kategori_id'],0)+a['jumlah']
 return {'total_asset':len(arr),'total_unit':sum(a['jumlah'] for a in arr),'per_kategori':[{'kategori_id':k,'jumlah':v} for k,v in by.items()],'items':[item(a) for a in arr]}
@app.get('/api/v1/laporan/rekap/print',response_class=HTMLResponse)
def print_report(lokasi_tipe:str=None,_=Depends(auth)):
 r=recap(lokasi_tipe=lokasi_tipe); rows=''.join(f"<tr><td>{html.escape(a['kode'])}</td><td>{html.escape(a['nama'])}</td><td>{a['jumlah']}</td></tr>" for a in r['items'])
 return f'<html><head><title>Rekap Asset</title></head><body><h1>Rekap Asset Gudang</h1><p>Total unit: {r["total_unit"]}</p><table border="1"><tr><th>Kode</th><th>Nama</th><th>Jumlah</th></tr>{rows}</table></body></html>'
@app.get('/api/v1/laporan/rekap/share-wa')
def share(lokasi_tipe:str=None,_=Depends(auth)):
 r=recap(lokasi_tipe=lokasi_tipe); return {'text':f'Rekap Asset Gudang\nTotal asset: {r["total_asset"]}\nTotal unit: {r["total_unit"]}'}
@app.get('/api/v1/laporan/mutasi')
def movement_report(tanggal_awal:str=None,tanggal_akhir:str=None,_=Depends(auth)): return store.movements
