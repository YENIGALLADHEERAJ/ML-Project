/* AI Demo (classic light instrument). Two clearly separated backends:
   LIVE  : POST /api/predict with raw image bytes (the study's real checkpoints, CPU, in memory).
   MOCK  : precomputed outputs of the same checkpoints on the exact shipped JPEG files (9 held-out FracAtlas images) (data/samples.json). Never used to answer an uploaded file.
   GSAP drives the scan, the report reveal, count-ups and bars; Lenis (from motion.js) handles scrolling. Falls back to instant rendering without GSAP / with reduced motion. */
(function(){
const {$,$$}=SL,CL=["Hip","Knee","Shoulder"],COL={Hip:"var(--c1)",Knee:"var(--c2)",Shoulder:"var(--c3)"};
const visualReview={
 sample1:"Hip",sample2:"Hip",sample3:"Hip",
 sample4:"Knee",sample5:"Knee",sample6:"Elbow",
 sample7:"Shoulder",sample8:"Shoulder",sample9:"Shoulder"
};
const elbowCaseId="sample6";
const G=window.gsap,reduced=matchMedia("(prefers-reduced-motion: reduce)").matches,anim=!!G&&!reduced;
const live={async available(){try{const r=await fetch("api/health",{cache:"no-store"});if(!r.ok)return false;return (await r.json()).status==="ok"}catch(e){return false}},
 async predict(file){const r=await fetch("api/predict",{method:"POST",headers:{"Content-Type":file.type||"image/jpeg"},body:file});const j=await r.json().catch(()=>({}));if(!r.ok)throw new Error(j.message||("Server error "+r.status));return j}};
const mock={samples:null,async load(){return this.samples||(this.samples=await fetch("data/samples.json").then(r=>r.json()))},async predict(id){const s=(await this.load()).find(x=>x.id===id);if(!s)throw new Error("Unknown sample");return s}};
let savedRegions={};
let mode="mock",current=null,sample=null,previewUrl=null,laser=null,busy=false;
const dz=$("#dz"),fi=$("#file"),out=$("#out"),stat=$("#backend"),laserEl=$("#laser");
const esc=t=>String(t).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const scrollToReport=()=>{if(innerWidth<=980){const t=$("#report-anchor");window.lenis?lenis.scrollTo(t,{offset:-84,duration:1.3}):t.scrollIntoView({behavior:reduced?"auto":"smooth"})}};
function setStatus(){const d=stat.querySelector(".dot"),t=stat.querySelector(".msg");d.className="dot "+(mode==="live"?"live":"mock");
 t.innerHTML=mode==="live"?"<b>Live inference</b> · analysed in memory, never stored":"<b>Demo mode</b> · inference server offline — choose a precomputed sample"}
/* ---------- init ---------- */
async function init(){mode=(await live.available())?"live":"mock";setStatus();let S;try{S=await mock.load()}catch(e){fail("The specimen library could not load. Refresh the page to retry.");return}const sb=$("#samples");
 if(mode==="mock"){
  try{const response=await fetch("data/expanded-samples.json",{cache:"no-cache"});if(response.ok)savedRegions=await response.json()}catch(e){}
 }
 S.forEach((s,i)=>{const b=document.createElement("button");b.type="button";b.setAttribute("aria-pressed","false");b.setAttribute("aria-label","Sample "+(i+1)+(s.id===elbowCaseId?", likely elbow, label-audit example":", visually reviewed as "+(visualReview[s.id]||"unverified")));b.innerHTML=`<img src="${s.file}" alt="" loading="lazy"><span class="n">${String(i+1).padStart(2,"0")}</span>`;b.addEventListener("click",()=>pick(s,b));sb.appendChild(b);
  if(anim&&matchMedia("(hover: hover)").matches){const rx=G.quickTo(b,"rotationY",{duration:.5}),ry=G.quickTo(b,"rotationX",{duration:.5});b.addEventListener("pointermove",e=>{const r=b.getBoundingClientRect();rx(((e.clientX-r.left)/r.width-.5)*18);ry(-((e.clientY-r.top)/r.height-.5)*18)});b.addEventListener("pointerleave",()=>{rx(0);ry(0)})}});
 sb.setAttribute("data-lenis-prevent","");
 if(mode==="mock")$("#drop-sub").textContent="Uploads need the inference server — pick a specimen below.";
 if(anim){const tl=G.timeline({defaults:{ease:"expo.out"}});tl.from(".plate",{y:60,opacity:0,duration:1.4,delay:.6,clearProps:"transform,opacity"}).from(".plate .cap span",{opacity:0,y:8,stagger:.1,duration:.8},"-=.9").from(".film .reticle i",{scale:2.4,opacity:0,stagger:.08,duration:1},"-=1").from("#samples button",{opacity:0,y:20,stagger:.05,duration:.9,clearProps:"transform,opacity"},"-=.8").from(".report",{y:60,opacity:0,duration:1.4,clearProps:"transform,opacity"},"-=1.2").from(".idle li",{opacity:0,x:-16,stagger:.12,duration:.9},"-=.8");
  G.to(".film .prompt svg",{y:-6,duration:2,yoyo:true,repeat:-1,ease:"sine.inOut"})}
 const q=new URLSearchParams(location.search).get("sample");if(q&&S[+q-1])setTimeout(()=>pick(S[+q-1],$$("#samples button")[+q-1]),1800)}
/* ---------- input ---------- */
function showImage(src,label){const oldUrl=previewUrl;previewUrl=src;
 const pr=$(".prompt",dz);if(pr&&pr.style.display!=="none")anim?G.to(pr,{opacity:0,y:-14,duration:.35,onComplete:()=>pr.style.display="none"}):pr.style.display="none";
 const load=window.OTFilm?OTFilm.swap(dz,src,{imageClass:"spec",alt:"Selected radiograph"}):Promise.reject(new Error("Image transition module unavailable"));
 load.catch(e=>fail(e.message)).finally(()=>{if(oldUrl&&oldUrl!==src&&oldUrl.startsWith("blob:"))URL.revokeObjectURL(oldUrl)});
 let lb=$(".label",dz);if(!lb){lb=document.createElement("div");lb.className="label";dz.appendChild(lb)}lb.textContent=label}

function pick(s,b){if(busy)return;$$("#samples button").forEach(x=>x.setAttribute("aria-pressed",x===b));sample=s;current=null;const i=$$("#samples button").indexOf(b)+1;showImage(s.file,"SPECIMEN "+String(i).padStart(2,"0")+(s.id===elbowCaseId?" · LIKELY ELBOW":" · "+(visualReview[s.id]||"HELD-OUT").toUpperCase()));run()}
function onFile(f){if(!f||busy)return;if(mode!=="live")return fail("Uploads need the inference server. Please choose one of the precomputed specimens.");
 if(!/^image\/(jpeg|png|bmp|webp|tiff)$/.test(f.type))return fail("Please choose a JPEG, PNG, WebP, BMP or TIFF image. (DICOM must be exported to an image first.)");
 if(f.size>12*1024*1024)return fail("File is larger than 12 MB.");
 $$("#samples button").forEach(x=>x.setAttribute("aria-pressed","false"));sample=null;current=f;showImage(URL.createObjectURL(f),"YOUR UPLOAD · IN MEMORY ONLY");run()}
function fail(m){out.innerHTML=`<div class="report"><div class="rp-pad"><div class="err" role="alert"><b>Cannot analyse.</b> ${esc(m)}</div></div></div>`;if(anim)G.from(".err",{x:-12,opacity:0,duration:.7,ease:"expo.out"})}
/* ---------- scan + run ---------- */
function scanOn(){dz.classList.add("busy");if(!anim)return;laserEl.style.opacity=1;laser=G.fromTo(laserEl,{y:0},{y:dz.clientHeight-3,duration:1.15,ease:"sine.inOut",yoyo:true,repeat:-1});G.to(".plate",{boxShadow:"0 2px 0 #000,0 40px 90px -30px rgba(212,255,58,.25),0 0 0 1px #4f6f38",duration:.6})}
function scanOff(){dz.classList.remove("busy");if(!anim)return;laser&&laser.kill();G.to(laserEl,{opacity:0,duration:.4});G.to(".plate",{boxShadow:"0 2px 0 #000,0 40px 70px -34px rgba(4,22,12,.6),0 0 0 1px #203c25",duration:.8})}
async function run(){busy=true;scanOn();
 out.innerHTML=`<div class="report"><div class="rp-pad"><div class="rp-head"><div><span class="rp-kicker">Analysing</span><span class="rp-no">Preparing the image and scoring anatomy…</span></div></div><div class="skel" style="width:60%;height:44px"></div><div class="skel"></div><div class="skel" style="width:80%"></div><div class="skel" style="width:70%"></div></div></div>`;
 scrollToReport();const t0=performance.now();
 try{let r,isLive=false;if(current){r=await live.predict(current);isLive=true}else if(mode==="live"){const response=await fetch(sample.file);if(!response.ok)throw new Error("Could not load this specimen. Try another sample.");const blob=await response.blob();r=await live.predict(blob);r={...r,id:sample.id,file:sample.file,true_label:sample.true_label,source:sample.source};isLive=true}else{r={...await mock.predict(sample.id),expanded:savedRegions[sample.id]}}const wait=Math.max(0,(anim?500:0)-(performance.now()-t0));await new Promise(s=>setTimeout(s,wait));render(r,isLive)}
 catch(e){fail(e.message)}finally{busy=false;scanOff()}}
/* ---------- report ---------- */
function expandedReport(r){
 const classes=r.expanded?.classes;
 if(!classes?.length)return "";
 const selected=classes.filter(c=>c.selected).map(c=>c.name);
 const labels=selected.length?selected.join(", "):"No region met its cutoff";
 const conflicting=selected.includes("Elbow")&&(selected.includes("Knee")||selected.includes("Leg"));
 const reviewed=visualReview[r.id];
 let note="";
 if(reviewed==="Elbow"){
  note=selected.includes("Elbow")
   ?conflicting
    ?"The provisional visual review identifies Elbow. The model picked up Elbow and also flagged a lower-limb region on this image."
    :"The expanded model flagged Elbow, which matches the provisional visual review."
   :"The provisional visual review identified an elbow. The expanded model missed it.";
 }else if(conflicting){
  note="The model flagged both an elbow and a lower-limb region. Review the image and the scores to check for a mismatch.";
 }else if(reviewed==="Shoulder"&&selected.includes("Elbow")){
  note="The visual review identified a shoulder. The expanded model also flagged Elbow.";
 }
 const pct=n=>(n*100).toFixed(1)+"%";
 const scores=classes.map(c=>`<tr><th scope="row">${esc(c.name)}</th><td>${pct(c.score)}</td><td>${pct(c.threshold)}</td><td>${c.selected?"Flagged":"Below cutoff"}</td></tr>`).join("");
 return `<section class="rp-sec expanded-report"><h3>Expanded anatomy model</h3><small>Model prediction</small><p class="expanded-labels">${esc(labels)}</p><p>The model scores the center crop across eight views. Each region has its own cutoff, and more than one region can be flagged.</p>${note?`<p class="expanded-note">${esc(note)}</p>`:""}
 <table class="expanded-scores" aria-label="Six-region scores and decision cutoffs"><thead><tr><th scope="col">Region</th><th scope="col">Score</th><th scope="col">Cutoff</th><th scope="col">Result</th></tr></thead><tbody>${scores}</tbody></table></section>`;
}
function ring(M,main){const C=2*Math.PI*52,seg=C/4,gap=6;return `<div class="ring" aria-hidden="true"><svg viewBox="0 0 132 132"><circle class="bg" cx="66" cy="66" r="52"/>${M.map((m,i)=>`<circle class="seg ${m.pred===main.pred?"":"no"}" cx="66" cy="66" r="52" stroke-dasharray="${seg-gap} ${C}" stroke-dashoffset="${-i*seg}" data-len="${seg-gap}" data-c="${C}"/>`).join("")}</svg><div class="mid"><div><b class="agree">${M.filter(m=>m.pred===main.pred).length}/4</b><i>agree</i></div></div></div>`}
function render(r,isLive){
 const M=r.models,main=M[0],agree=r.all_agree,nofa=M.find(m=>m.id==="no_fracatlas"),f=r.image,nAgree=M.filter(m=>m.pred===main.pred).length;
 const no=current?"Upload":(r.id?"No. "+r.id.replace("sample","").padStart(2,"0"):"Sample");
 const anatomy=visualReview[r.id],outOfScope=anatomy&&!CL.includes(anatomy);
 const matches=anatomy?M.filter(m=>m.pred===anatomy).length:null;
 const rows=M.map(m=>`<div class="crow${(anatomy?m.pred!==anatomy:m.pred!==main.pred)?" dis":""}"><div><div class="nm">${esc(m.name)}</div><div class="ds">${esc(m.description)}</div><span class="pr">${m.pred} · ${(m.confidence*100).toFixed(1)}%</span>${anatomy?`<span class="review-match">${outOfScope?"Unsupported joint":m.pred===anatomy?"Matches visual review":"Differs from visual review"}</span>`:""}</div><div>${CL.map(c=>`<div class="hb${c===m.pred?" top":""}"><span>${c}</span><span class="t"><span class="f" style="background:${COL[c]}" data-w="${(m.probs[c]*100).toFixed(1)}"></span></span><span class="v">${(m.probs[c]*100).toFixed(1)}%</span></div>`).join("")}</div></div>`).join("");
 const verdict=agree?`<div class="verdict"><b>Concordance · 4 of 4</b>All four checkpoints say <span style="font-weight:600">${main.pred}</span>. In the study, agreement like this was typical <i>for familiar sources</i>; it is not evidence the answer is right for a new hospital, device or joint.</div>`
  :`<div class="verdict dis"><b>Disagreement · ${nAgree} of 4 agree</b>The pooled model says <span style="font-weight:600">${main.pred}</span>${nofa&&nofa.pred!==main.pred?`, while the model trained without FracAtlas says <span style="font-weight:600">${nofa.pred}</span> (${(nofa.confidence*100).toFixed(0)}%)`:""}. This is the source sensitivity the study measures: when training and test sources differ, joint recognition can fall toward chance.</div>`;
 const truth=r.true_label?`<p class="small" style="color:var(--muted);margin:12px 0 0">Project label: <b style="color:var(--ink-2)">${r.true_label}</b> (${esc(r.source||"")}).${r.true_label==="Knee"?" The project’s FracAtlas knee labels are provisional — AI-assigned, awaiting clinician verification.":""}</p>`:"";
 const anatomyNote=outOfScope?`<div class="verdict dis specimen-note"><b>Likely elbow · outside the three-class benchmark</b>This image appears to show a lateral elbow. FracAtlas tagged this image as Leg, and the original three-class benchmark recorded it as Knee. The four benchmark checkpoints can only choose Hip, Knee or Shoulder. The anatomy assessment is based on visual review and awaits clinician verification.</div>`:anatomy?`<div class="verdict ${matches===M.length?"":"dis"} specimen-note"><b>Visual review · ${anatomy}</b>${matches} of ${M.length} predictions match the joint visible in this specimen.</div>`:"";
 const origSrc=current?previewUrl:r.file;
 const fig=r.gradcam?`<section class="rp-sec rp-fig"><h3>Grad-CAM activation overlay</h3><div class="cmp" id="cmp"><img class="base" src="${origSrc}" alt="Original radiograph"><img class="over-img" src="${r.gradcam}" alt="Grad-CAM activation overlay for ${r.gradcam_class}"><div class="hdl"></div><span class="lb l">Grad-CAM · ${r.gradcam_class}</span><span class="lb r">Original</span><input type="range" min="0" max="100" value="50" aria-label="Compare original and activation overlay"></div><figcaption><b>Drag to compare.</b> Last convolutional block of the pooled model. Highlighted regions influenced the pooled model’s score for the displayed class. The benchmark also found that models could use cues such as image borders.</figcaption></section>`:"";
 const facts=f?`<section class="rp-sec"><h3>Image properties</h3><div class="facts"><div>Size<b>${f.width}×${f.height}</b></div><div>Aspect<b>${f.aspect}</b></div><div>Format<b>${esc(f.format)}</b></div><div>File<b>${f.file_kb} kB</b></div><div>Border<b>${f.border_mean}</b></div></div><p class="small" style="color:var(--muted);margin:12px 0 0">Size, aspect and border are cheap, non-anatomical cues. In our shortcut probes, the dimensions-only model reached 97.1% pooled balanced accuracy and 33.3% under source-decoupled testing (<a href="results.html#t-short">Results</a>).</p></section>`:"";
 const warn=(r.warnings||[]).length?`<ul class="small" style="color:var(--muted);margin:14px 0 0;padding-left:18px">${r.warnings.map(w=>`<li>${esc(w)}</li>`).join("")}</ul>`:"";
 out.innerHTML=`<article class="report" id="report"><div class="rp-pad">
 <header class="rp-head"><div><span class="rp-kicker">Joint Recognition Report</span><span class="rp-no">Specimen <b>${esc(current?"Upload":no)}</b></span></div><span class="pill ${isLive?"ok":"warn"}">${isLive?(current?"LIVE · UPLOADED":"LIVE · SAMPLE"):"PRECOMPUTED · SAMPLE"}</span></header>
 ${expandedReport(r)}
 ${anatomyNote}
 <div class="rp-result"><div><small>Three-class benchmark · pooled prediction</small><span class="rp-word" aria-label="${main.pred}">${esc(main.pred)}</span><p>Softmax score <b class="conf">0.0</b>%. The model divides its score among Hip, Knee and Shoulder.</p></div>${ring(M,main)}</div>
 <section class="rp-sec"><h3>Four checkpoints, one image</h3>${rows}${verdict}${truth}</section>${fig}${facts}${warn}
 <div class="review-export"><button type="button" class="btn" id="download-review">Download review record</button><p>Includes model scores and benchmark agreement. Image pixels and filenames are omitted.</p></div><p class="rp-foot"><b>Project scope.</b> The expanded model scores anatomy. The four benchmark checkpoints compare source sensitivity across Hip, Knee and Shoulder.</p></div></article>`;
 const root=$("#report"),confEl=$(".conf",root),segs=$$(".ring .seg",root),bars=$$(".hb .f",root);
 $("#download-review",root).addEventListener("click",()=>{
  const record={
   project:"OrthoTrace", schema_version:1,
   inference:isLive?"live":"precomputed",
   input:current?"upload":no,
   visual_review:visualReview[r.id]||null,
   expanded:r.expanded||null,
   benchmark:M.map(({id,name,pred,probs})=>({id,name,pred,probs})),
   benchmark_agreement:nAgree,
   scope:"Anatomy model evaluation and dataset quality review"
  };
  const url=URL.createObjectURL(new Blob([JSON.stringify(record,null,2)],{type:"application/json"}));
  const link=document.createElement("a");link.href=url;link.download="orthotrace-review.json";link.click();
  setTimeout(()=>URL.revokeObjectURL(url),1000);
 });
 const cmp=$("#cmp");if(cmp){const inp=$("input",cmp),ov=$(".over-img",cmp),h=$(".hdl",cmp);const set=v=>{ov.style.clipPath=`inset(0 ${100-v}% 0 0)`;h.style.left=v+"%"};inp.addEventListener("input",()=>set(+inp.value));set(50);
  if(anim&&window.ScrollTrigger)ScrollTrigger.create({trigger:cmp,start:"top 80%",once:true,onEnter:()=>{const o={v:50};G.to(o,{v:82,duration:.9,ease:"power2.inOut",yoyo:true,repeat:1,onUpdate:()=>{inp.value=o.v;set(o.v)}})}})}
 if(!anim){confEl.textContent=(main.confidence*100).toFixed(1);bars.forEach(b=>b.style.width=b.dataset.w+"%");return}
 const cv={v:0};
 G.set(segs,{attr:{"stroke-dasharray":"0 400"}});
 const tl=G.timeline({defaults:{ease:"expo.out"}});
 tl.from(root,{y:24,opacity:0,duration:.9,clearProps:"transform,opacity"})
  .from(".rp-word",{y:12,opacity:0,duration:.65,clearProps:"transform,opacity"},"-=.4")
  .to(cv,{v:main.confidence*100,duration:1.6,ease:"power3.out",onUpdate:()=>{confEl.textContent=cv.v.toFixed(1)}},"<.1")
  .to(segs,{attr:{"stroke-dasharray":(i,el)=>`${el.dataset.len} 400`},duration:.9,stagger:.12},"<.2")
  .from(".ring .agree",{scale:.4,opacity:0,duration:.8},"<.3")
  .from(".rp-sec",{opacity:0,y:30,duration:1,stagger:.12,clearProps:"transform,opacity"},"-=.9");
 bars.forEach((b,i)=>G.to(b,{width:b.dataset.w+"%",duration:1.3,ease:"expo.out",delay:.9+(i%3)*.06+Math.floor(i/4)*.14}));
 $$(".crow.dis",root).forEach(r=>G.fromTo(r,{backgroundColor:"rgba(217,84,30,.18)"},{backgroundColor:"rgba(217,84,30,0)",duration:2.4,delay:1.6}));
 if(window.ScrollTrigger)setTimeout(()=>ScrollTrigger.refresh(),1800)}
/* ---------- events ---------- */
const needServer=()=>fail("Uploads need the inference server. Please choose a precomputed specimen.");
dz.addEventListener("click",e=>{if(busy||e.target.closest("button"))return;mode==="live"?fi.click():needServer()});
$("#browse").addEventListener("click",e=>{e.stopPropagation();if(busy)return;mode==="live"?fi.click():needServer()});
dz.addEventListener("keydown",e=>{if(e.key==="Enter"||e.key===" "){e.preventDefault();dz.click()}});
["dragenter","dragover"].forEach(ev=>dz.addEventListener(ev,e=>{e.preventDefault();if(!dz.classList.contains("over")){dz.classList.add("over");anim&&G.to(".plate",{scale:1.02,duration:.5,ease:"expo.out"})}}));
["dragleave","drop"].forEach(ev=>dz.addEventListener(ev,e=>{e.preventDefault();dz.classList.remove("over");anim&&G.to(".plate",{scale:1,duration:.6,ease:"expo.out"})}));
dz.addEventListener("drop",e=>onFile(e.dataTransfer.files[0]));
fi.addEventListener("change",()=>{onFile(fi.files[0]);fi.value=""});
init();
})();
