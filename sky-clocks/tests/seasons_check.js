const fs=require('fs');
const html=fs.readFileSync(__dirname+'/../index.html','utf8');
const m=html.match(/\/\*MATH-START\*\/([\s\S]*?)\/\*MATH-END\*\//)[1];
const M=new Function(m+';return {jdOf,findSunLon};')();
const iso=jd=>new Date((jd-2440587.5)*86400000).toISOString().slice(0,16)+'Z';
const JDa=M.jdOf(Date.UTC(2026,0,1)),JDb=M.jdOf(Date.UTC(2027,0,1));
const T=[0,90,180,270].map(t=>M.findSunLon(JDa,t));T.push(M.findSunLon(JDb,0));
console.log('2026 terms:',T.map(iso).join('  '));
console.log('season lengths (d):',[0,1,2,3].map(i=>(T[i+1]-T[i]).toFixed(2)).join('  '),' sum',(T[4]-T[0]).toFixed(3));
