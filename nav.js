(function(){
if(window.__ix)return;window.__ix=1;
var L=[['/','خانه'],['/prices.html','قیمت‌ها'],['/chart.html','نمودارها'],['/analysis.html','تحلیل و اخبار'],['/dealers.html','همکاران'],['/tools.html','ابزارها']];
var X=[['/bubble.html','حباب سکه و طلا'],['https://t.me/Irannerkhh_bot','ربات تلگرام'],['https://t.me/irannerkhh1','کانال تلگرام'],['https://www.instagram.com/irannerkhh/','اینستاگرام']];
var p=location.pathname.replace(/index\.html$/,'');
function on(h){if(h==='/')return p==='/'||p==='';if(h==='/analysis.html')return p.indexOf('/analysis')===0||p.indexOf('/posts/')===0;return p.indexOf(h.replace('.html',''))===0}
var I={home:'<path d="M3 11l9-8 9 8v10h-6v-6H9v6H3z"/>',chart:'<path d="M4 20V10M10 20V4M16 20v-8M22 20H2"/>',tools:'<path d="M14.7 6.3a4 4 0 0 0-5.4 5.4L3 18l3 3 6.3-6.3a4 4 0 0 0 5.4-5.4l-2.6 2.6-2.4-.6-.6-2.4z"/>',news:'<path d="M5 4h14v16H5zM8 8h8M8 12h8M8 16h5"/>',menu:'<path d="M4 6h16M4 12h16M4 18h16"/>',tg:'<path d="M21 4L3 11l6 2 2 6 3-4 5 3z"/>',ig:'<rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/>'};
function ic(n){return '<svg viewBox="0 0 24 24" aria-hidden="true">'+I[n]+'</svg>'}
function cur(h){return on(h)?' aria-current="page"':''}
var nav=L.map(function(l){return '<a href="'+l[0]+'"'+cur(l[0])+'>'+l[1]+'</a>'}).join('');
var dr='<h2>صفحه‌ها</h2>'+L.map(function(l){return '<a href="'+l[0]+'"'+cur(l[0])+'>'+l[1]+'</a>'}).join('')+'<h2>بیشتر</h2>'+X.map(function(l){return '<a href="'+l[0]+'"'+cur(l[0])+(l[0].indexOf('http')===0?' rel="noopener" target="_blank"':'')+'>'+l[1]+'</a>'}).join('');
var bn=[['/','home','خانه'],['/chart.html','chart','نمودار'],['/tools.html','tools','ابزارها'],['/analysis.html','news','اخبار']].map(function(b){return '<a class="ix-bn" href="'+b[0]+'"'+cur(b[0])+'>'+ic(b[1])+'<span>'+b[2]+'</span></a>'}).join('')+'<button class="ix-bn" id="ixMore" type="button" aria-label="بیشتر">'+ic('menu')+'<span>بیشتر</span></button>';
var logo='<a class="ix-logo" href="/" aria-label="ایران نرخ"><svg viewBox="0 0 32 32" fill="#D9B43B" aria-hidden="true"><rect x="3" y="18" width="6" height="11" rx="1"/><rect x="13" y="11" width="6" height="18" rx="1"/><rect x="23" y="4" width="6" height="25" rx="1"/></svg>ایران نرخ</a>';
document.querySelectorAll('body > header, .topbar').forEach(function(e){e.remove()});
var h=document.createElement('header');h.className='ix-hd';
h.innerHTML='<div class="ix-in">'+logo+'<nav class="ix-nav" aria-label="منوی اصلی">'+nav+'</nav><div class="ix-act"><a class="ix-ic ix-soc" href="https://t.me/irannerkhh1" rel="noopener" target="_blank" aria-label="تلگرام">'+ic('tg')+'</a><a class="ix-ic ix-soc" href="https://www.instagram.com/irannerkhh/" rel="noopener" target="_blank" aria-label="اینستاگرام">'+ic('ig')+'</a><button class="ix-ic" id="ixMenu" type="button" aria-label="باز کردن منو" aria-expanded="false">'+ic('menu')+'</button></div></div>';
var ov=document.createElement('div');ov.className='ix-ov';
var d=document.createElement('aside');d.className='ix-dr';d.id='ixDr';d.setAttribute('aria-label','منو');d.innerHTML=dr;
var b=document.createElement('nav');b.className='ix-bnav';b.setAttribute('aria-label','ناوبری پایین');b.innerHTML=bn;
document.body.insertBefore(h,document.body.firstChild);
document.body.appendChild(ov);document.body.appendChild(d);document.body.appendChild(b);
document.body.classList.add('ix-pad');
var m=document.getElementById('ixMenu');
function set(o){document.documentElement.classList.toggle('ix-open',o);document.body.classList.toggle('ix-lock',o);m.setAttribute('aria-expanded',o)}
m.onclick=function(){set(true)};document.getElementById('ixMore').onclick=function(){set(true)};
ov.onclick=function(){set(false)};d.addEventListener('click',function(e){if(e.target.tagName==='A')set(false)});
document.addEventListener('keydown',function(e){if(e.key==='Escape')set(false)});
if(!document.getElementById('ixFont')){var f=document.createElement('link');f.id='ixFont';f.rel='stylesheet';f.href='https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;700&display=swap';document.head.appendChild(f)}
})();
