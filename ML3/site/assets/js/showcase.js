/* Reading-room controls work without animation libraries. */
(function(){
 const search=document.querySelector('#paper-search'),theme=document.querySelector('#paper-theme');
 if(search&&theme){const cards=[...document.querySelectorAll('.paper-card')];const filter=()=>{const query=search.value.trim().toLowerCase();let n=0;cards.forEach(card=>{const visible=(!query||card.dataset.search.includes(query))&&(theme.value==='all'||theme.value===card.dataset.theme);card.hidden=!visible;if(visible)n++});document.querySelector('#paper-count').textContent=n+' of '+cards.length+' references';document.querySelector('#paper-empty').hidden=n!==0;window.ScrollTrigger&&ScrollTrigger.refresh()};search.addEventListener('input',filter);theme.addEventListener('change',filter)}
})();
