(function(){
  var form=document.getElementById("hire-enquiry");
  if(!form) return;
  form.addEventListener("submit", function(e){
    e.preventDefault();
    if(form.website_hp && form.website_hp.value) return;
    var name=(form.name.value||"").trim();
    var email=(form.email.value||"").trim();
    var type=(form.work_type.value||"").trim();
    var budget=(form.budget.value||"").trim();
    var timeline=(form.timeline.value||"").trim();
    var brief=(form.brief.value||"").trim();
    if(!name||!email||!type||!budget||!timeline||!brief){
      var msg=form.querySelector("[data-form-msg]");
      if(msg) msg.textContent="Please complete every required field.";
      return;
    }
    var subject="Project enquiry — "+type+" — "+budget;
    var body=[
      "Name: "+name,
      "Email: "+email,
      "Work type: "+type,
      "Budget band: "+budget,
      "Timeline: "+timeline,
      "",
      "Brief:",
      brief
    ].join("\r\n");
    window.location.href="mailto:support@rohankells.com?subject="+encodeURIComponent(subject)+"&body="+encodeURIComponent(body);
  });
})();
