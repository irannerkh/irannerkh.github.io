/* نرخ‌های اتحادیه طلا و جواهر تهران: اول از شاخه‌ی data (سریع‌تر)، بعد از union.json خود سایت */
window.IxUnion=function(cb){
  var RAW='https://raw.githubusercontent.com/irannerkh/irannerkh.github.io/data/union.json';
  function ok(d){if(!d||!d.items||!(d.items.gold18>0))return null;return (Date.now()-new Date(d.fetched).getTime())<3600000?d:null}
  function load(u){return fetch(u+'?t='+Date.now(),{cache:'no-store'}).then(function(r){if(!r.ok)throw 0;return r.json()}).then(ok).catch(function(){return null})}
  Promise.all([load(RAW),load('/union.json')]).then(function(a){
    var d=(a[0]&&a[1])?(new Date(a[0].fetched)>=new Date(a[1].fetched)?a[0]:a[1]):(a[0]||a[1]);
    cb(d||null);
  });
};
