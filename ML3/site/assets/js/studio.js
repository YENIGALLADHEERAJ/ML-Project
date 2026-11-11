/* Original radiograph pixel field: local specimen, no model output is fabricated. */
(function(){
 const canvas=document.querySelector('#radiograph-field');
 const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
 if(canvas){
  const ctx=canvas.getContext('2d'),source=new Image();let points=[],w=0,h=0,dpr=1,raf=0,visible=true,time=0,last=0;const pointer={x:-1000,y:-1000};
  function size(){w=canvas.clientWidth;h=canvas.clientHeight;dpr=Math.min(devicePixelRatio||1,1.6);canvas.width=w*dpr;canvas.height=h*dpr;ctx.setTransform(dpr,0,0,dpr,0,0);if(source.complete&&source.naturalWidth)sample()}
  function sample(){const off=document.createElement('canvas');off.width=96;off.height=116;const c=off.getContext('2d',{willReadFrequently:true});c.drawImage(source,0,0,96,116);const pixels=c.getImageData(0,0,96,116).data;points=[];const fieldW=Math.min(w*.8,850),fieldH=h*.94,step=fieldW/96,left=w-fieldW+30,top=(h-fieldH)/2;for(let y=0;y<116;y++)for(let x=0;x<96;x++){const v=pixels[(y*96+x)*4]/255;if(v>.07&&((x+y)%2===0||v>.3))points.push({x:left+x*step,y:top+y*fieldH/116,v,s:Math.max(1,step*.48)})}draw(0)}
  function draw(t){ctx.clearRect(0,0,w,h);for(const p of points){const dx=p.x-pointer.x,dy=p.y-pointer.y,dist=Math.hypot(dx,dy),near=Math.max(0,1-dist/145),wave=reduced?0:Math.sin(t*.00065+p.y*.018+p.x*.008)*2;const shift=near*16;ctx.globalAlpha=Math.min(.75,p.v*.6+near*.3);ctx.fillStyle=near>.5?'#d4ff3a':p.v>.65?'#69c88c':'#256e53';ctx.fillRect(p.x+(dx/(dist||1))*shift,p.y+wave+(dy/(dist||1))*shift,p.s,p.s)}ctx.globalAlpha=1}
  function frame(t){if(!visible||reduced){raf=0;return}if(t-last>32){draw(t);last=t}raf=requestAnimationFrame(frame)}
  const hero=canvas.parentElement;hero.addEventListener('pointermove',e=>{const r=canvas.getBoundingClientRect();pointer.x=e.clientX-r.left;pointer.y=e.clientY-r.top},{passive:true});hero.addEventListener('pointerleave',()=>{pointer.x=pointer.y=-1000});
  source.onload=()=>{size();if(!reduced&&!raf)raf=requestAnimationFrame(frame)};source.src='assets/samples/sample5.jpg';
  let timer;addEventListener('resize',()=>{clearTimeout(timer);timer=setTimeout(size,120)});new IntersectionObserver(entries=>{visible=entries[0].isIntersecting;if(visible&&!raf&&!reduced)raf=requestAnimationFrame(frame)},{threshold:0}).observe(canvas);document.addEventListener('visibilitychange',()=>{visible=!document.hidden;if(visible&&!raf&&!reduced)raf=requestAnimationFrame(frame)});
 }
 if(!window.gsap||!window.ScrollTrigger||reduced)return;
 document.querySelectorAll('[data-reading]').forEach(el=>{const text=el.textContent;el.replaceChildren(...text.trim().split(/\s+/).flatMap(word=>{const span=document.createElement('span');span.textContent=word+' ';return[span]}));gsap.fromTo(el.children,{opacity:.22},{opacity:1,stagger:.12,ease:'none',scrollTrigger:{trigger:el,start:'top 85%',end:'bottom 45%',scrub:.5}})});
 document.querySelectorAll('.receipt-main,.collection-preview,.research-shelf').forEach(el=>gsap.from(el,{y:35,opacity:0,duration:1,ease:'power3.out',clearProps:'transform,opacity',scrollTrigger:{trigger:el,start:'top 92%',once:true}}));
})();
