(function(){
  function escapeHtml(s){
    return String(s).replace(/[&<>"']/g, function(c){
      return ({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"})[c];
    });
  }
  function render(out, docs, q){
    if(!out) return;
    q=(q||"").trim();
    if(!q){
      out.innerHTML="<p>Type a word or phrase to search the site.</p>";
      return;
    }
    var terms=q.toLowerCase().split(/\s+/).filter(Boolean);
    var hits=(docs||[]).filter(function(d){
      var hay=((d.t||"")+" "+(d.h||"")+" "+(d.x||"")+" "+(d.u||"")).toLowerCase();
      return terms.every(function(term){ return hay.indexOf(term)!==-1; });
    });
    if(!hits.length){
      out.innerHTML="<p>No pages matched “"+escapeHtml(q)+"”.</p>";
      return;
    }
    var html="<p>"+hits.length+" page"+(hits.length===1?"":"s")+" matched.</p><ul class=\"search-hits\">";
    hits.forEach(function(d){
      html+="<li><a href=\""+escapeHtml(d.u||"/")+"\"><strong>"+escapeHtml(d.t||d.h||d.u)+"</strong></a>";
      if(d.x) html+="<span>"+escapeHtml(d.x)+"</span>";
      html+="</li>";
    });
    html+="</ul>";
    out.innerHTML=html;
  }
  function bind(form){
    var input=form.querySelector("input[name=q], input[type=search]");
    var out=document.getElementById(form.getAttribute("data-search-out")||"") ||
            form.parentNode.querySelector(".search-out") ||
            document.getElementById("search-out");
    if(!input||!out) return;
    var inline=form.hasAttribute("data-inline-search");
    var docsCache=null;
    function load(){
      if(docsCache) return Promise.resolve(docsCache);
      return fetch("/assets/search-index.json",{headers:{Accept:"application/json"}})
        .then(function(r){ if(!r.ok) throw new Error("index"); return r.json(); })
        .then(function(data){ docsCache=data.docs||[]; return docsCache; });
    }
    function run(q){
      load().then(function(docs){ render(out, docs, q); })
        .catch(function(){
          out.innerHTML="<p>The search index could not be loaded. See the <a href=\"/sitemap/\">site map</a>.</p>";
        });
    }
    form.addEventListener("submit", function(e){
      if(inline){
        e.preventDefault();
        run(input.value);
      }
    });
    input.addEventListener("input", function(){
      if(inline) run(input.value);
    });
    var initial="";
    if(!inline){
      initial=new URLSearchParams(location.search).get("q")||"";
      if(initial) input.value=initial;
      run(initial);
    } else {
      out.innerHTML="";
    }
  }
  document.querySelectorAll("form[data-site-search]").forEach(bind);
})();
