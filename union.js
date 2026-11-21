/* قیمت‌های اتحادیه طلا و جواهر تهران (از union.json که ربات گوشی به‌روز می‌کند) */
window.IxUnion=function(cb){
  fetch('/union.json?t='+Date.now()).then(function(r){if(!r.ok)throw 0;return r.json()}).then(function(d){
    var age=(Date.now()-new Date(d.fetched).getTime())/60000;
    cb(d&&d.items&&d.items.gold18>0&&age<60?d:null);
  }).catch(function(){cb(null)});
};
