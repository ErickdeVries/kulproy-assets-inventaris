const { test } = require('node:test');
const assert = require('node:assert/strict');
const http = require('node:http');
const ts = require('typescript');
require.extensions['.ts'] = (module, filename) => module._compile(ts.transpileModule(require('node:fs').readFileSync(filename,'utf8'), {compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2022}}).outputText, filename);
const { normalizeUrl, Client, assetPayload } = require('../src/client.ts');
const memory = () => { const values = new Map(); return {values, getItemAsync:async k=>values.get(k)||null,setItemAsync:async(k,v)=>values.set(k,v),deleteItemAsync:async k=>values.delete(k)}; };
test('safe URL requires exact API prefix and rejects secrets and unsafe URLs', () => {
 assert.equal(normalizeUrl(' https://example.test/api/v1/// '),'https://example.test/api/v1');
 for(const u of ['https://x','https://u:p@x/api/v1','ftp://x/api/v1','https://x/api/v1?q=1','https://x/api/v1#x','bad']) assert.throws(()=>normalizeUrl(u));
});
test('asset payload validates categories, integers, raw enums and nested location', () => {
 const form={nama:' Bor ',kategori_id:'cat',jumlah:'2',satuan:'unit',kondisi:'baik',tipe:'dalam_gudang',zona:'A',rak:'1',catatan:'',keterangan:'',kode:''};
 assert.deepEqual(assetPayload(form,[{id:'cat'}]),{nama:'Bor',kategori_id:'cat',jumlah:2,satuan:'unit',kondisi:'baik',lokasi:{tipe:'dalam_gudang',zona:'A',rak:'1',catatan:''},keterangan:'',foto:[]});
 for (const change of [{jumlah:'0'},{jumlah:'1.5'},{jumlah:'abc'},{kategori_id:'fake'},{kondisi:'Bagus'},{tipe:'gudang'},{nama:' '}]) assert.throws(()=>assetPayload({...form,...change},[{id:'cat'}]));
});
test('real HTTP transport: login, SecureStore restore, reports, list/detail/create, password, 401 and logout', async t => {
 const requests=[]; let expired=false;
 const server=http.createServer(async(req,res)=>{let raw='';for await(const c of req)raw+=c; const body=raw?JSON.parse(raw):null; requests.push({url:req.url,method:req.method,body,auth:req.headers.authorization}); res.setHeader('Content-Type','application/json');
 if(req.url==='/api/v1/auth/login') return res.end(JSON.stringify({access_token:'test-only-session',user:{id:'u',nama:'User',username:'user',role:'non_admin'}}));
 if(req.headers.authorization!=='Bearer test-only-session'||expired){res.statusCode=401;return res.end(JSON.stringify({detail:'Token tidak valid'}));}
 if(req.url==='/api/v1/auth/me') return res.end(JSON.stringify({id:'u',nama:'User',username:'user',role:'non_admin'}));
 if(req.url==='/api/v1/laporan/rekap') return res.end(JSON.stringify({total_asset:1,total_unit:2,per_kategori:[],items:[]}));
 if(req.url==='/api/v1/categories') return res.end(JSON.stringify([{id:'cat',nama:'Alat'}]));
 if(req.url.startsWith('/api/v1/assets?'))return res.end(JSON.stringify({items:[{id:'a',nama:'Bor'}],page:1,total:1,limit:20}));
 if(req.url==='/api/v1/assets/a')return res.end(JSON.stringify({id:'a',nama:'Bor',riwayat:[]}));
 if(req.url==='/api/v1/assets'&&req.method==='POST'){res.statusCode=201;return res.end(JSON.stringify({...body,id:'new'}));}
 if(req.url==='/api/v1/auth/change-password')return res.end(JSON.stringify({status:'ok'}));
 res.statusCode=404;res.end(JSON.stringify({detail:'Not Found'})); });
 await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve)); t.after(()=>server.close());
 const store=memory(), base=`http://127.0.0.1:${server.address().port}/api/v1`; let resets=0;
 const client=new Client(store,()=>resets++); await client.connect(base); await client.login('user','not-persisted');
 assert.equal(client.user.nama,'User'); assert.ok(!JSON.stringify([...store.values]).includes('not-persisted'));
 const restored=new Client(store,()=>resets++); assert.equal(await restored.restore(),true); assert.equal(restored.baseUrl,base);
 assert.equal((await restored.report()).total_unit,2); assert.equal((await restored.categories())[0].id,'cat');
 assert.equal((await restored.assets('Bor & alat',1)).items[0].id,'a'); assert.equal((await restored.asset('a')).nama,'Bor');
 const payload={nama:'Bor',kategori_id:'cat',jumlah:2,kondisi:'baik',satuan:'unit',lokasi:{tipe:'dalam_gudang',zona:'',rak:'',catatan:''},foto:[],keterangan:''};
 assert.equal((await restored.createAsset(payload)).id,'new'); await restored.changePassword('old-secret','new-secret');
 assert.deepEqual(requests.find(r=>r.url==='/api/v1/assets'&&r.method==='POST').body,payload);
 assert.match(requests.find(r=>r.url.startsWith('/api/v1/assets?')).url,/q=Bor/);
 assert.deepEqual(requests.find(r=>r.url.endsWith('change-password')).body,{current_password:'old-secret',new_password:'new-secret'});
 expired=true; await assert.rejects(()=>restored.report(),/Sesi/); assert.equal(restored.user,null); assert.equal(resets,1);
 assert.ok(!JSON.stringify([...store.values]).includes('test-only-session')); await client.logout(); assert.equal(client.user,null);
});
test('failed restore preserves secure session for network retry and handles malformed storage',async()=>{
 const store=memory();await store.setItemAsync('asset-gudang.session',JSON.stringify({baseUrl:'http://127.0.0.1:1/api/v1',token:'test'}));
 const client=new Client(store,()=>{});await assert.rejects(()=>client.restore(),/server|jaringan/i);assert.ok(store.values.has('asset-gudang.session'));
 await store.setItemAsync('asset-gudang.session','not json');assert.equal(await client.restore(),false);
});
