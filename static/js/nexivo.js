/* Nexivo: thin reading-progress line along the top edge. */
(function(){
  var bar=document.createElement('div');bar.className='nx-progress';bar.setAttribute('aria-hidden','true');
  document.body.appendChild(bar);
  function upd(){var m=document.documentElement.scrollHeight-innerHeight;bar.style.width=(m>0?Math.min(1,Math.max(0,scrollY/m))*100:0)+'%';}
  addEventListener('scroll',upd,{passive:true});addEventListener('resize',upd);upd();
})();
