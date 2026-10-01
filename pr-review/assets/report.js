/* pr-review report renderer — editable source for templates/report.html (inline copy). No dependencies, no network. */
(function () {
  function $(s) { return document.querySelector(s); }
  function esc(s) { return String(s == null ? "" : s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;"); }
  var data = JSON.parse(document.getElementById("review-data").textContent);
  // Rendering logic lives inline in templates/report.html; this file is the
  // maintained source. Copy its body into the template's <script> block.
})();
