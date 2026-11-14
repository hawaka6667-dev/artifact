const fs=require('fs');
const html=fs.readFileSync(__dirname+'/../index.html','utf8');
const m=html.match(/\/\*MATH-START\*\/([\s\S]*?)\/\*MATH-END\*\//)[1];
const M=new Function(m+';return {norm,jdOf,sunLon,saturnPos,elong};')();
const iso=jd=>new Date((jd-2440587.5)*86400000).toISOString().slice(0,16)+'Z';
const el=jd=>M.norm(M.saturnPos(jd).lon-M.sunLon(jd).lon);
// find opposition (elongation = 180) near a guess date
function opp(guessISO){
  let jd=M.jdOf(Date.parse(guessISO));
  for(let i=0;i<30;i++){const d=((el(jd)-180+540)%360)-180;jd+=d/1.04; }
  return jd;
}
console.log('opposition 2025-09-21 expected ->',iso(opp('2025-09-18T00:00:00Z')));
console.log('opposition 2026-10-04 expected ->',iso(opp('2026-10-01T00:00:00Z')));
console.log('opposition 2027-10-18 expected ->',iso(opp('2027-10-15T00:00:00Z')));
const j2=M.saturnPos(2451545);
console.log('J2000 geocentric lon (want ~40.4):',j2.lon.toFixed(2),' dist',j2.dist.toFixed(2),'AU');
const n=M.saturnPos(M.jdOf(Date.parse('2026-11-11T06:00:00Z')));
console.log('2026-11-11 Saturn lon/lat/dist:',n.lon.toFixed(2),n.lat.toFixed(2),n.dist.toFixed(2));
const d=((M.saturnPos(M.jdOf(Date.parse('2026-11-11T18:00:00Z'))).lon-M.saturnPos(M.jdOf(Date.parse('2026-11-10T18:00:00Z'))).lon+540)%360)-180;
console.log('daily motion (deg/day, negative = retrograde):',d.toFixed(3));
