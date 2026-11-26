/* Preference centre: reads ?token= and talks to /api/newsletter/preferences. */
(function () {
  function $(id) { return document.getElementById(id); }
  function ready(fn) {
    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", fn);
    else fn();
  }
  ready(function () {
    var params = new URLSearchParams(location.search);
    var token = params.get("token") || "";
    var form = $("pref-form");
    var status = $("pref-status");
    var tokenInput = $("pref-token");
    if (!form) return;
    if (tokenInput) tokenInput.value = token;
    if (!token) {
      if (status) {
        status.hidden = false;
        status.textContent = "Open this page from the link in your email so we can load your preferences. You can also use the unsubscribe link in any marketing email, which we honour immediately.";
      }
      return;
    }
    form.hidden = false;
    fetch("/api/newsletter/preferences?token=" + encodeURIComponent(token), { credentials: "same-origin" })
      .then(function (r) { return r.json().then(function (j) { return { ok: r.ok, j: j }; }); })
      .then(function (res) {
        if (!res.ok || !res.j || !res.j.ok) {
          if (status) { status.hidden = false; status.textContent = (res.j && res.j.error) || "This link is not valid. Use the latest email we sent you, or email us and we will honour your request immediately."; }
          form.hidden = true;
          return;
        }
        var topics = res.j.topics || [];
        form.querySelectorAll('input[name="topics"]').forEach(function (c) {
          c.checked = topics.indexOf(c.value) !== -1;
        });
        if (res.j.frequency) {
          var r = form.querySelector('input[name="frequency"][value="' + res.j.frequency + '"]');
          if (r) r.checked = true;
        }
      })
      .catch(function () {
        if (status) { status.hidden = false; status.textContent = "We could not load your preferences just now. Email us and we will honour your request immediately."; }
      });
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var fd = new FormData(form);
      var body = {
        token: token,
        topics: fd.getAll("topics"),
        frequency: fd.get("frequency") || "",
        unsubscribe_all: !!(e.submitter && e.submitter.name === "unsubscribe_all")
      };
      fetch("/api/newsletter/preferences", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "same-origin",
        body: JSON.stringify(body)
      }).then(function (r) { return r.json(); }).then(function (j) {
        if (status) {
          status.hidden = false;
          status.textContent = j && j.ok
            ? (body.unsubscribe_all ? "You are unsubscribed from all marketing email. This took effect immediately." : "Your preferences have been saved.")
            : (j && j.error) || "Something went wrong. Email us and we will help.";
        }
        if (j && j.ok && body.unsubscribe_all) form.hidden = true;
      }).catch(function () {
        if (status) { status.hidden = false; status.textContent = "Something went wrong. Email us and we will honour your request immediately."; }
      });
    });
  });
})();
