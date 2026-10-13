/* TechPulse showreel theme: timecode HUD, scroll progress, colour-wipe transitions */
(function(){
  var rm=window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches;
  var d=document,b=d.body;
  function p2(n){return (n<10?'0':'')+n}
  var hud=d.createElement('div');hud.className='rt-hud';hud.setAttribute('aria-hidden','true');
  hud.innerHTML='<div class="rt-bar"></div><i></i><b>TechPulse</b><span class="rt-hide">Daily Tech Reel</span><span class="rt-sp"></span><span class="rt-hide" data-rt-sec></span><span data-rt-tc>00:00:00</span><b data-rt-pct>0%</b>';
  b.appendChild(hud);
  var bar=hud.querySelector('.rt-bar'),tc=hud.querySelector('[data-rt-tc]'),pct=hud.querySelector('[data-rt-pct]'),sec=hud.querySelector('[data-rt-sec]');
  var t0=Date.now();
  sec.textContent=(d.title||'').split(/[—|–-]/)[0].trim().slice(0,28);
  function upd(){
    var s=Math.floor((Date.now()-t0)/1000);tc.textContent=p2(Math.floor(s/3600))+':'+p2(Math.floor(s/60)%60)+':'+p2(s%60);
  }
  function scr(){
    var m=d.documentElement.scrollHeight-innerHeight,r=m>0?Math.min(1,Math.max(0,scrollY/m)):0;
    bar.style.width=(r*100)+'%';pct.textContent=Math.round(r*100)+'%';
  }
  setInterval(upd,1000);addEventListener('scroll',scr,{passive:true});addEventListener('resize',scr);scr();
  if(rm)return;
  var w=d.createElement('div');w.className='rt-wipe';w.setAttribute('aria-hidden','true');
  w.innerHTML='<span></span><span></span><span></span><span></span>';b.appendChild(w);
  function reveal(){
    w.className='rt-wipe hold';void w.offsetWidth;
    requestAnimationFrame(function(){w.className='rt-wipe out';setTimeout(function(){w.className='rt-wipe'},800)});
  }
  var came=false;try{came=sessionStorage.getItem('rt-wipe')==='1';sessionStorage.removeItem('rt-wipe')}catch(e){}
  if(came)reveal();
  addEventListener('pageshow',function(e){if(e.persisted)w.className='rt-wipe'});
  d.addEventListener('click',function(e){
    if(e.defaultPrevented||e.button!==0||e.metaKey||e.ctrlKey||e.shiftKey||e.altKey)return;
    var a=e.target.closest&&e.target.closest('a[href]');
    if(!a||a.target&&a.target!=='_self'||a.hasAttribute('download'))return;
    var u;try{u=new URL(a.href,location.href)}catch(x){return}
    if(u.origin!==location.origin||u.pathname===location.pathname&&u.search===location.search)return;
    if(/\.(xml|pdf|zip|png|jpe?g|svg|json)$/i.test(u.pathname))return;
    e.preventDefault();
    try{sessionStorage.setItem('rt-wipe','1')}catch(x){}
    w.className='rt-wipe cover';
    setTimeout(function(){location.href=u.href},520);
  });
})();
