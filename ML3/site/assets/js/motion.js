/* Motion layer: Lenis smooth scroll, GSAP + ScrollTrigger, split-text reveals, parallax, magnetic buttons, page curtain, pinned "two ways of testing" scene.
   Everything degrades: no JS libs -> static page; prefers-reduced-motion -> no smooth scroll, no pin, no curtain, final states shown. */
(function(){
const root=document.documentElement,$=(s,r=document)=>r.querySelector(s),$$=(s,r=document)=>[...r.querySelectorAll(s)];
const reduced=matchMedia("(prefers-reduced-motion: reduce)").matches,fine=matchMedia("(hover: hover) and (pointer: fine)").matches;
const failsafe=()=>{root.classList.remove("is-entering");$$("[data-split]").forEach(e=>e.classList.add("is-split"))};
setTimeout(()=>root.classList.remove("is-entering"),4500);
if(!window.gsap||!window.ScrollTrigger){failsafe();return}
gsap.registerPlugin(ScrollTrigger);
const curtain=$(".curtain");let lenis=null;
/* ---------- smooth scroll ---------- */
if(!reduced&&window.Lenis){lenis=new Lenis({lerp:.09,smoothWheel:true,wheelMultiplier:.95});lenis.on("scroll",ScrollTrigger.update);gsap.ticker.add(t=>lenis.raf(t*1000));gsap.ticker.lagSmoothing(0);window.lenis=lenis;
 $$(".tablewrap,.chart table").forEach(e=>e.setAttribute("data-lenis-prevent",""));
 document.addEventListener("click",e=>{const a=e.target.closest('a[href^="#"]');if(!a||a.getAttribute("href")==="#")return;const t=$(a.getAttribute("href"));if(t){e.preventDefault();lenis.scrollTo(t,{offset:-80,duration:1.4})}})}
/* progress bar */
const pb=$(".progress");if(pb&&!reduced)gsap.to(pb,{scaleX:1,ease:"none",scrollTrigger:{start:0,end:"max",scrub:.3}});
/* ---------- split text ---------- */
function split(el){const walk=n=>[...n.childNodes].forEach(c=>{if(c.nodeType===3){const f=document.createDocumentFragment();c.textContent.split(/(\s+)/).forEach(t=>{if(!t)return;if(/^\s+$/.test(t)){f.appendChild(document.createTextNode(" "));return}const w=document.createElement("span"),i=document.createElement("span");w.className="w";i.className="wi";i.textContent=t;w.appendChild(i);f.appendChild(w)});c.replaceWith(f)}else if(c.nodeType===1)walk(c)});walk(el);el.classList.add("is-split");return $$(".wi",el)}
const splits=$$("[data-split]").map(el=>({el,words:split(el)}));
if(!reduced)splits.forEach(s=>gsap.set(s.words,{yPercent:118}));
function playSplit(s,delay=0){if(reduced)return;gsap.to(s.words,{yPercent:0,duration:1.15,ease:"expo.out",stagger:.05,delay})}
/* ---------- intro / curtain ---------- */
function intro(){
 const heroSplit=splits.filter(s=>s.el.closest(".hero,.phead,.experience-hero,.studio-hero"));
 heroSplit.forEach((s,i)=>playSplit(s,.1+i*.15));
 splits.filter(s=>!heroSplit.includes(s)).forEach(s=>ScrollTrigger.create({trigger:s.el,start:"top 88%",once:true,onEnter:()=>playSplit(s)}));
 const introTargets=$$(".hero .lead, .phead .lead, .hero .cta-row, .hero .frame, .hero .eyebrow, .phead .eyebrow");
 if(!reduced&&introTargets.length){gsap.from(introTargets,{opacity:0,y:28,duration:1.2,ease:"expo.out",stagger:.1,delay:.35,clearProps:"all"})}
 window.dispatchEvent(new Event("sl:intro"))}
function enter(){
 if(curtain&&root.classList.contains("is-entering")&&!reduced){const svg=$("svg,img",curtain);gsap.timeline({onComplete:()=>{root.classList.remove("is-entering");gsap.set(curtain,{yPercent:101,clearProps:"transform"})}}).to(svg,{opacity:0,duration:.25,delay:.15}).to(curtain,{yPercent:-101,duration:.75,ease:"expo.inOut"},"-=.05").add(intro,"-=.45")}
 else{root.classList.remove("is-entering");intro()}}
(document.fonts&&document.fonts.ready?Promise.race([document.fonts.ready,new Promise(r=>setTimeout(r,900))]):Promise.resolve()).then(enter);
window.addEventListener("pageshow",e=>{if(e.persisted&&curtain){root.classList.remove("is-entering");gsap.set(curtain,{yPercent:101})}});
/* leave transition */
if(curtain&&!reduced)document.addEventListener("click",e=>{const a=e.target.closest("a[href]");if(!a||e.defaultPrevented||e.button||e.metaKey||e.ctrlKey||e.shiftKey||e.altKey||a.target||a.hasAttribute("download"))return;
 const u=new URL(a.href,location.href);if(u.origin!==location.origin||!/(\.html|\/)$/.test(u.pathname)||(u.pathname===location.pathname&&u.search===location.search))return;
 e.preventDefault();lenis&&lenis.stop();gsap.set(curtain,{yPercent:101});gsap.to($("svg,img",curtain),{opacity:1,duration:.25,delay:.25});gsap.to(curtain,{yPercent:0,duration:.6,ease:"expo.inOut",onComplete:()=>{location.href=u.href}})});
/* ---------- generic scroll effects ---------- */
if(!reduced){
 $$("[data-parallax]").forEach(el=>{const k=parseFloat(el.dataset.parallax)||.15;gsap.fromTo(el,{yPercent:-k*50},{yPercent:k*50,ease:"none",scrollTrigger:{trigger:el.parentElement||el,start:"top bottom",end:"bottom top",scrub:true}})});
 $$(".collage figure").forEach((f,i)=>{gsap.from(f,{clipPath:"inset(100% 0 0 0)",duration:1.4,ease:"expo.out",scrollTrigger:{trigger:f,start:"top 88%",once:true},delay:i*.08});gsap.to($("img",f),{scale:1,ease:"none",scrollTrigger:{trigger:f,start:"top bottom",end:"bottom 30%",scrub:true}})});
 $$(".steps>div").forEach((d,i)=>ScrollTrigger.create({trigger:d,start:"top 85%",once:true,onEnter:()=>setTimeout(()=>d.classList.add("in"),i*150)}));
 $$(".sbar span").forEach((s,i)=>gsap.from(s,{scaleX:0,duration:1.4,ease:"expo.out",delay:i*.1,scrollTrigger:{trigger:s.parentElement,start:"top 88%",once:true}}));
 $$(".rowlink").forEach(r=>gsap.from(r,{opacity:0,y:36,duration:1,ease:"expo.out",scrollTrigger:{trigger:r,start:"top 92%",once:true}}));
}else{$$(".collage img").forEach(i=>i.style.transform="none");$$(".steps>div").forEach(d=>d.classList.add("in"))}
/* count-ups */
$$("[data-count]").forEach(el=>{const a=parseFloat(el.dataset.from),b=parseFloat(el.dataset.to),d=+(el.dataset.dec||3),o={v:a};el.textContent=(reduced?b:a).toFixed(d);if(reduced)return;
 ScrollTrigger.create({trigger:el,start:"top 85%",once:true,onEnter:()=>gsap.to(o,{v:b,duration:2.2,ease:"power3.inOut",onUpdate:()=>{el.textContent=o.v.toFixed(d)}})})});
/* ---------- magnetic buttons + cursor glow ---------- */
if(fine&&!reduced){
 $$(".btn:not(:disabled),.menu .cta,.brand").forEach(b=>{const xt=gsap.quickTo(b,"x",{duration:.6,ease:"power3"}),yt=gsap.quickTo(b,"y",{duration:.6,ease:"power3"});
  b.addEventListener("pointermove",e=>{const r=b.getBoundingClientRect();xt((e.clientX-r.left-r.width/2)*.28);yt((e.clientY-r.top-r.height/2)*.38)});b.addEventListener("pointerleave",()=>{xt(0);yt(0)})});
 const g=$(".glow");if(g){const gx=gsap.quickTo(g,"x",{duration:.9,ease:"power3"}),gy=gsap.quickTo(g,"y",{duration:.9,ease:"power3"});window.addEventListener("pointermove",e=>{root.classList.add("has-glow");gx(e.clientX);gy(e.clientY)},{passive:true})}
 $$(".card.hov,.cards .card").forEach(c=>c.addEventListener("pointermove",e=>{const r=c.getBoundingClientRect();c.style.setProperty("--mx",(e.clientX-r.left)+"px");c.style.setProperty("--my",(e.clientY-r.top)+"px")}))}
/* ---------- pinned scene (home) ---------- */
const scene=$("#scene");
if(scene&&window.SL)SL.load().then(D=>{
 const rows=D.gap.filter(g=>g.primary).sort((a,b)=>b.decoupled-a.decoupled),host=$("#scene-bars");
 host.innerHTML='<div class="bars-wrap"><span class="chance-line"></span><span class="chance-lab">CHANCE 0.33</span>'+rows.map(r=>`<div class="brow"><span class="lab">${r.name.replace(" (fine-tuned)"," · fine-tuned").replace(" (probe)"," · probe")}</span><span class="trk"><span class="fill" style="width:${r.pooled*100}%"></span></span><span class="val">${r.pooled.toFixed(3)}</span></div>`).join("")+"</div>";
 const fills=$$(".fill",host),vals=$$(".val",host),A=$("#st-a"),B=$("#st-b"),big=$("#bigval"),cap=$("#bigcap");
 const mp=rows.reduce((s,r)=>s+r.pooled,0)/rows.length,md=rows.reduce((s,r)=>s+r.decoupled,0)/rows.length;
 const set=t=>{const e=t<.5?2*t*t:1-Math.pow(-2*t+2,2)/2;fills.forEach((f,i)=>{const v=rows[i].pooled+(rows[i].decoupled-rows[i].pooled)*e;f.style.width=v*100+"%";f.style.setProperty("--t",e);vals[i].textContent=v.toFixed(3)});
  big.firstChild.textContent=(mp+(md-mp)*e).toFixed(2);A.style.opacity=1-Math.min(1,e*2.4);B.style.opacity=Math.min(1,(e-.35)*2.4);A.style.transform=`translateY(${-e*18}px)`;B.style.transform=`translateY(${(1-e)*18}px)`;cap.textContent=e<.5?"mean balanced accuracy · pooled random split":"mean balanced accuracy · source-controlled test"};
 set(0);
 if(reduced){set(1);$("#scene-static").hidden=false;return}
 const pin=matchMedia("(min-width: 901px)").matches;
 const st={trigger:scene,start:pin?"top top":"top 70%",end:pin?"+=170%":"bottom 40%",pin:pin?true:false,scrub:.6,anticipatePin:1};
 const o={p:0};gsap.timeline({scrollTrigger:st}).to(o,{p:1,ease:"none",duration:1,onUpdate:()=>set(Math.max(0,Math.min(1,(o.p-.18)/.64)))});
 ScrollTrigger.refresh()});
/* refresh after fonts/images/charts settle */
window.addEventListener("load",()=>setTimeout(()=>ScrollTrigger.refresh(),400));
})();
