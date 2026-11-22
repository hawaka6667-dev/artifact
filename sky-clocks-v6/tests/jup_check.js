const fs=require('fs');
const html=fs.readFileSync(__dirname+'/../index.html','utf8');
const m=html.match(/\/\*MATH-START\*\/([\s\S]*?)\/\*MATH-END\*\//)[1];
const M=new Function(m+';return {norm,jdOf,sunLon,jupiterPos};')();
const iso=jd=>new Date((jd-2440587.5)*86400000).toISOString().slice(0,16)+'Z';
const el=jd=>M.norm(M.jupiterPos(jd).lon-M.sunLon(jd).lon);
function opp(g){let jd=M.jdOf(Date.parse(g));for(let i=0;i<30;i++){const d=((el(jd)-180+540)%360)-180;jd+=d/0.92;}return jd;}
console.log('opposition 2024-12-07 expected ->',iso(opp('2024-12-04T00:00:00Z')));
console.log('opposition 2026-01-10 expected ->',iso(opp('2026-01-07T00:00:00Z')));
console.log('opposition 2027-02-10 expected ->',iso(opp('2027-02-07T00:00:00Z')));
const j=M.jupiterPos(2451545);console.log('J2000 geocentric lon (want ~25.2):',j.lon.toFixed(2),'dist',j.dist.toFixed(2),'AU');
