(function(){
  document.querySelectorAll("form.cf").forEach(function(form){
    form.addEventListener("submit", function(e){
      e.preventDefault();
      if(form.website_hp && form.website_hp.value) return;
      var msg=form.querySelector(".form-msg, [data-form-msg]");
      if(!form.checkValidity()){
        form.reportValidity();
        if(msg) msg.textContent="Please complete every required field.";
        return;
      }
      var kind=(form.getAttribute("data-form")|| (form.querySelector("[name=type]") && form.querySelector("[name=type]").value) || "enquiry");
      var subject="Rohan Kells — "+kind;
      var lines=[];
      var fd=new FormData(form);
      fd.forEach(function(value, key){
        if(key==="website_hp"||key==="consent") return;
        if(!String(value).trim()) return;
        lines.push(key+": "+value);
      });
      if(!lines.length){
        if(msg) msg.textContent="Please complete every required field.";
        return;
      }
      if(msg) msg.textContent="Your mail application will open with a structured message to support@rohankells.com. There is no form server.";
      window.location.href="mailto:support@rohankells.com?subject="+encodeURIComponent(subject)+"&body="+encodeURIComponent(lines.join("\r\n"));
    });
  });
})();
