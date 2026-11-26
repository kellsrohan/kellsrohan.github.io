(function(){
  var btn=document.querySelector(".rk-menu-btn");
  if(!btn) return;
  btn.addEventListener("click",function(){
    var open=document.body.classList.toggle("nav-open");
    btn.setAttribute("aria-expanded", open ? "true" : "false");
  });
})();
(function(){
  var bg=document.querySelector(".page-bg");
  if(!bg) return;
  var reduce=window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if(reduce) return;
  window.addEventListener("pointermove", function(e){
    var x=(e.clientX/Math.max(window.innerWidth,1)-0.5)*16;
    var y=(e.clientY/Math.max(window.innerHeight,1)-0.5)*16;
    bg.style.backgroundPosition=x+"px "+y+"px";
  }, {passive:true});
})();
