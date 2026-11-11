/* Robustness Demo: interactive pooled vs source-controlled "what the model is really recognising" explorer. All numbers from data/results.json. */
(function(){
const {$,$$}=SL;
SL.load().then(D=>{
 const sel=$("#rb-model"),pm=$("#rb-pooled"),dm=$("#rb-dec"),gap=$("#rb-gap"),note=$("#rb-note"),bar1=$("#rb-bar1"),bar2=$("#rb-bar2");
 const prim=D.gap.filter(g=>g.primary||g.id.startsWith("rf|dims")||g.id.startsWith("rf|meta"));
 prim.forEach(g=>{const o=document.createElement("option");o.value=g.id;o.textContent=g.name;sel.appendChild(o)});
 sel.value="ft|effnet|full";
 function show(){const g=D.gap.find(x=>x.id===sel.value);
  pm.textContent=g.pooled.toFixed(3);dm.textContent=g.decoupled.toFixed(3);gap.textContent=(g.gap*100).toFixed(1)+" pp";
  bar1.style.width=(g.pooled*100)+"%";bar2.style.width=(g.decoupled*100)+"%";
  note.innerHTML=`Source-controlled balanced accuracy: 95% CI ${g.dec_lo.toFixed(2)}–${g.dec_hi.toFixed(2)} · drop: 95% CI ${(g.gap_lo*100).toFixed(1)}–${(g.gap_hi*100).toFixed(1)} pp · ${g.seeds} seed${g.seeds>1?"s":""}`+(g.p_holm?` · Holm-adjusted p = ${g.p_holm}`:"")+(g.id.startsWith("rf|")?`<br><b>This model sees no anatomy</b> — only ${g.id.includes("dims")?"image width, height and aspect ratio":"file/image metadata"}. Chance is 0.333.`:"")}
 sel.addEventListener("change",show);show();
 /* three-way scenario */
 const sc=$("#rb-scen");
 const S={pooled:{t:"Pooled random split",d:"Train and test images are drawn from the same six sources. A model can recognise the <i>source</i> and get the joint right.",k:"pooled"},dec:{t:"Source-controlled (hold out FracAtlas)",d:"Train without FracAtlas, test on FracAtlas, the only source with hip, knee and shoulder together. Joint no longer correlates with source.",k:"decoupled"}};
 function scen(k){$$("#rb-seg button").forEach(b=>b.setAttribute("aria-pressed",b.dataset.k===k));$("#rb-title").textContent=S[k].t;$("#rb-desc").innerHTML=S[k].d;
  const rows=D.gap.filter(g=>g.primary).sort((a,b)=>b[S[k].k]-a[S[k].k]);
  sc.innerHTML=rows.map(g=>`<div class="pbar scenario-row"><span class="small">${g.name.replace(" (fine-tuned)"," (FT)")}</span><span class="t"><span class="f" style="background:${k==="pooled"?"var(--c1)":"var(--c2)"};width:${(g[S[k].k]*100).toFixed(1)}%"></span></span><span class="mono">${g[S[k].k].toFixed(3)}</span></div>`).join("")+`<div class="pbar scenario-row"><span class="small muted">chance</span><span class="t"><span class="f" style="background:var(--chance);width:33.3%"></span></span><span class="mono muted">0.333</span></div>`}
 $$("#rb-seg button").forEach(b=>b.addEventListener("click",()=>scen(b.dataset.k)));scen("pooled");
 /* held-out predictions */
 const hp=$("#rb-hold");
 if(hp){const rows=[["ft|effnet|full","K"],["ft|effnet|full","U"]];hp.innerHTML=rows.map(([m,s])=>{const h=D.holdout_pred_share[m][s];return `<div class="card"><h4>${h.label}</h4><p class="small muted">EfficientNet-B3, trained without this source. What does it call these images?</p>${["Hip","Knee","Shoulder"].map((c,j)=>`<div class="pbar"><span>${c}</span><span class="t"><span class="f" style="background:var(--c${j+1});width:${h.share[j]*100}%"></span></span><span class="mono">${(h.share[j]*100).toFixed(0)}%</span></div>`).join("")}</div>`}).join("")}
});
})();
