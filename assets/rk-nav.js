(function(){
  var btn=document.querySelector(".rk-menu-btn");
  if(!btn) return;
  btn.addEventListener("click",function(){
    var open=document.body.classList.toggle("nav-open");
    btn.setAttribute("aria-expanded", open ? "true" : "false");
  });
})();
