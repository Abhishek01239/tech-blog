/* Motion reel engine: canvas scenes + synthesized score. Mount via <figure data-motion-reel>. */
(function(){
"use strict";
const W=1280,H=720,DUR=40;
const clamp=(x,a=0,b=1)=>Math.min(b,Math.max(a,x));
const lerp=(a,b,t)=>a+(b-a)*t;
const prog=(t,a,b)=>clamp((t-a)/(b-a));
const eOut=t=>1-Math.pow(1-t,3);
const eIn=t=>t*t*t;
const eIO=t=>t<.5?4*t*t*t:1-Math.pow(-2*t+2,3)/2;
const eExpo=t=>t>=1?1:1-Math.pow(2,-10*t);
const eBack=t=>{const c1=1.70158,c3=c1+1;return 1+c3*Math.pow(t-1,3)+c1*Math.pow(t-1,2)};
const eElastic=t=>t<=0?0:t>=1?1:Math.pow(2,-10*t)*Math.sin((t*10-.75)*(2*Math.PI/3))+1;
function rng(seed){return function(){seed|=0;seed=seed+0x6D2B79F5|0;let t=Math.imul(seed^seed>>>15,1|seed);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}}
const pad2=n=>(n<10?'0':'')+n;
const C={ink:'#101114',paper:'#EAE3D2',red:'#E8382B',yellow:'#F7C417',blue:'#1E4FD6',navy:'#0E1B3D',cream:'#F2EDE0',white:'#FAFAF7',teal:'#2FA6A0',coral:'#FF8A78',sage:'#9DB48A',orange:'#F08A3C',pink:'#F4B6B0'};
const F_DISP="'Anton','Impact','Arial Narrow',sans-serif";
const F_MONO="'JetBrains Mono','Courier New',monospace";

function hex2rgb(h){h=h.replace('#','');return [parseInt(h.slice(0,2),16),parseInt(h.slice(2,4),16),parseInt(h.slice(4,6),16)]}
function mix(a,b,t){const A=hex2rgb(a),B=hex2rgb(b);return 'rgb('+Math.round(lerp(A[0],B[0],t))+','+Math.round(lerp(A[1],B[1],t))+','+Math.round(lerp(A[2],B[2],t))+')'}

function txt(g,s,x,y,size,color,o){
  o=o||{};
  g.save();
  g.globalAlpha=o.a==null?1:o.a;
  g.font=(o.w||'')+' '+size+'px '+(o.f||F_DISP);
  if(o.mw){const m=g.measureText(s).width;if(m>o.mw){size=size*o.mw/m;g.font=(o.w||'')+' '+size+'px '+(o.f||F_DISP)}}
  g.fillStyle=color;
  g.textAlign=o.al||'left';
  g.textBaseline='alphabetic';
  if(o.ls){try{g.letterSpacing=o.ls+'px'}catch(e){}}
  g.translate(x,y);
  if(o.rot)g.rotate(o.rot);
  if(o.sc)g.scale(o.sc,o.sc);
  g.fillText(s,0,0);
  g.restore();
}
function tw(g,s,size,f,w){g.save();g.font=(w||'')+' '+size+'px '+(f||F_DISP);const r=g.measureText(s).width;g.restore();return r}

function mkPath(pts){
  const L=[0];
  for(let i=1;i<pts.length;i++)L.push(L[i-1]+Math.hypot(pts[i][0]-pts[i-1][0],pts[i][1]-pts[i-1][1]));
  return {pts:pts,L:L,len:L[L.length-1]};
}
function strokePath(g,P,p,color,w){
  if(p<=0)return null;
  const target=P.len*clamp(p);
  g.save();g.strokeStyle=color;g.lineWidth=w;g.lineCap='round';g.lineJoin='round';
  g.beginPath();g.moveTo(P.pts[0][0],P.pts[0][1]);
  let tip=P.pts[0];
  for(let i=1;i<P.pts.length;i++){
    if(P.L[i]<=target){g.lineTo(P.pts[i][0],P.pts[i][1]);tip=P.pts[i]}
    else{
      const f=(target-P.L[i-1])/((P.L[i]-P.L[i-1])||1);
      const x=lerp(P.pts[i-1][0],P.pts[i][0],f),y=lerp(P.pts[i-1][1],P.pts[i][1],f);
      g.lineTo(x,y);tip=[x,y];break;
    }
  }
  g.stroke();g.restore();
  return tip;
}
function wob(pts,sub,amt,seed){
  const R=rng(seed);const out=[];
  for(let i=0;i<pts.length-1;i++){
    const a=pts[i],b=pts[i+1];
    for(let k=0;k<sub;k++){const u=k/sub;out.push([lerp(a[0],b[0],u)+(R()-.5)*amt,lerp(a[1],b[1],u)+(R()-.5)*amt])}
  }
  out.push(pts[pts.length-1].slice());
  return out;
}
function arcPts(cx,cy,r,a0,a1,n,amt,seed){
  const R=rng(seed||1);const pts=[];
  for(let i=0;i<=n;i++){const a=lerp(a0,a1,i/n);const rr=r+(amt?(R()-.5)*amt:0);pts.push([cx+Math.cos(a)*rr,cy+Math.sin(a)*rr])}
  return pts;
}
function tri(g,cx,cy,s,rot,color){
  g.save();g.translate(cx,cy);g.rotate(rot);g.beginPath();
  g.moveTo(-.55*s,-.8*s);g.lineTo(-.55*s,.8*s);g.lineTo(.85*s,0);g.closePath();
  g.fillStyle=color;g.fill();g.restore();
}

/* ---------- wipes ---------- */
function wipe(g,t,B,cols){
  const dur=.8,st=.04,n=cols.length,k=1-(n-1)*st;
  const mid=.5*k+(n-1)*st/2;
  const u0=(t-(B-dur*mid))/dur;
  if(u0<=0||u0>=1)return;
  for(let i=0;i<n;i++){
    const u=clamp((u0-i*st)/k);
    let y=0,h;
    if(u<.4){h=H*eExpo(u/.4)}
    else if(u<.6){h=H}
    else{y=H*eIn((u-.6)/.4);h=H-y}
    if(h<=0)continue;
    g.fillStyle=cols[i];
    g.fillRect(Math.floor(i*W/n),y,Math.ceil(W/n)+1,h);
  }
}
const WIPES=[
  [4.5,[C.red,C.yellow,C.blue,C.ink,C.paper]],
  [9,[C.paper,C.red,C.yellow,C.blue,C.navy]],
  [15,[C.navy,C.cream,C.teal,C.coral,C.sage]],
  [25,[C.ink,C.coral,C.yellow,C.blue,C.white]],
  [32,[C.white,C.ink,C.blue,C.yellow,C.red]],
  [37,[C.red,C.yellow,C.paper,C.blue,C.ink]]
];
function grain(g,t){
  const R=rng(Math.floor(t*24)+7);
  g.save();g.globalAlpha=.07;
  for(let i=0;i<260;i++){g.fillStyle=R()<.5?'#000':'#fff';g.fillRect(R()*W,R()*H,2,2)}
  g.restore();
}
function hud(g,t){
  g.save();g.globalCompositeOperation='difference';
  txt(g,'DISTILBOOK / SHOWREEL',36,48,14,'#fff',{f:F_MONO,w:'600',ls:3});
  const ff=Math.floor((t%1)*30);
  txt(g,'00:'+pad2(Math.floor(t))+':'+pad2(ff),W-36,48,14,'#fff',{f:F_MONO,w:'600',ls:3,al:'right'});
  g.fillStyle='#fff';
  g.fillRect(36,H-30,(W-72)*clamp(t/DUR),3);
  g.globalAlpha=.35;g.fillRect(36,H-30,W-72,1);
  g.restore();
}

/* ---------- A: the page (0 - 4.5) ---------- */
const SHEET=mkPath([[-150,-195],[110,-195],[150,-155],[150,195],[-150,195],[-150,-195]]);
const A_BARS=(function(){
  const R=rng(11);const a=[];
  for(let i=0;i<11;i++)a.push({y:-140+i*30,w:i===0?220:150+R()*80,h:i===0?18:9,dx:300+R()*900,dy:(R()-.5)*500,rot:(R()-.5)*2});
  return a;
})();
function sA(g,t){
  g.fillStyle=C.ink;g.fillRect(0,0,W,H);
  g.fillStyle='rgba(255,255,255,.08)';
  for(let x=40;x<W;x+=40)for(let y=40;y<H;y+=40)g.fillRect(x,y,2,2);
  const exit=prog(t,3.4,4.15),ex=eIn(exit);
  g.save();
  g.translate(640,350);g.rotate(-.05+Math.sin(t*.9)*.012);g.scale(1+ex*.12,1+ex*.12);
  g.globalAlpha=prog(t,1.0,1.5)*(1-ex);
  g.beginPath();
  SHEET.pts.forEach((p,i)=>{if(i)g.lineTo(p[0],p[1]);else g.moveTo(p[0],p[1])});
  g.closePath();g.fillStyle=C.paper;g.fill();
  g.globalAlpha=1-ex;
  strokePath(g,SHEET,eIO(prog(t,.2,1.4)),C.cream,4);
  g.globalAlpha=1;
  A_BARS.forEach((b,i)=>{
    const p=eOut(prog(t,1.3+i*.09,1.6+i*.09));
    if(p<=0)return;
    g.save();g.translate(ex*b.dx,ex*b.dy);g.rotate(ex*b.rot);g.globalAlpha=1-ex*.6;
    g.fillStyle=i===0?C.ink:'#BDB6A3';
    g.fillRect(-110,b.y,b.w*p,b.h);
    g.restore();
  });
  g.restore();
  const cap='40 PAGES. ZERO VIEWS.';
  const n=Math.floor(prog(t,2.0,3.0)*cap.length);
  if(n>0)txt(g,cap.slice(0,n)+((Math.floor(t*4)%2&&n<cap.length)?'_':''),640,640,22,C.cream,{al:'center',f:F_MONO,w:'600',ls:5,a:1-ex});
  txt(g,'p.01 / 40',840,170,14,'rgba(250,250,247,.55)',{f:F_MONO,ls:2,a:prog(t,1,1.5)*(1-ex)});
}

/* ---------- B: drop anything in (4.5 - 9) ---------- */
const B_ROWS=[['PDF',C.yellow,C.ink],['DOCX',C.blue,C.paper],['LINK',C.red,C.paper],['IMAGE',C.ink,C.yellow]];
function sB(g,t){
  g.fillStyle=C.paper;g.fillRect(0,0,W,H);
  const exit=eIn(prog(t,6.6,7.1));
  B_ROWS.forEach((r,i)=>{
    const st=4.7+i*.5;
    const p=eExpo(prog(t,st,st+.28));
    const w=tw(g,r[0],150)+70;
    const x=lerp(-w-60,60,p)+exit*(W+300);
    const y=66+i*150;
    g.fillStyle=r[1];g.fillRect(x-400,y,w+400,130);
    txt(g,r[0],x,y+118,150,r[2]);
  });
  const se=eIO(prog(t,6.7,7.7));
  const ap=Math.max(0,eBack(prog(t,5.0,5.7)));
  g.fillStyle=C.red;
  g.beginPath();g.arc(lerp(980,640,se),lerp(250,320,se),lerp(150,240,se)*ap,0,Math.PI*2);g.fill();
  tri(g,lerp(1090,660,se),lerp(520,320,se),lerp(70,115,se)*ap,(1-se)*t*1.2,mix(C.blue,C.ink,se));
  g.save();
  g.translate(lerp(860,640,se),lerp(540,614,se));g.rotate((1-se)*t*.7);
  const sw=lerp(110,900,se)*ap,sh=lerp(110,26,se)*ap;
  g.fillStyle=C.yellow;g.fillRect(-sw/2,-sh/2,sw,sh);
  if(se>=1){g.fillStyle=C.ink;g.fillRect(-450,-13,900*prog(t,7.8,8.9),26)}
  g.restore();
  const cp=eExpo(prog(t,7.4,7.8));
  txt(g,'DROP ANYTHING IN.',640,112-(1-cp)*80,64,C.ink,{al:'center',a:cp,mw:900});
  txt(g,'PDF  ·  DOCX  ·  TXT  ·  IMAGES  ·  LINKS',640,675,16,C.ink,{al:'center',f:F_MONO,w:'600',ls:4,a:prog(t,8.0,8.4)*.8});
}

/* ---------- C: a script you approve (9 - 15) ---------- */
const C_LINES=['Every document hides a story.','DistilBook reads it first,','writes the narration,','and waits for your say.'];
const GREET=['Hello','Hola','Bonjour','Ciao','Hallo','Olá','Hej','Merhaba'];
function sC(g,t){
  const s=t-9;
  g.fillStyle=C.navy;g.fillRect(0,0,W,H);
  g.strokeStyle='rgba(242,237,224,.06)';g.lineWidth=1;
  for(let x=0;x<W;x+=64){g.beginPath();g.moveTo(x,0);g.lineTo(x,H);g.stroke()}
  for(let y=0;y<H;y+=64){g.beginPath();g.moveTo(0,y);g.lineTo(W,y);g.stroke()}
  const tp=eOut(prog(s,.25,.85));
  txt(g,'A SCRIPT YOU APPROVE.',110,108-(1-tp)*50,64,C.cream,{a:tp});
  const cp=Math.max(0,eBack(prog(s,.2,.85)));
  const shake=s>4.6?Math.max(0,1-(s-4.6)/.35):0;
  const sx=Math.sin(s*90)*8*shake,sy=Math.cos(s*70)*6*shake;
  g.save();
  g.translate(430+sx,350+sy);g.scale(cp,cp);g.translate(-320,-200);
  g.fillStyle='rgba(0,0,0,.35)';g.fillRect(10,12,640,400);
  g.fillStyle=C.cream;g.fillRect(0,0,640,400);
  txt(g,'SCRIPT  ·  SLIDE 3 OF 10',30,40,14,'#5a5a52',{f:F_MONO,w:'600',ls:3});
  g.fillStyle='#cfc8b5';g.fillRect(30,58,580,2);
  let caret=null;
  C_LINES.forEach((ln,i)=>{
    const y=120+i*62;
    const st=1.1+i*.95;
    const n=clamp(Math.floor((s-st)*34),0,ln.length);
    if(i===3){
      const hp=eOut(prog(s,3.7,4.3));
      g.fillStyle='rgba(247,196,23,.9)';
      g.fillRect(24,y-30,tw(g,ln,27,F_MONO)*hp+12,40);
    }
    if(n>0)txt(g,ln.slice(0,n),30,y,27,C.ink,{f:F_MONO});
    if(n>0&&n<ln.length)caret=[30+tw(g,ln.slice(0,n),27,F_MONO)+2,y];
  });
  if(caret&&Math.floor(s*5)%2===0){g.fillStyle=C.red;g.fillRect(caret[0],caret[1]-26,3,32)}
  const sp=prog(s,4.6,4.78);
  if(sp>0){
    g.save();
    g.translate(420,330);g.rotate(-.14);
    const k=lerp(3.2,1,eExpo(sp));g.scale(k,k);
    g.globalAlpha=Math.min(1,sp*4);
    g.strokeStyle=C.red;g.lineWidth=8;
    g.strokeRect(-190,-52,380,104);
    txt(g,'APPROVED',0,28,78,C.red,{al:'center'});
    g.restore();
  }
  g.restore();
  const lb=prog(s,.8,1.2);
  txt(g,'NARRATION  ·  20 LANGUAGES',820,190,15,C.cream,{f:F_MONO,w:'600',ls:3,a:.85*lb});
  const act=eOut(prog(s,4.7,5.1));
  for(let i=0;i<26;i++){
    const env=Math.abs(Math.sin(i*1.7));
    const h=8+act*(10+(Math.sin(s*9+i*.8)*.5+.5)*(40+60*env));
    g.globalAlpha=lb*(.35+.65*act);
    g.fillStyle=C.yellow;
    g.fillRect(820+i*14,300-h/2,8,h);
  }
  g.globalAlpha=1;
  if(s>4.8){
    const gi=Math.floor((s-4.8)*3)%GREET.length;
    txt(g,GREET[gi],820,420,64,C.yellow);
  }
  const c1=Math.max(0,eBack(prog(s,5.2,5.6))),c2=Math.max(0,eBack(prog(s,5.4,5.8)));
  g.save();g.translate(880,500);g.scale(c1,c1);
  g.strokeStyle=C.cream;g.lineWidth=3;g.strokeRect(-60,-34,120,68);
  txt(g,'16:9',0,6,18,C.cream,{al:'center',f:F_MONO,w:'600'});g.restore();
  g.save();g.translate(1040,500);g.scale(c2,c2);
  g.strokeStyle=C.cream;g.lineWidth=3;g.strokeRect(-34,-60,68,120);
  txt(g,'9:16',0,6,18,C.cream,{al:'center',f:F_MONO,w:'600'});g.restore();
  txt(g,'You review every line before a single frame is drawn.',110,610,22,C.cream,{f:F_MONO,a:prog(s,1.3,1.9)*.85});
}

/* ---------- D: 19 styles (15 - 25) ---------- */
const BULB=(function(){
  const P={};
  P.glass=mkPath(wob(arcPts(330,330,118,Math.PI*.72,Math.PI*2.28,48,0),1,3,5));
  P.neck=mkPath([[272,418],[270,452],[390,452],[388,418]]);
  P.base1=mkPath([[282,472],[378,472]]);
  P.base2=mkPath([[292,492],[368,492]]);
  P.fil=mkPath([[300,452],[300,360],[318,336],[336,372],[352,336],[360,452]]);
  P.rays=[];
  for(let i=0;i<9;i++){
    const aa=-Math.PI*.95+i*(Math.PI*.9/8);
    P.rays.push(mkPath([[330+Math.cos(aa)*158,330+Math.sin(aa)*158],[330+Math.cos(aa)*204,330+Math.sin(aa)*204]]));
  }
  return P;
})();
const STYLES=[
 ['Isometric Illustration',C.blue,C.cream],['Earthy Organic',C.sage,C.ink],['Soft 3D Coral',C.coral,C.white],
 ['Sketch Notebook',C.paper,C.blue],['Hand-Drawn Education',C.white,C.ink],['Bauhaus Poster',C.yellow,C.red],
 ['Cut Paper Collage',C.pink,C.navy],['Doodle Color Pop',C.teal,C.yellow],['Editorial Flat Vector',C.cream,C.navy],
 ['Inkwash Journal','#CFC9BC',C.ink],['Ivory Navy Gold',C.navy,'#D9B44A'],['Minimal Yellow Line',C.yellow,C.ink],
 ['Navy & Red Editorial',C.navy,C.red],['Triangle Badges',C.cream,C.orange],
 ['Whiteboard A',C.white,C.ink],['Whiteboard B',C.white,C.blue],['Whiteboard C',C.white,C.red],
 ['Whiteboard D',C.white,C.teal],['Whiteboard E',C.white,C.orange]
];
function motif(g,k,x,y,w,h,col,t,seed){
  g.save();g.beginPath();g.rect(x,y,w,h);g.clip();
  g.translate(x+w/2,y+h/2-8);
  g.fillStyle=col;g.strokeStyle=col;g.lineWidth=4;
  const m=k%7,s=Math.sin(t*2+seed)*.5;
  if(m===0){g.beginPath();g.arc(0,0,26,0,7);g.fill()}
  else if(m===1){tri(g,0,0,30,t*.8+seed,col)}
  else if(m===2){g.rotate(.4+s*.2);g.fillRect(-24,-24,48,48)}
  else if(m===3){for(let i=-2;i<=2;i++){g.beginPath();g.moveTo(-40,i*14);g.lineTo(40,i*14+s*10);g.stroke()}}
  else if(m===4){g.beginPath();for(let i=-40;i<=40;i+=4){const yy=Math.sin(i*.12+t*3+seed)*14;i===-40?g.moveTo(i,yy):g.lineTo(i,yy)}g.stroke()}
  else if(m===5){g.beginPath();g.arc(-14,0,20,0,7);g.arc(16,4,16,0,7);g.fill()}
  else{g.beginPath();g.moveTo(-34,22);g.lineTo(0,-26);g.lineTo(34,22);g.closePath();g.stroke()}
  g.restore();
}
function sD(g,t){
  const s=t-15;
  g.fillStyle=C.cream;g.fillRect(0,0,W,H);
  if(s<4.2){
    const pen=[
      [BULB.glass,.25,1.5,C.ink],[BULB.neck,1.4,1.8,C.ink],[BULB.base1,1.7,2.0,C.ink],[BULB.base2,1.9,2.2,C.ink],
      [BULB.fil,2.1,2.9,C.red]
    ];
    let tip=null;
    pen.forEach(p=>{const q=prog(s,p[1],p[2]);const r=strokePath(g,p[0],eIO(q),p[3],7);if(r&&q>0&&q<1)tip=r});
    BULB.rays.forEach((r,i)=>{
      const a=2.7+i*.1,q=prog(s,a,a+.35);
      const rr=strokePath(g,r,eOut(q),C.yellow,9);if(rr&&q>0&&q<1)tip=rr;
    });
    const glow=prog(s,2.9,3.4);
    if(glow>0){const gr=g.createRadialGradient(330,330,0,330,330,190);gr.addColorStop(0,'rgba(247,196,23,'+(.55*glow)+')');gr.addColorStop(1,'rgba(247,196,23,0)');g.fillStyle=gr;g.fillRect(100,100,460,460)}
    if(tip){g.save();g.translate(tip[0],tip[1]);g.rotate(-.9);g.fillStyle=C.blue;g.fillRect(0,-5,70,10);g.fillStyle=C.ink;g.beginPath();g.moveTo(0,-5);g.lineTo(-14,0);g.lineTo(0,5);g.fill();g.restore()}
    const a1=eOut(prog(s,.4,1.0)),a2=eOut(prog(s,1.2,1.8)),a3=eOut(prog(s,2.4,3.0));
    txt(g,'DRAWN.',640,250-(1-a1)*40,150,C.ink,{a:a1,mw:580});
    txt(g,'NOT STOCK.',640,400-(1-a2)*40,150,C.red,{a:a2,mw:580});
    txt(g,'Every scene is original artwork,',650,470,24,C.ink,{f:F_MONO,a:a3,mw:590});
    txt(g,'revealed stroke by stroke',650,508,24,C.ink,{f:F_MONO,a:a3,mw:590});
    txt(g,'as the narration reaches it.',650,546,24,C.ink,{f:F_MONO,a:a3,mw:590});
    txt(g,'No stock footage. No synthetic presenter.',650,610,18,C.blue,{f:F_MONO,w:'600',a:prog(s,3.3,3.8),mw:590});
  } else {
    const e=s-4.2;
    const count=clamp(Math.floor((e-.1)/.17)+1,0,19);
    txt(g,String(count),50,134,104,C.ink,{});
    txt(g,'STYLES.',50+tw(g,'19',104)+24,134,104,C.red,{a:prog(e,.1,.5),mw:700});
    const x0=50,y0=156,tw0=224,th=106,gx=15,gy=12;
    for(let i=0;i<19;i++){
      const st=.1+i*.17,p=Math.max(0,eBack(prog(e,st,st+.4)));
      if(p<=0)continue;
      const col=i%5,row=Math.floor(i/5);
      const x=x0+col*(tw0+gx),y=y0+row*(th+gy);
      const flash=e>5.2&&((Math.floor(e*6)+i)%7===0);
      const bg=flash?STYLES[i][2]:STYLES[i][1],fg=flash?STYLES[i][1]:STYLES[i][2];
      g.save();g.translate(x+tw0/2,y+th/2);g.scale(p,p);g.translate(-tw0/2,-th/2);
      g.fillStyle=bg;g.fillRect(0,0,tw0,th);
      motif(g,i,0,0,tw0,th,fg,t,i);
      txt(g,STYLES[i][0].toUpperCase(),10,th-10,13,fg,{f:F_MONO,w:'700',ls:1});
      g.restore();
    }
    const ep=Math.max(0,eBack(prog(e,3.5,4.0)));
    g.save();g.translate(x0+4*(tw0+gx)+tw0/2,y0+3*(th+gy)+th/2);g.scale(ep,ep);g.translate(-tw0/2,-th/2);
    g.fillStyle=C.red;g.fillRect(0,0,tw0,th);
    txt(g,'YOURS.',tw0/2,th/2+16,52,C.cream,{al:'center'});g.restore();
  }
}

/* ---------- E: edit anything (25 - 32) ---------- */
const STEPS=['SOURCES','TEMPLATE','AI AGENT','EDITOR'];
const PAL=[[C.red,C.yellow,C.blue],[C.teal,C.coral,C.navy],[C.orange,C.sage,C.ink],[C.blue,C.pink,C.yellow]];
function sE(g,t){
  const s=t-25;
  g.fillStyle=C.ink;g.fillRect(0,0,W,H);
  STEPS.forEach((n,i)=>{
    const p=Math.max(0,eBack(prog(s,.1+i*.14,.5+i*.14)));
    const on=s>.55*i+.2;
    const w=250,x=60+i*(w+28),y=70;
    g.save();g.translate(x+w/2,y+25);g.scale(p,p);g.translate(-w/2,-25);
    g.fillStyle=on?C.yellow:'#2b2d33';g.fillRect(0,0,w,50);
    txt(g,n,w/2,33,19,on?C.ink:'#8a8c93',{al:'center',f:F_MONO,w:'700',ls:3});
    g.restore();
  });
  const wp=Math.max(0,eBack(prog(s,.9,1.5)));
  const wx=60,wy=170,ww=760,wh=470;
  g.save();g.translate(wx+ww/2,wy+wh/2);g.scale(wp,wp);g.translate(-ww/2,-wh/2);
  g.fillStyle='rgba(0,0,0,.5)';g.fillRect(12,14,ww,wh);
  g.fillStyle=C.cream;g.fillRect(0,0,ww,wh);
  g.fillStyle=C.paper;g.fillRect(0,0,ww,36);
  ['#E8382B','#F7C417','#2FA6A0'].forEach((c,i)=>{g.fillStyle=c;g.beginPath();g.arc(20+i*22,18,6,0,7);g.fill()});
  const pi=Math.floor(Math.max(0,s-2.4)/1.1)%PAL.length,pal=PAL[pi];
  g.fillStyle=C.white;g.fillRect(24,58,500,330);
  g.fillStyle=pal[0];g.fillRect(24,58,500,16);
  g.fillStyle=pal[1];g.beginPath();g.arc(190,232,90,0,7);g.fill();
  tri(g,360,232,80,s*.6,pal[2]);
  g.fillStyle=pal[2];g.fillRect(24,340,500,48);
  txt(g,'HOW IT WORKS',40,376,34,C.cream,{});
  g.fillStyle='#d9d3c1';g.fillRect(540,58,196,330);
  txt(g,'PALETTE',556,86,13,'#5a5a52',{f:F_MONO,w:'700',ls:2});
  pal.forEach((c,i)=>{g.fillStyle=c;g.fillRect(556+i*56,100,46,46)});
  txt(g,'LOGO',556,184,13,'#5a5a52',{f:F_MONO,w:'700',ls:2});
  const lg=Math.max(0,eBack(prog(s,3.4,3.9)));
  g.save();g.translate(580,226);g.scale(lg,lg);g.fillStyle=C.ink;g.fillRect(-24,-24,48,48);txt(g,'YOU',0,7,19,C.yellow,{al:'center'});g.restore();
  txt(g,'TIMING',556,284,13,'#5a5a52',{f:F_MONO,w:'700',ls:2});
  const kn=.2+.6*(Math.sin(s*1.7)*.5+.5);
  g.fillStyle='#b7b09c';g.fillRect(556,306,150,6);g.fillStyle=C.red;g.fillRect(556,306,150*kn,6);
  g.beginPath();g.arc(556+150*kn,309,10,0,7);g.fill();
  for(let i=0;i<8;i++){
    const th=eOut(prog(s,1.5+i*.08,1.8+i*.08));
    g.fillStyle=i===(Math.floor(s*1.5)%8)?C.red:'#bdb6a3';
    g.fillRect(24+i*62,412,54*th,40);
  }
  g.restore();
  const cx=lerp(480,590,eIO(prog(s,2.0,2.8)))+Math.sin(s*3)*4,cy=lerp(560,206,eIO(prog(s,2.0,2.8)))+Math.cos(s*3)*3;
  if(s>1.8&&s<4.8){g.save();g.translate(cx,cy);g.fillStyle=C.red;g.beginPath();g.moveTo(0,0);g.lineTo(0,26);g.lineTo(8,19);g.lineTo(14,32);g.lineTo(20,29);g.lineTo(14,17);g.lineTo(24,17);g.closePath();g.fill();g.restore()}
  const hp=eOut(prog(s,.8,1.4));
  txt(g,'EDIT',880,300-(1-hp)*50,120,C.cream,{a:hp,mw:360});
  txt(g,'ANYTHING.',880,410-(1-hp)*50,98,C.yellow,{a:hp,mw:360});
  txt(g,'Text. Visuals. Timing.',880,470,22,C.cream,{f:F_MONO,a:prog(s,1.6,2.1),mw:370});
  txt(g,'Your logo on every plan.',880,512,22,C.cream,{f:F_MONO,a:prog(s,3.3,3.8),mw:370});
  txt(g,'Your colours on every scene.',880,554,22,C.cream,{f:F_MONO,a:prog(s,3.7,4.2),mw:370});
  const tp=prog(s,5.0,5.4);
  if(tp>0){
    g.fillStyle=C.blue;g.fillRect(880,590,380,60*eExpo(tp));
    txt(g,'MP4 · UP TO 1440p',900,628,22,C.cream,{f:F_MONO,w:'700',a:tp,mw:340});
  }
}

/* ---------- F: numbers (32 - 37) ---------- */
function sF(g,t){
  const s=t-32;
  g.fillStyle=C.white;g.fillRect(0,0,W,H);
  const T=[
    ['MINUTES',null,C.red,C.cream,'upload to video'],
    ['20',20,C.blue,C.cream,'narration languages'],
    ['2,800+',2800,C.yellow,C.ink,'videos created'],
    ['1,500+',1500,C.ink,C.yellow,'creators on board']
  ];
  const cw=W/4;
  T.forEach((c,i)=>{
    const p=eExpo(prog(s,.15+i*.28,.7+i*.28));
    const h=H*p;
    g.fillStyle=c[2];g.fillRect(i*cw,H-h,cw+1,h);
    if(p>.5){
      let label=c[0];
      if(c[1]){
        const q=eOut(prog(s,.5+i*.28,1.6+i*.28));
        const v=Math.round(c[1]*q);
        label=c[1]>=1000?v.toLocaleString('en-US')+'+':String(v);
      }
      txt(g,label,i*cw+cw/2,H/2+30,150,c[3],{al:'center',a:clamp((p-.5)*3),mw:cw-36});
      txt(g,c[4].toUpperCase(),i*cw+cw/2,H/2+84,15,c[3],{al:'center',f:F_MONO,w:'700',a:clamp((p-.6)*3),mw:cw-36});
    }
  });
  const cut=prog(s,3.7,4.1);
  if(cut>0){
    g.fillStyle=C.ink;g.fillRect(0,H/2-70*cut,W,140*cut);
    txt(g,'STOP SPENDING WEEKS.',W/2,H/2+22,76,C.cream,{al:'center',a:cut,mw:1120});
  }
}

/* ---------- G: outro (37 - 40) ---------- */
function sG(g,t){
  const s=t-37;
  g.fillStyle=C.ink;g.fillRect(0,0,W,H);
  const burst=prog(s,.0,.6);
  const R=rng(3);
  for(let i=0;i<46;i++){
    const a=R()*7,d=eOut(burst)*(180+R()*520),sz=8+R()*22;
    g.save();g.translate(640+Math.cos(a)*d,330+Math.sin(a)*d*.7);g.rotate(a+s*2);
    g.globalAlpha=1-prog(s,1.2,2.2);
    g.fillStyle=[C.red,C.yellow,C.blue,C.cream][i%4];
    if(i%3===0){g.beginPath();g.arc(0,0,sz*.6,0,7);g.fill()}else g.fillRect(-sz/2,-sz/2,sz,sz*(i%2?1:.4));
    g.restore();
  }
  g.globalAlpha=1;
  const k=Math.max(0,eElastic(prog(s,.15,1.0)));
  g.save();g.translate(640,340);g.scale(k,k);
  txt(g,'DISTILBOOK',0,40,190,C.cream,{al:'center',mw:1100});
  g.restore();
  const u=eExpo(prog(s,.9,1.5));
  g.fillStyle=C.yellow;g.fillRect(640-420*u,372,840*u,10);
  txt(g,'Turn documents into animated explainer videos.',640,448,28,C.cream,{al:'center',f:F_MONO,a:prog(s,1.2,1.7),mw:1100});
  const bp=Math.max(0,eBack(prog(s,1.7,2.2)));
  g.save();g.translate(640,540);g.scale(bp,bp);
  g.fillStyle=C.red;g.fillRect(-170,-34,340,68);
  txt(g,'TRY FOR FREE',0,12,36,C.cream,{al:'center',ls:3});
  g.restore();
  txt(g,'distilbook.com',640,640,20,C.cream,{al:'center',f:F_MONO,w:'600',ls:4,a:prog(s,2.1,2.5)*.8});
}

/* ---------- master ---------- */
function render(g,t){
  t=clamp(t,0,DUR-.0001);
  if(t<4.5)sA(g,t);else if(t<9)sB(g,t);else if(t<15)sC(g,t);
  else if(t<25)sD(g,t);else if(t<32)sE(g,t);else if(t<37)sF(g,t);else sG(g,t);
  WIPES.forEach(w=>wipe(g,t,w[0],w[1]));
  grain(g,t);
  hud(g,t);
}

/* ---------- score: synthesized, C minor, 120 bpm ---------- */
const BPM=120,BEAT=60/BPM;
const mtof=m=>440*Math.pow(2,(m-69)/12);
function noiseBuf(ac,sec){
  const b=ac.createBuffer(1,Math.floor(ac.sampleRate*sec),ac.sampleRate),d=b.getChannelData(0);
  const R=rng(99);for(let i=0;i<d.length;i++)d[i]=R()*2-1;return b;
}
function impulse(ac,sec,decay){
  const n=Math.floor(ac.sampleRate*sec),b=ac.createBuffer(2,n,ac.sampleRate),R=rng(5);
  for(let c=0;c<2;c++){const d=b.getChannelData(c);for(let i=0;i<n;i++)d[i]=(R()*2-1)*Math.pow(1-i/n,decay)}
  return b;
}
function buildScore(ac,out,off){
  const T0=ac.currentTime+.08;
  const at=x=>T0+x-off;
  const nb=noiseBuf(ac,2);
  const verb=ac.createConvolver();verb.buffer=impulse(ac,2.2,2.6);
  const vg=ac.createGain();vg.gain.value=.28;verb.connect(vg);vg.connect(out);
  const bus=ac.createGain();bus.gain.value=.9;bus.connect(out);bus.connect(verb);

  function tone(x,dur,freq,type,vol,lp,atk){
    if(x+dur<off)return;
    const s=Math.max(x,off),o=ac.createOscillator(),f=ac.createBiquadFilter(),g=ac.createGain();
    o.type=type;o.frequency.value=freq;f.type='lowpass';f.frequency.value=lp||2000;
    const a=atk||.01,st=at(s);
    g.gain.setValueAtTime(0,st);g.gain.linearRampToValueAtTime(vol,st+a);
    g.gain.exponentialRampToValueAtTime(.0001,at(x+dur));
    o.connect(f);f.connect(g);g.connect(bus);o.start(st);o.stop(at(x+dur)+.05);
  }
  function noise(x,dur,type,freq,vol,sweepTo){
    if(x<off)return;
    const s=ac.createBufferSource(),f=ac.createBiquadFilter(),g=ac.createGain();
    s.buffer=nb;f.type=type;f.frequency.setValueAtTime(freq,at(x));
    if(sweepTo)f.frequency.exponentialRampToValueAtTime(sweepTo,at(x+dur));
    g.gain.setValueAtTime(vol,at(x));g.gain.exponentialRampToValueAtTime(.0001,at(x+dur));
    s.connect(f);f.connect(g);g.connect(bus);s.start(at(x),0,dur);
  }
  function riser(x,dur){
    if(x<off)return;
    const s=ac.createBufferSource(),f=ac.createBiquadFilter(),g=ac.createGain();
    s.buffer=nb;f.type='bandpass';f.Q.value=3;
    f.frequency.setValueAtTime(300,at(x));f.frequency.exponentialRampToValueAtTime(7000,at(x+dur));
    g.gain.setValueAtTime(.0001,at(x));g.gain.exponentialRampToValueAtTime(.35,at(x+dur));
    g.gain.linearRampToValueAtTime(0,at(x+dur+.02));
    s.connect(f);f.connect(g);g.connect(bus);s.start(at(x),0,dur+.05);
  }
  function kick(x,vol){
    if(x<off)return;
    const o=ac.createOscillator(),g=ac.createGain();
    o.frequency.setValueAtTime(150,at(x));o.frequency.exponentialRampToValueAtTime(40,at(x+.18));
    g.gain.setValueAtTime(vol,at(x));g.gain.exponentialRampToValueAtTime(.0001,at(x+.3));
    o.connect(g);g.connect(bus);o.start(at(x));o.stop(at(x+.32));
  }
  function boom(x){
    kick(x,1.0);noise(x,.9,'lowpass',2500,.7,80);
    tone(x,2.2,mtof(24),'sine',.7,300,.005);
  }

  /* drone, swells with the reel */
  if(off<40){
    const s=Math.max(0,off),st=at(s);
    [24,31].forEach((m,i)=>{
      const o=ac.createOscillator(),f=ac.createBiquadFilter(),g=ac.createGain();
      o.type='sawtooth';o.frequency.value=mtof(m);f.type='lowpass';
      f.frequency.setValueAtTime(180,st);f.frequency.linearRampToValueAtTime(900,at(25));f.frequency.linearRampToValueAtTime(260,at(40));
      g.gain.setValueAtTime(0,st);g.gain.linearRampToValueAtTime(.16-i*.06,st+1.2);g.gain.setValueAtTime(.16-i*.06,at(36));g.gain.linearRampToValueAtTime(0,at(40));
      o.connect(f);f.connect(g);g.connect(bus);o.start(st);o.stop(at(40)+.1);
    });
  }

  /* string-like ostinato: 8ths to 15s, 16ths to 32s, long notes after */
  const ARP=[48,51,55,58,55,51,50,53,58,62,58,53];
  let step=0;
  for(let x=0;x<37;x+=BEAT/2){
    const sixt=x>=15&&x<32;
    const n=ARP[step%ARP.length]+((x>=25&&x<32)?12:0);
    const vol=lerp(.05,.17,clamp(x/30));
    const lp=lerp(700,3600,clamp(x/28));
    tone(x,BEAT*.9,mtof(n),'sawtooth',vol,lp,.012);
    if(sixt)tone(x+BEAT/4,BEAT*.4,mtof(n+12),'triangle',vol*.9,lp,.005);
    step++;
  }

  /* percussion */
  for(let b=0;b<80;b++){
    const x=b*BEAT;
    if(x>=9&&x<37)kick(x,x>=15?.9:.5);
    if(x>=25&&x<37&&b%2===1){noise(x,.18,'bandpass',1800,.45);noise(x,.1,'highpass',6000,.2)}
    if(x>=15&&x<37)for(let k=0;k<4;k++){noise(x+k*BEAT/4,.05,'highpass',8000,k%2?.07:.12)}
    if(x>=4&&x<9&&b%2===0)noise(x,.06,'highpass',7000,.12);
  }
  /* tick pulse of the opening */
  for(let x=1;x<4.4;x+=BEAT/2)tone(x,.06,1760,'square',.03,5000,.002);

  /* wipe risers and impacts */
  WIPES.forEach(w=>{riser(w[0]-1.1,1.1);boom(w[0])});

  /* stamp on APPROVED, sparkle on the logo burst */
  noise(13.6,.25,'lowpass',1200,.8,100);kick(13.6,1.1);
  [0,4,7,12,16].forEach((m,i)=>tone(37.25+i*.12,1.6,mtof(72+m),'triangle',.12,5000,.005));

  /* final chord */
  [36,43,48,51,55,60].forEach(m=>tone(37,3.0,mtof(m),'sawtooth',.09,1800,.02));
  return bus;
}

/* ---------- embeddable player: one instance per [data-motion-reel] ---------- */
let CURRENT=null;
function mount(root){
  if(root.__mounted)return;root.__mounted=true;
  const q=s=>root.querySelector(s);
  const cv=q('canvas'),g=cv.getContext('2d');
  const playBtn=q('[data-act=play]'),scrub=q('[data-act=scrub]'),clock=q('[data-act=clock]'),
    muteBtn=q('[data-act=mute]'),veil=q('[data-act=veil]');
  const POSTER=parseFloat(root.dataset.poster||'24.3');
  let ac=null,master=null,bus=null,t0=0,pos=POSTER,playing=false,muted=false,raf=0,started=false;
  const api={pause:()=>pause()};

  function fmt(t){return '0:'+pad2(Math.floor(t))}
  function draw(t){
    try{render(g,t)}catch(e){console.error(e)}
    scrub.value=String(Math.round(t/DUR*1000));
    scrub.setAttribute('aria-valuetext',fmt(t)+' of 0:40');
    clock.textContent=fmt(t)+' / 0:40';
  }
  function ensureAudio(){
    if(ac)return;
    const AC=window.AudioContext||window.webkitAudioContext;
    ac=new AC();
    const comp=ac.createDynamicsCompressor();comp.threshold.value=-14;comp.ratio.value=4;
    master=ac.createGain();master.gain.value=muted?0:.8;
    master.connect(comp);comp.connect(ac.destination);
  }
  function stopAudio(){if(bus){try{bus.disconnect()}catch(e){}bus=null}}
  function label(){
    playBtn.textContent=playing?'Pause':(started&&pos>=DUR-.05?'Replay':'Play');
    playBtn.setAttribute('aria-pressed',String(playing));
  }
  function startAt(p){
    if(CURRENT&&CURRENT!==api)CURRENT.pause();
    CURRENT=api;
    ensureAudio();
    if(ac.state==='suspended')ac.resume();
    stopAudio();
    pos=p;bus=buildScore(ac,master,p);
    t0=ac.currentTime+.08-p;
    playing=true;started=true;veil.hidden=true;label();
    cancelAnimationFrame(raf);tick();
  }
  function pause(){
    if(!playing)return;
    pos=clamp(ac.currentTime-t0,0,DUR);
    playing=false;stopAudio();cancelAnimationFrame(raf);label();draw(pos);
  }
  function tick(){
    if(!playing)return;
    const t=ac.currentTime-t0;
    if(t>=DUR){playing=false;pos=DUR-.01;stopAudio();label();draw(pos);return}
    draw(t);raf=requestAnimationFrame(tick);
  }
  function seek(t){
    t=clamp(t,0,DUR-.01);
    if(playing)startAt(t);else{pos=t;draw(t)}
  }
  playBtn.addEventListener('click',()=>{
    if(playing)pause();else startAt(!started||pos>=DUR-.05?0:pos);
  });
  veil.addEventListener('click',()=>startAt(0));
  scrub.addEventListener('input',()=>seek(parseInt(scrub.value,10)/1000*DUR));
  muteBtn.addEventListener('click',()=>{
    muted=!muted;muteBtn.textContent=muted?'Sound off':'Sound on';
    muteBtn.setAttribute('aria-pressed',String(!muted));
    if(master)master.gain.value=muted?0:.8;
  });
  root.addEventListener('keydown',e=>{
    if(e.target&&/INPUT|BUTTON/.test(e.target.tagName))return;
    if(e.code==='ArrowRight')seek((playing?ac.currentTime-t0:pos)+2);
    if(e.code==='ArrowLeft')seek((playing?ac.currentTime-t0:pos)-2);
  });
  document.addEventListener('visibilitychange',()=>{if(document.hidden)pause()});
  if('IntersectionObserver' in window){
    new IntersectionObserver(es=>{es.forEach(en=>{if(!en.isIntersecting)pause()})},{threshold:.15}).observe(root);
  }
  const faces=['150px Anton','20px "JetBrains Mono"','700 20px "JetBrains Mono"'];
  draw(POSTER);
  Promise.race([Promise.all(faces.map(f=>document.fonts.load(f))),new Promise(r=>setTimeout(r,2500))])
    .catch(()=>{}).then(()=>{if(!playing&&!started)draw(POSTER)});
}
function mountAll(){document.querySelectorAll('[data-motion-reel]').forEach(mount)}
window.MotionReel={mount:mount,mountAll:mountAll};
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',mountAll);else mountAll();
})();
