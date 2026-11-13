const fs=require('fs'),vm=require('vm');
const js=fs.readFileSync(__dirname+'/../index.html','utf8').match(/<script>([\s\S]*?)<\/script>/)[1];
const cache={};
function mk(id){
  const e={id,_attrs:{},children:[],dataset:{},style:{},value:'',textContent:'',innerHTML:'',
    setAttribute(k,v){this._attrs[k]=v},getAttribute(k){return this._attrs[k]},
    addEventListener(k,fn){(this._ev=this._ev||{})[k]=fn},
    querySelectorAll(){return []}};
  return e;
}
const langBtns=[{dataset:{lang:'zh'},setAttribute(){},addEventListener(k,fn){this.click=fn}},{dataset:{lang:'en'},setAttribute(){},addEventListener(k,fn){this.click=fn}}];
const i18nNodes=[];
const document={
  documentElement:{},addEventListener(){},activeElement:null,title:'',
  getElementById(id){return cache[id]||(cache[id]=mk(id))},
  querySelectorAll(sel){
    if(sel==='.lang button')return langBtns;
    return [];
  }
};
let rafCb=null;
const ctx={document,window:{},performance:{now:()=>0},requestAnimationFrame:cb=>{rafCb=cb},
  localStorage:{getItem:()=>null,setItem(){}},Intl,Date,Math,console,String,Number,Array,parseFloat,isFinite,Object};
vm.createContext(ctx);
vm.runInContext(js+';globalThis.__st=st;globalThis.__render=render;globalThis.__langBtns=null;',ctx);
const out=(id)=>cache[id].textContent;
for(const L of ['zh','en']){
  langBtns.find(b=>b.dataset.lang===L).click();
  ctx.__st.utc=Date.UTC(2026,10,11,6,0,0);
  ctx.__render(1000);
  console.log('---',L);
  for(const k of ['rd1-date','rd1-doy','rd1-sign','rd1-dev','rd2-age','rd2-phase','rd2-nFull','rd3-asc','rd3-mc','rd3-rs']) console.log(k,'=',out(k));
}
// polar + custom lat checks
ctx.__st.lat=78;ctx.__st.utc=Date.UTC(2026,5,21,12,0,0);ctx.__render(5000);console.log('polar',out('rd3-rs'));
ctx.__st.utc=Date.UTC(2026,11,21,12,0,0);ctx.__render(9000);console.log('polar winter',out('rd3-rs'));
console.log('ecStatic has text:',/class="zn"/.test(cache['ecStatic'].innerHTML),'; months en sample:',(cache['ecStatic'].innerHTML.match(/>(Nov|11月)</)||[])[1]);
// seasons: north vs south, both languages
for(const [L,lat] of [['zh',39.9],['en',39.9],['zh',-33.9],['en',-33.9]]){
  langBtns.find(b=>b.dataset.lang===L).click();
  ctx.__st.lat=lat;ctx.__st.utc=Date.UTC(2026,10,11,6,0,0);ctx.__render(20000+lat);
  const ss=cache['ecStatic'].innerHTML;
  const names=[...ss.matchAll(/class="sname"[^>]*>([^<]+)</g)].map(m=>m[1]).join('/');
  const dates=[...ss.matchAll(/class="sdate"[^>]*>([^<]+)</g)].map(m=>m[1]).join(' | ');
  console.log(L,lat,'|',names,'|',cache['rd1-season'].textContent,'|',cache['rd1-next'].textContent);
  if(L==='zh'&&lat>0)console.log('   dates:',dates);
}
// saturn rows
for(const L of ['zh','en']){
  langBtns.find(b=>b.dataset.lang===L).click();
  ctx.__st.lat=39.9;ctx.__st.utc=Date.UTC(2026,10,11,12,0,0);ctx.__render(40000);
  console.log(L,'saturn:',['rd3-sat','rd3-satpos','rd3-satalt','rd3-satd'].map(k=>cache[k].textContent).join(' | '),'| icon:',cache['satIcon']._attrs.transform);
}
