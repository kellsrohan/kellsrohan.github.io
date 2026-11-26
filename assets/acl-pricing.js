/* ACL pricing helper: total is prominent, GST statement, estimates labelled, no drip pricing.
   Legal draft — review with a lawyer before relying on it. */
(function () {
  var GST = "Not registered for GST, so no GST is charged.";
  var ACL = "Our services come with guarantees that cannot be excluded under the Australian Consumer Law.";
  function ready(fn) {
    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", fn);
    else fn();
  }
  function ensureNote(el, cls, text) {
    var n = el.querySelector("." + cls);
    if (!n) {
      n = document.createElement("p");
      n.className = cls;
      el.appendChild(n);
    }
    n.textContent = text;
  }
  function enhance(el) {
    if (el.getAttribute("data-acl-enhanced") === "1") return;
    var total = el.getAttribute("data-total");
    var period = el.getAttribute("data-period") || "";
    var from = el.getAttribute("data-from") === "true";
    var fromOk = el.getAttribute("data-from-available") === "true";
    var estimate = el.getAttribute("data-estimate") === "true";
    var currency = el.getAttribute("data-currency") || "AUD";
    var breakdown = el.getAttribute("data-breakdown") || "";
    if (!el.querySelector(".nc-price-total") && total) {
      var t = document.createElement("div");
      t.className = "nc-price-total";
      var label = (from && fromOk ? "From " : "") + (currency === "AUD" ? "A$" : "$") + total;
      if (period) label += "/" + period;
      t.textContent = label;
      el.prepend(t);
    }
    if (from && !fromOk) {
      var warn = el.querySelector(".nc-price-total");
      if (warn) warn.setAttribute("data-from-invalid", "1");
    }
    if (breakdown && !el.querySelector(".nc-price-breakdown")) {
      var b = document.createElement("div");
      b.className = "nc-price-breakdown";
      b.textContent = breakdown;
      el.appendChild(b);
    }
    ensureNote(el, "nc-price-gst", GST);
    ensureNote(el, "nc-price-acl", ACL);
    if (estimate) {
      ensureNote(el, "nc-price-est", "This is an estimate only. The final amount is confirmed in writing.");
    }
    el.setAttribute("data-acl-enhanced", "1");
  }
  ready(function () {
    document.querySelectorAll("[data-acl-price]").forEach(enhance);
  });
  window.ncEnhanceAclPrices = function (root) {
    (root || document).querySelectorAll("[data-acl-price]").forEach(enhance);
  };
})();
