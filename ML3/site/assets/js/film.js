/* Shared, load-safe radiograph transition. Never changes image pixels or model inputs. */
(function(){
 const jobs=new WeakMap();
 window.OTFilm={swap(container,src,options={}){
  const token={};jobs.set(container,token);container.setAttribute('aria-busy','true');
  const previous=options.current||container.querySelector('img[data-film-current],img.spec');
  const next=new Image();next.className=options.imageClass||(previous?previous.className:'spec');next.alt=options.alt||'Selected radiograph';
  return new Promise((resolve,reject)=>{
   next.onload=()=>{if(jobs.get(container)!==token)return resolve(false);
    const oldId=previous&&previous.id;if(oldId){previous.removeAttribute('id');next.id=oldId}
    next.setAttribute('data-film-current','');previous&&previous.removeAttribute('data-film-current');container.appendChild(next);
    const G=window.gsap,animate=G&&!matchMedia('(prefers-reduced-motion: reduce)').matches;
    const finish=()=>{previous&&previous.remove();container.classList.remove('film-transitioning');container.setAttribute('aria-busy','false');resolve(true)};
    if(!animate){finish();return}
    container.classList.add('film-transitioning');G.killTweensOf(next);if(previous)G.killTweensOf(previous);
    let wipe=container.querySelector('.xray-wipe');if(!wipe){wipe=document.createElement('i');wipe.className='xray-wipe';wipe.setAttribute('aria-hidden','true');container.appendChild(wipe)}
    G.set(next,{opacity:0,scale:1.055,clipPath:'inset(0 100% 0 0)',filter:'grayscale(1) brightness(1.5) blur(5px)'});
    const tl=G.timeline({onComplete:finish});
    if(previous)tl.to(previous,{opacity:.15,x:-18,filter:'grayscale(1) blur(4px)',duration:.55,ease:'power2.inOut'},0);
    tl.to(next,{opacity:1,scale:1,clipPath:'inset(0 0% 0 0)',filter:'grayscale(1) brightness(1) blur(0px)',duration:1.05,ease:'power3.inOut',clearProps:'transform,filter,clipPath,opacity'},0)
      .fromTo(wipe,{left:'-5%',opacity:0},{left:'105%',opacity:.8,duration:1,ease:'power3.inOut'},0)
      .to(wipe,{opacity:0,duration:.2},.85);
   };
   next.onerror=()=>{container.setAttribute('aria-busy','false');reject(new Error('Could not load the selected radiograph.'))};
   next.src=src;
  });
 }};
})();
