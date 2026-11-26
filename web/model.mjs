export function filterRecords(records,{query='',group='',maker='',from=null,to=null,saved=null,sort='oldest'}={}){
 const terms=query.toLocaleLowerCase().trim().split(/\s+/).filter(Boolean);
 return records.filter(r=>{const text=[r.title,r.description,...r.terms,...r.makers,...r.materials,...r.places].join(' ').toLocaleLowerCase();const lo=r.start??r.end,hi=r.end??r.start;return terms.every(t=>text.includes(t))&&(!group||r.groups.includes(group))&&(!maker||r.makers.includes(maker))&&(!saved||saved.has(r.id))&&(from===null||hi!==null&&hi>=from)&&(to===null||lo!==null&&lo<=to);}).sort((a,b)=>sort==='title'?a.title.localeCompare(b.title):(a.start===null&&b.start===null?0:a.start===null?1:b.start===null?-1:(a.start-b.start)*(sort==='newest'?-1:1))||a.title.localeCompare(b.title));
}
export function printDate(r){return r.date||'Date not recorded';}
export function compareYears(a,b){if(a.start===null||b.start===null)return null;return Math.abs(a.start-b.start);}
export function csv(records){const cell=v=>'"'+String(v??'').replace(/^[\s]*[=+@-]/,"'$&").replaceAll('"','""')+'"';const fields=['title','date','makers','places','materials','source'];return [fields,...records.map(r=>fields.map(k=>Array.isArray(r[k])?r[k].join('; '):r[k]))].map(row=>row.map(cell).join(',')).join('\r\n');}
export function loadSaved(value,known){try{const ids=JSON.parse(value);return new Set(Array.isArray(ids)?ids.filter(id=>known.has(id)).slice(0,2000):[]);}catch{return new Set();}}
export function safeExternal(url){try{const u=new URL(url);return u.protocol==='https:'&&!u.username&&!u.password?u.href:'';}catch{return '';}}
