/* Home hero: (1) quiet particle field (2D canvas, pauses off-screen, static under reduced motion), (2) specimen frame cycling real held-out samples with the study checkpoints' real outputs. */
(function(){
const $=(s,r=document)=>r.querySelector(s),reduced=matchMedia("(prefers-reduced-motion: reduce)").matches;
/* particles */
const cv=$("#fx");
if(cv){const ctx=cv.getContext("2d");let W,H,P=[],mouse={x:-999,y:-999},run=true,raf,dpr=Math.min(2,devicePixelRatio||1);
 const col=()=>getComputedStyle(document.documentElement).getPropertyValue("--accent").trim()||"#8CF0D2";let C=col();
 function size(){const r=cv.getBoundingClientRect();W=r.width;H=r.height;cv.width=W*dpr;cv.height=H*dpr;ctx.setTransform(dpr,0,0,dpr,0,0);const n=Math.min(95,Math.floor(W*H/(innerWidth<700?22000:15000)));P=Array.from({length:n},()=>({x:Math.random()*W,y:Math.random()*H,vx:(Math.random()-.5)*.22,vy:(Math.random()-.5)*.22,r:Math.random()*1.2+.4}));draw(true)}
 function draw(still){ctx.clearRect(0,0,W,H);ctx.fillStyle=C;ctx.strokeStyle=C;
  for(let i=0;i<P.length;i++){const p=P[i];if(!still){p.x+=p.vx;p.y+=p.vy;if(p.x<0||p.x>W)p.vx*=-1;if(p.y<0||p.y>H)p.vy*=-1;const dx=p.x-mouse.x,dy=p.y-mouse.y,d=dx*dx+dy*dy;if(d<14000){const f=(1-d/14000)*.9;p.x+=dx*.02*f*4;p.y+=dy*.02*f*4}}
   ctx.globalAlpha=.55;ctx.beginPath();ctx.arc(p.x,p.y,p.r,0,6.283);ctx.fill();
   for(let j=i+1;j<P.length;j++){const q=P[j],dx=p.x-q.x,dy=p.y-q.y,d=dx*dx+dy*dy;if(d<12000){ctx.globalAlpha=(1-d/12000)*.16;ctx.lineWidth=.6;ctx.beginPath();ctx.moveTo(p.x,p.y);ctx.lineTo(q.x,q.y);ctx.stroke()}}}
  ctx.globalAlpha=1}
 function loop(){if(!run)return;draw(false);raf=requestAnimationFrame(loop)}
 size();addEventListener("resize",()=>{clearTimeout(size.t);size.t=setTimeout(size,200)});
 const hero=cv.parentElement;hero.addEventListener("pointermove",e=>{const r=cv.getBoundingClientRect();mouse.x=e.clientX-r.left;mouse.y=e.clientY-r.top},{passive:true});hero.addEventListener("pointerleave",()=>{mouse.x=mouse.y=-999});
 new MutationObserver(()=>{C=col()}).observe(document.documentElement,{attributes:true,attributeFilter:["data-theme"]});
 if(!reduced&&"IntersectionObserver" in window)new IntersectionObserver(es=>{const v=es[0].isIntersecting;if(v&&!run){run=true;loop()}else if(!v){run=false;cancelAnimationFrame(raf)}}).observe(hero);
 if(!reduced)loop()}
/* specimen frame */
const fr=$("#frame");
if(fr)fetch("data/hero.json").then(r=>r.json()).then(S=>{
 const ids=["sample2","sample5","sample8"],list=ids.map(i=>S.find(s=>s.id===i)).filter(Boolean);if(!list.length)return;
 const imgs=list.map(s=>{const i=document.createElement("img");i.src=s.file;i.alt=`Held-out radiograph, recorded label ${s.true_label}`;i.decoding="async";fr.insertBefore(i,fr.querySelector(".scanline"));return i});
 const meta=$(".meta",fr),nm={pooled:"Pooled model",no_fracatlas:"Trained without FracAtlas",no_hip_implants:"Without hip-implant source",no_shoulder_implants:"Without shoulder-implant source"};
 let k=-1;
 function show(){const prev=k;k=(k+1)%list.length;const s=list[k],p=s.models[0].pred;
  meta.innerHTML=`<div class="row"><span>Recorded label</span><b>${s.true_label}${s.true_label==="Knee"?" (provisional)":""}</b></div>`+s.models.map(m=>`<div class="row${m.pred!==p?" dis":""}"><span>${nm[m.id]||m.name}</span><b>${m.pred} ${(m.confidence*100).toFixed(0)}%</b></div>`).join("");
  if(window.gsap&&!reduced){if(prev>=0)gsap.to(imgs[prev],{opacity:0,duration:.9,onComplete:()=>imgs[prev].classList.remove("on")});imgs[k].classList.add("on");gsap.fromTo(imgs[k],{opacity:0,scale:1.08},{opacity:1,scale:1,duration:1.6,ease:"power3.out"});gsap.from(meta.children,{opacity:0,y:10,stagger:.07,duration:.7,delay:.3})}
  else{imgs.forEach((im,i)=>{im.classList.toggle("on",i===k);im.style.opacity=i===k?1:0;im.style.transform="none"})}}
 show();if(!reduced)setInterval(show,6200)});
})();
