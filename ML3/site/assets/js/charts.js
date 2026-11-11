/* Dependency-free SVG chart helpers (original implementation). Each chart: tooltips on hover/focus, aria labels, and a 'table view' fallback. */
(function(){
const NS="http://www.w3.org/2000/svg";
const css=n=>getComputedStyle(document.documentElement).getPropertyValue(n).trim();
const el=(t,a={},p)=>{const e=document.createElementNS(NS,t);for(const k in a)e.setAttribute(k,a[k]);if(p)p.appendChild(e);return e};
const fmt=(v,d=2)=>v==null?"–":(+v).toFixed(d);
let tip;function tipEl(){if(!tip){tip=document.createElement("div");tip.className="tip";tip.setAttribute("role","tooltip");document.body.appendChild(tip)}return tip}
function bindTip(node,html){const show=e=>{const t=tipEl();t.innerHTML=html;t.classList.add("on");const r=(e.target.getBoundingClientRect?e.target.getBoundingClientRect():{left:e.clientX,top:e.clientY,width:0,height:0});
  const x=e.clientX!=null&&e.type==="mousemove"?e.clientX+14:r.left+r.width/2, y=e.clientY!=null&&e.type==="mousemove"?e.clientY+14:r.top-10;t.style.left=Math.min(x,innerWidth-300)+"px";t.style.top=Math.max(8,y)+"px"};
  node.setAttribute("data-tip","1");node.addEventListener("mousemove",show);node.addEventListener("mouseenter",show);node.addEventListener("focus",show);
  const hide=()=>tipEl().classList.remove("on");node.addEventListener("mouseleave",hide);node.addEventListener("blur",hide)}
function mount(host,build,tableHtml,aria){host.innerHTML="";const wrap=document.createElement("div");wrap.className="chart";host.appendChild(wrap);const svgHost=document.createElement("div");wrap.appendChild(svgHost);
  const tb=document.createElement("div");tb.hidden=true;tb.className="tablewrap";tb.innerHTML=tableHtml;wrap.appendChild(tb);
  const btn=document.createElement("button");btn.className="btn ghost small";btn.style.marginTop="8px";btn.textContent="View as table";btn.setAttribute("aria-pressed","false");
  btn.onclick=()=>{const on=tb.hidden;tb.hidden=!on;svgHost.hidden=on;btn.textContent=on?"View as chart":"View as table";btn.setAttribute("aria-pressed",on)};wrap.appendChild(btn);
  const draw=()=>{svgHost.innerHTML="";build(svgHost)};host._draw=draw;draw();
  if(!host._ro&&window.ResizeObserver){let w=host.clientWidth;host._ro=new ResizeObserver(()=>{if(Math.abs(host.clientWidth-w)>40){w=host.clientWidth;host._draw()}});host._ro.observe(host)}
  wrap.setAttribute("role","group");wrap.setAttribute("aria-label",aria||"chart")}
const table=(head,rows)=>`<table class="data"><thead><tr>${head.map(h=>`<th>${h}</th>`).join("")}</tr></thead><tbody>${rows.map(r=>`<tr>${r.map(c=>`<td>${c}</td>`).join("")}</tr>`).join("")}</tbody></table>`;
function scaleLin(d0,d1,r0,r1){return v=>r0+(v-d0)/(d1-d0)*(r1-r0)}
const colors=()=>[css("--c1"),css("--c2"),css("--c3"),css("--c4"),css("--c5"),css("--c6")];

/* dumbbell: rows [{label,a,b,aLo,aHi,bLo,bHi,tip}] a = pooled (blue), b = decoupled (orange) */
function dumbbell(host,rows,o={}){const [c1,c2]=[css("--c1"),css("--c2")];const aN=o.aName||"Pooled",bN=o.bName||"Source-decoupled";
 mount(host,s=>{const W=Math.max(520,host.clientWidth),rh=o.rowH||40,L=o.left||210,R=16,T=18,B=34,H=T+rows.length*rh+B;const svg=el("svg",{viewBox:`0 0 ${W} ${H}`,role:"img"},s);
  const x=scaleLin(o.min??0.2,o.max??1.02,L,W-R);for(let t=(o.min??0.2);t<=1.0001;t+=.2){el("line",{x1:x(t),x2:x(t),y1:T-6,y2:H-B,stroke:css("--line")},svg);el("text",{x:x(t),y:H-B+18,"text-anchor":"middle"},svg).textContent=t.toFixed(1)}
  if(o.chance!==false){el("line",{x1:x(1/3),x2:x(1/3),y1:T-6,y2:H-B,class:"chance"},svg);el("text",{x:x(1/3)+4,y:T-8,style:"font-size:10.5px"},svg).textContent="chance 0.33"}
  rows.forEach((r,i)=>{const y=T+i*rh+rh/2;const g=el("g",{},svg);el("text",{x:L-12,y:y+4,"text-anchor":"end",class:"lbl"},g).textContent=r.label;
   el("line",{x1:x(r.b),x2:x(r.a),y1:y,y2:y,stroke:css("--line-2"),"stroke-width":3,"stroke-linecap":"round"},g);
   if(r.bLo!=null)el("line",{x1:x(r.bLo),x2:x(r.bHi),y1:y,y2:y,stroke:c2,"stroke-width":7,opacity:.22,"stroke-linecap":"round"},g);
   const dA=el("circle",{cx:x(r.a),cy:y,r:7,fill:c1,stroke:css("--surface"),"stroke-width":2},g),dB=el("circle",{cx:x(r.b),cy:y,r:7,fill:c2,stroke:css("--surface"),"stroke-width":2},g);
   bindTip(dA,`<b>${r.label}</b><br>${aN}: ${fmt(r.a,3)}`+(r.tip?`<br>${r.tip}`:""));bindTip(dB,`<b>${r.label}</b><br>${bN}: ${fmt(r.b,3)}`+(r.bLo!=null?` (95% CI ${fmt(r.bLo)}–${fmt(r.bHi)})`:"")+(r.tip?`<br>${r.tip}`:""));
   if(o.gapText!==false&&r.gap!=null)el("text",{x:W-R-2,y:y+4,"text-anchor":"end",class:"val"},g).textContent="";});
  svg.setAttribute("aria-label",o.aria||"Pooled versus source-decoupled balanced accuracy")},
  table(["Model",aN,bN,"Gap"],rows.map(r=>[r.label,fmt(r.a,3),fmt(r.b,3)+(r.bLo!=null?` (${fmt(r.bLo)}–${fmt(r.bHi)})`:""),r.gap!=null?fmt(r.gap,2):"–"])),o.aria)}

/* grouped bars: cats [labels], series [{name,color,vals:[{v,lo,hi,tip}]}] */
function groupedBars(host,cats,series,o={}){mount(host,s=>{const W=Math.max(520,host.clientWidth),H=o.h||300,L=46,R=10,T=14,B=62;const svg=el("svg",{viewBox:`0 0 ${W} ${H}`,role:"img"},s);const y=scaleLin(o.min??0,o.max??1,H-B,T);
  for(let t=o.min??0;t<=(o.max??1)+1e-9;t+=o.step||.2){el("line",{x1:L,x2:W-R,y1:y(t),y2:y(t),stroke:css("--line")},svg);el("text",{x:L-8,y:y(t)+4,"text-anchor":"end"},svg).textContent=t.toFixed(1)}
  if(o.chance!==false&&(o.min??0)<1/3){el("line",{x1:L,x2:W-R,y1:y(1/3),y2:y(1/3),class:"chance"},svg)}
  const gw=(W-L-R)/cats.length,bw=Math.min(34,(gw-14)/series.length);cats.forEach((c,i)=>{const cx=L+gw*i+gw/2;const lines=String(c).split("\n");lines.forEach((ln,k)=>el("text",{x:cx,y:H-B+18+k*14,"text-anchor":"middle"},svg).textContent=ln);
   series.forEach((se,j)=>{const d=se.vals[i];if(!d||d.v==null)return;const bx=cx-(series.length*bw)/2+j*bw;const h=Math.max(0,y(o.min??0)-y(d.v));const r=el("rect",{x:bx+1,width:bw-2,y:y(o.min??0),height:0,rx:3,fill:se.color||colors()[j],class:"bar"},svg);
    requestAnimationFrame(()=>requestAnimationFrame(()=>{r.setAttribute("y",y(d.v));r.setAttribute("height",h)}));bindTip(r,`<b>${se.name}</b><br>${c.replace("\n"," ")}: ${fmt(d.v,3)}`+(d.lo!=null?` (95% CI ${fmt(d.lo)}–${fmt(d.hi)})`:"")+(d.tip?`<br>${d.tip}`:""));
    if(d.lo!=null){el("line",{x1:bx+bw/2,x2:bx+bw/2,y1:y(d.lo),y2:y(d.hi),stroke:css("--ink-2"),"stroke-width":1.3},svg);el("line",{x1:bx+bw/2-3,x2:bx+bw/2+3,y1:y(d.hi),y2:y(d.hi),stroke:css("--ink-2")},svg);el("line",{x1:bx+bw/2-3,x2:bx+bw/2+3,y1:y(d.lo),y2:y(d.lo),stroke:css("--ink-2")},svg)}})});
  if(o.yLabel){const t=el("text",{x:14,y:H/2-20,transform:`rotate(-90 14 ${H/2-20})`,"text-anchor":"middle"},svg);t.textContent=o.yLabel}},
 table(["Group",...series.map(s=>s.name)],cats.map((c,i)=>[String(c).replace("\n"," "),...series.map(s=>s.vals[i]&&s.vals[i].v!=null?fmt(s.vals[i].v,3):"n/a")])),o.aria||"grouped bar chart");
 const lg=document.createElement("div");lg.className="legend";lg.innerHTML=series.map((s,j)=>`<span><i style="background:${s.color||colors()[j]}"></i>${s.name}</span>`).join("");host.insertBefore(lg,host.firstChild)}

/* lines: series [{name,color,x:[],y:[]}] */
function lines(host,series,o={}){mount(host,s=>{const W=Math.max(520,host.clientWidth),H=o.h||300,L=48,R=14,T=14,B=44;const svg=el("svg",{viewBox:`0 0 ${W} ${H}`,role:"img"},s);const x=scaleLin(0,1,L,W-R),y=scaleLin(0,1,H-B,T);
  for(let t=0;t<=1.0001;t+=.2){el("line",{x1:L,x2:W-R,y1:y(t),y2:y(t),stroke:css("--line")},svg);el("text",{x:L-8,y:y(t)+4,"text-anchor":"end"},svg).textContent=t.toFixed(1);el("text",{x:x(t),y:H-B+18,"text-anchor":"middle"},svg).textContent=t.toFixed(1)}
  el("text",{x:(L+W-R)/2,y:H-6,"text-anchor":"middle"},svg).textContent=o.xLabel||"";el("text",{x:14,y:H/2-20,transform:`rotate(-90 14 ${H/2-20})`,"text-anchor":"middle"},svg).textContent=o.yLabel||"";
  series.forEach((se,j)=>{const col=se.color||colors()[j];const d=se.x.map((xx,k)=>(k?"L":"M")+x(xx)+" "+y(se.y[k])).join(" ");const p=el("path",{d,fill:"none",stroke:col,"stroke-width":2.6,"stroke-linejoin":"round","stroke-linecap":"round"},svg);
   const len=p.getTotalLength?p.getTotalLength():600;p.style.strokeDasharray=len;p.style.strokeDashoffset=len;p.style.transition="stroke-dashoffset 1.1s ease";requestAnimationFrame(()=>requestAnimationFrame(()=>p.style.strokeDashoffset=0));
   se.x.forEach((xx,k)=>{const c=el("circle",{cx:x(xx),cy:y(se.y[k]),r:6,fill:"transparent"},svg);bindTip(c,`<b>${se.name}</b><br>coverage ${xx.toFixed(2)}: accuracy ${se.y[k].toFixed(3)}`)})})},
 table(["Coverage",...series.map(s=>s.name)],series[0].x.map((xx,k)=>[xx.toFixed(2),...series.map(s=>s.y[k].toFixed(3))])),o.aria||"line chart");
 const lg=document.createElement("div");lg.className="legend";lg.innerHTML=series.map((s,j)=>`<span><i style="background:${s.color||colors()[j]}"></i>${s.name}</span>`).join("");host.insertBefore(lg,host.firstChild)}

/* heat: m [[v]], rows, cols; opts: fmt, scale 'blue'|'diverge', min,max, norm:'row' */
function heat(host,m,rowL,colL,o={}){mount(host,s=>{const cw=o.cw||78,ch=o.ch||46,L=o.left||120,T=o.top||40,W=L+cw*colL.length+10,H=T+ch*rowL.length+8;const svg=el("svg",{viewBox:`0 0 ${W} ${H}`,role:"img",style:`max-width:${W*1.4}px`},s);
  colL.forEach((c,j)=>{el("text",{x:L+cw*j+cw/2,y:T-14,"text-anchor":"middle"},svg).textContent=c});
  const base=o.color||css("--c1");m.forEach((row,i)=>{el("text",{x:L-10,y:T+ch*i+ch/2+4,"text-anchor":"end",class:"lbl"},svg).textContent=rowL[i];const tot=row.reduce((a,b)=>a+b,0)||1;
   row.forEach((v,j)=>{const t=o.norm==="row"?v/tot:(v-(o.min??0))/((o.max??1)-(o.min??0));const r=el("rect",{x:L+cw*j+2,y:T+ch*i+2,width:cw-4,height:ch-4,rx:8,fill:base,"fill-opacity":Math.max(.05,Math.min(1,t)),stroke:css("--line")},svg);
    const tx=el("text",{x:L+cw*j+cw/2,y:T+ch*i+ch/2+4,"text-anchor":"middle",class:"val",style:`fill:${t>.55?"#fff":css("--ink")}`},svg);tx.textContent=o.fmt?o.fmt(v,t):fmt(v,2);bindTip(r,`<b>${rowL[i]} → ${colL[j]}</b><br>${o.fmt?o.fmt(v,t):fmt(v,3)}`+(o.tipExtra?o.tipExtra(i,j):""))})})},
 table(["",...colL],m.map((r,i)=>[rowL[i],...r.map(v=>o.fmt?o.fmt(v,0):fmt(v,3))])),o.aria||"heat map")}

/* stacked horizontal bars: rows [{label,parts:[{name,v,color}]}] */
function stacked(host,rows,o={}){mount(host,s=>{const W=Math.max(520,host.clientWidth),rh=44,L=200,R=60,T=10,B=26,H=T+rows.length*rh+B;const svg=el("svg",{viewBox:`0 0 ${W} ${H}`,role:"img"},s);const mx=Math.max(...rows.map(r=>r.parts.reduce((a,p)=>a+p.v,0)));const x=scaleLin(0,mx*1.04,L,W-R);
  rows.forEach((r,i)=>{const y=T+i*rh;el("text",{x:L-10,y:y+rh/2+4,"text-anchor":"end",class:"lbl"},svg).textContent=r.label;let acc=0;r.parts.forEach(p=>{if(!p.v)return;const rc=el("rect",{x:x(acc),y:y+8,width:0,height:rh-18,rx:4,fill:p.color,stroke:css("--surface"),"stroke-width":2,class:"bar"},svg);
    const w=x(acc+p.v)-x(acc);requestAnimationFrame(()=>requestAnimationFrame(()=>rc.setAttribute("width",Math.max(0,w-1))));bindTip(rc,`<b>${r.label}</b><br>${p.name}: ${p.v}`);acc+=p.v});el("text",{x:x(acc)+8,y:y+rh/2+4,class:"val"},svg).textContent=acc});
  [0,500,1000,1500].filter(t=>t<=mx*1.04).forEach(t=>el("text",{x:x(t),y:H-6,"text-anchor":"middle"},svg).textContent=t)},
 table(["Source",...rows[0].parts.map(p=>p.name),"Total"],rows.map(r=>[r.label,...r.parts.map(p=>p.v),r.parts.reduce((a,p)=>a+p.v,0)])),o.aria||"stacked bar chart");
 const lg=document.createElement("div");lg.className="legend";lg.innerHTML=rows[0].parts.map(p=>`<span><i style="background:${p.color}"></i>${p.name}</span>`).join("");host.insertBefore(lg,host.firstChild)}

window.Charts={dumbbell,groupedBars,lines,heat,stacked,colors,fmt};
})();
