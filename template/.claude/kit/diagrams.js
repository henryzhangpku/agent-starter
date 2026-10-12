// diagrams v1: draws Mermaid diagrams big and readable, click for full screen, plus the light/dark toggle.
// Copy next to look.css and include on every page that shows a diagram:  <script src="/static/diagrams.js" defer></script>
// Finds <pre class="mermaid"> and <code class="language-mermaid"> blocks (what markdown renderers emit).
(function () {
  "use strict";
  var root = document.documentElement;
  try { var saved = localStorage.getItem("theme"); if (saved) root.dataset.theme = saved; } catch (e) {}

  function toggle() {
    var b = document.createElement("button");
    b.className = "theme-toggle"; b.type = "button";
    var label = function () { b.textContent = root.dataset.theme === "dark" ? "Light" : "Dark"; };
    label();
    b.onclick = function () {
      root.dataset.theme = root.dataset.theme === "dark" ? "light" : "dark";
      try { localStorage.setItem("theme", root.dataset.theme); } catch (e) {}
      label(); draw(true);
    };
    document.body.appendChild(b);
  }

  var sources = [];
  function collect() {
    document.querySelectorAll("pre.mermaid, code.language-mermaid").forEach(function (el) {
      var host = el.tagName === "CODE" && el.parentElement.tagName === "PRE" ? el.parentElement : el;
      var box = document.createElement("div");
      box.className = "diagram"; box.title = "Click for full screen";
      var hint = document.createElement("div");
      hint.className = "diagram-hint"; hint.textContent = "Click the diagram for full screen";
      host.replaceWith(box); box.after(hint);
      sources.push({ box: box, text: el.textContent });
      box.addEventListener("click", function () { full(box); });
    });
  }

  function full(box) {
    var svg = box.querySelector("svg"); if (!svg) return;
    var over = document.createElement("div");
    over.className = "diagram-full"; over.appendChild(svg.cloneNode(true));
    var close = function () { over.remove(); document.removeEventListener("keydown", esc); };
    var esc = function (e) { if (e.key === "Escape") close(); };
    over.addEventListener("click", close); document.addEventListener("keydown", esc);
    document.body.appendChild(over);
  }

  var n = 0;
  function draw(again) {
    if (!window.mermaid || !sources.length) return;
    window.mermaid.initialize({
      startOnLoad: false, securityLevel: "strict",
      theme: root.dataset.theme === "dark" ? "dark" : "neutral",
      themeVariables: { fontSize: "16px", fontFamily: "Geist, system-ui, sans-serif" },
      flowchart: { useMaxWidth: false, htmlLabels: true, nodeSpacing: 40, rankSpacing: 50 },
    });
    sources.forEach(function (s) {
      window.mermaid.render("dgm" + (n++), s.text).then(function (r) { s.box.innerHTML = r.svg; })
        .catch(function (e) { s.box.innerHTML = "<pre>" + s.text.replace(/</g, "&lt;") + "</pre>"; });
    });
  }

  function start() {
    toggle(); collect();
    if (!sources.length) return;
    if (window.mermaid) return draw();
    var s = document.createElement("script");
    s.src = "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js";
    s.onload = function () { draw(); };
    s.onerror = function () { /* offline: the source text stays visible inside each box */
      sources.forEach(function (x) { x.box.innerHTML = "<pre>" + x.text.replace(/</g, "&lt;") + "</pre>"; });
    };
    document.head.appendChild(s);
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start); else start();
})();
