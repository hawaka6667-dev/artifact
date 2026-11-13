const fs=require('fs');
const dir=__dirname+'/../';
const html=fs.readFileSync(dir+'index.html','utf8');
const m=html.match(/\/\*MATH-START\*\/([\s\S]*?)\/\*MATH-END\*\//)[1];
const M=new Function(m+';return {norm,sin,cos,jdOf,sunLon,moonPos,eclToEq,angles,altOf,elong,nextPhase,R2D,D2R};')();
const {norm,sin,cos,jdOf,sunLon,moonPos,eclToEq,angles,altOf,elong,nextPhase,R2D,D2R}=M;
const U=s=>Date.parse(s);
const sl=s=>sunLon(jdOf(U(s))).lon;
console.log('equinox 2026-03-20 14:46Z sun lon (want ~0):',(((sl('2026-03-20T14:46:00Z')+180)%360)-180).toFixed(3));
console.log('solstice 2026-06-21 08:24Z sun lon (want ~90):',sl('2026-06-21T08:24:00Z').toFixed(3));
console.log('solstice 2026-12-21 20:50Z sun lon (want ~270):',sl('2026-12-21T20:50:00Z').toFixed(3));
const e=elong(jdOf(U('2026-08-12T17:46:00Z')));
console.log('eclipse 2026-08-12 17:46Z elongation (want ~0):',(((e+180)%360)-180).toFixed(3));
const nn=nextPhase(jdOf(U('2026-11-11T00:00:00Z')),180);
console.log('next full moon after 2026-11-11:',new Date((nn-2440587.5)*86400000).toISOString());
const nm=nextPhase(jdOf(U('2026-11-11T00:00:00Z')),0);
console.log('next new moon after 2026-11-11:',new Date((nm-2440587.5)*86400000).toISOString());
// ascendant: ecliptic point with alt=0 and H<0 (rising)
let worst=0;
for(const lat of [0,23,40,51.5,-34,60]){
  for(let LST=0;LST<360;LST+=17){
    const eps=23.44,{asc}=angles(LST,lat,eps);
    const q=eclToEq(asc,0,eps),H=norm(LST-q.ra);
    const alt=altOf(q.dec,H,lat);
    const rising=H>180; // east side
    if(Math.abs(alt)>1e-6||!rising){console.log('ASC FAIL',lat,LST,alt.toFixed(4),H.toFixed(1));worst++;}
  }
}
console.log('asc failures:',worst);
// eccentric model vs true longitude at k=1
function eccModel(JD,k){
  const s=sunLon(JD),Rc=150,d=0.03342*k*Rc,pa=102.93-270;
  const C=[d*sin(pa),-d*cos(pa)],phm=s.L-270;
  const S=[C[0]+Rc*sin(phm),C[1]-Rc*cos(phm)];
  return norm(Math.atan2(S[0],-S[1])*R2D+270);
}
let maxe=0;
for(let i=0;i<365;i+=5){
  const JD=jdOf(U('2026-01-01T00:00:00Z'))+i,s=sunLon(JD);
  const dv=((eccModel(JD,1)-s.lon+540)%360)-180;
  maxe=Math.max(maxe,Math.abs(dv));
}
console.log('eccentric k=1 max deviation (deg):',maxe.toFixed(3));
