(function(){
  var input=document.querySelector("[data-skills-search]");
  if(!input) return;
  var items=[].slice.call(document.querySelectorAll("[data-skill-item]"));
  var empty=document.querySelector("[data-empty]");
  var count=document.querySelector("[data-search-count]");
  var total=items.length;
  function norm(s){ return (s||"").toLowerCase(); }
  function filter(){
    var q=norm(input.value).trim();
    var n=0;
    items.forEach(function(el){
      var hay=norm([el.getAttribute("data-name"),el.getAttribute("data-keywords"),el.getAttribute("data-category")].join(" "));
      var ok=!q || hay.indexOf(q)!==-1;
      el.hidden=!ok;
      if(ok) n++;
    });
    if(count) count.textContent=q?(n+" of "+total+" shown"):(total+" in this list");
    if(empty) empty.classList.toggle("is-visible", n===0);
    document.body.classList.toggle("is-filtering", !!q);
  }
  input.addEventListener("input", filter);
  filter();
})();
