(function(){
  var form=document.getElementById("hire-enquiry");
  if(!form) return;
  form.addEventListener("submit", function(e){
    e.preventDefault();
    if(form.website_hp && form.website_hp.value) return;
    var name=(form.name.value||"").trim();
    var email=(form.email.value||"").trim();
    var subject=(form.subject.value||"").trim();
    var need=(form.need.value||"").trim();
    var msg=form.querySelector("[data-form-msg]");
    if(!name||!email||!subject||!need){
      if(msg) msg.textContent="Please complete every required field.";
      return;
    }
    var body=[
      "Name: "+name,
      "Email: "+email,
      "Subject: "+subject,
      "",
      "What you need:",
      need
    ].join("\r\n");
    window.location.href="mailto:support@rohankells.com?subject="+encodeURIComponent(subject)+"&body="+encodeURIComponent(body);
  });
})();
