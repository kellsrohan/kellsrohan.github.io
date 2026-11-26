(function(){
  var root=document.querySelector("[data-status-page]");
  if(!root) return;
  function set(key, text, ok){
    var el=document.querySelector('[data-status="'+key+'"]');
    if(!el) return;
    el.textContent=text;
    el.classList.toggle("ok", ok===true);
    el.classList.toggle("down", ok===false);
  }
  function run(){
    set("website","Checking…");
    set("forms","Checking…");
    var checks=[
      {key:"website", url:"/"},
      {key:"forms", url:"/contact/"}
    ];
    Promise.all(checks.map(function(c){
      var start=performance.now();
      return fetch(c.url,{method:"GET", cache:"no-store"}).then(function(r){
        return {key:c.key, ok:r.ok, ms:Math.round(performance.now()-start)};
      }).catch(function(){ return {key:c.key, ok:false, ms:0}; });
    })).then(function(results){
      var site=results.find(function(r){ return r.key==="website"; });
      var contact=results.find(function(r){ return r.key==="forms"; });
      if(site){
        set("website", site.ok ? "Reachable" : "Not reachable", site.ok);
        set("ms", site.ok && site.ms ? site.ms+" ms" : "–", site.ok);
      }
      if(contact){
        set("forms", contact.ok ? "Contact page reachable" : "Contact page not reachable", contact.ok);
      }
      var time=document.querySelector('[data-status="time"]');
      if(time){
        time.textContent=new Date().toLocaleString("en-AU",{timeZone:"Australia/Sydney"})+" (Australia/Sydney)";
      }
    });
  }
  var btn=document.querySelector("[data-status-recheck]");
  if(btn) btn.addEventListener("click", run);
  run();
})();
