/* Motion tells the same story as the content; data and navigation never depend on it. */
(function(){
 if(!window.gsap||matchMedia('(prefers-reduced-motion: reduce)').matches)return;
 const G=gsap,stage=document.querySelector('.scan-stage');
 if(stage){
   const intro=G.timeline({defaults:{ease:'power3.out'}});
   intro.from('.scan-film-main',{y:65,rotation:5,opacity:0,duration:1.4},.15)
     .from('.scan-film-back',{y:45,rotation:-3,opacity:0,duration:1.3},.35)
     .from('.floating-result',{x:35,y:20,opacity:0,duration:1.1},.7)
     .from('.hero-label,.hero-description,.experience-copy .cta-row,.hero-footnote',{y:20,opacity:0,duration:.9,stagger:.1},.3);
   G.to('.film-scanner',{top:'92%',duration:3.5,repeat:-1,yoyo:true,ease:'sine.inOut'});
   G.to('.scan-film-back',{y:-14,duration:4,repeat:-1,yoyo:true,ease:'sine.inOut'});
   if(window.ScrollTrigger)G.to(stage,{yPercent:10,ease:'none',scrollTrigger:{trigger:'.experience-hero',start:'top top',end:'bottom top',scrub:1}});
 }
 if(!window.ScrollTrigger)return;
 document.querySelectorAll('.journey-links,.task-grid,.pipeline,.evidence-links').forEach(group=>{
   G.from(group.children,{y:32,opacity:0,duration:.85,stagger:.1,ease:'power3.out',clearProps:'transform,opacity',scrollTrigger:{trigger:group,start:'top 90%',once:true}});
 });
 document.querySelectorAll('.implant-art,.diagram-panel,.gap-statement,.workbench-preview,.final-invitation').forEach(el=>G.from(el,{y:35,opacity:0,duration:1,ease:'power3.out',clearProps:'transform,opacity',scrollTrigger:{trigger:el,start:'top 92%',once:true}}));
 document.querySelectorAll('.contribution-lines a,.evolution li').forEach(el=>G.from(el,{x:-25,opacity:0,duration:.8,clearProps:'transform,opacity',scrollTrigger:{trigger:el,start:'top 92%',once:true}}));
})();
