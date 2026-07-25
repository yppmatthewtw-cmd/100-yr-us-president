/* Unified presidency-cycle comparison charts.
   X = cycle day (Inauguration = 0). Y = Easy/Hard Index (0-100) or indexed NDX.
   Every president is one line on the SAME axis. */
(function () {
  var NS = "http://www.w3.org/2000/svg";
  var CY = DATA.cycle;
  var ORDER = ["Obama II", "Trump I", "Biden", "Trump II"];
  var COL = { "Obama II": "#3987e5", "Trump I": "#d95926", "Biden": "#9085e9", "Trump II": "#d55181" };
  var CN = { "Obama II": "奧巴馬 II", "Trump I": "特朗普 I", "Biden": "拜登", "Trump II": "特朗普 II" };
  var visible = {}, mode = "sm";
  ORDER.forEach(function (n) { visible[n] = !!CY.series[n]; });

  function el(t, a) { var e = document.createElementNS(NS, t); for (var k in a) e.setAttribute(k, a[k]); return e; }
  function txt(e, s) { e.textContent = s; return e; }

  var CD0 = -84, CD1 = 1461;

  function drawIndex(host) {
    host.innerHTML = "";
    var W = 1000, H = 440, mL = 50, mR = 104, mT = 52, mB = 62;
    var iw = W - mL - mR, ih = H - mT - mB;
    var X = function (cd) { return mL + (cd - CD0) / (CD1 - CD0) * iw; };
    var Y = function (v) { return mT + ih - (v / 100) * ih; };
    var svg = el("svg", { viewBox: "0 0 " + W + " " + H, role: "img",
      "aria-label": "四任總統在同一總統週期軸上的 Easy/Hard 指數比較" });

    // zone reference bands (status colours, low alpha — reference, not series identity).
    // Labels sit INSIDE the plot so the right gutter stays free for series direct labels.
    [[70, 100, "rgba(62,207,142,.10)", "EASY ≥70", "#3ecf8e"],
     [40, 70, "rgba(230,178,61,.09)", "UNCERTAIN 40–70", "#e6b23d"],
     [0, 40, "rgba(242,107,127,.10)", "HARD ≤40", "#f26b7f"]].forEach(function (b) {
      svg.appendChild(el("rect", { x: mL, y: Y(b[1]), width: iw, height: Y(b[0]) - Y(b[1]), fill: b[2] }));
      var lb = el("text", { x: mL + 7, y: Y(b[1]) + 13, fill: b[4], "font-size": "10", "font-weight": "800", opacity: .75 });
      svg.appendChild(txt(lb, b[3]));
    });
    [70, 40].forEach(function (v) {
      svg.appendChild(el("line", { x1: mL, y1: Y(v), x2: mL + iw, y2: Y(v), stroke: "rgba(255,255,255,.22)", "stroke-width": 1, "stroke-dasharray": "4 4" }));
    });
    // y ticks
    [0, 20, 40, 60, 80, 100].forEach(function (v) {
      svg.appendChild(txt(el("text", { x: mL - 9, y: Y(v) + 4, "text-anchor": "end", fill: "var(--muted)", "font-size": "10" }), v));
    });
    svg.appendChild(txt(el("text", { x: 14, y: mT + ih / 2, fill: "var(--ink2)", "font-size": "11", "font-weight": "700",
      transform: "rotate(-90 14 " + (mT + ih / 2) + ")", "text-anchor": "middle" }), "Easy / Hard 指數"));

    drawMilestones(svg, X, mT, ih, true);
    drawSeries(svg, X, Y, "index", mL, iw, mT, ih);
    host.appendChild(svg);
    attachHover(host, svg, X, Y, W, H, mL, iw, mT, ih, "index");
  }

  function drawNdx(host) {
    host.innerHTML = "";
    var W = 1000, H = 340, mL = 54, mR = 104, mT = 46, mB = 58;
    var iw = W - mL - mR, ih = H - mT - mB;
    var lo = 60, hi = 60;
    ORDER.forEach(function (n) {
      if (!CY.series[n] || !visible[n]) return;
      CY.series[n].forEach(function (p) { if (p.ix > hi) hi = p.ix; if (p.ix < lo) lo = p.ix; });
    });
    hi = Math.ceil(hi / 20) * 20; lo = Math.min(60, Math.floor(lo / 20) * 20);
    var X = function (cd) { return mL + (cd - CD0) / (CD1 - CD0) * iw; };
    var Y = function (v) { return mT + ih - (v - lo) / (hi - lo) * ih; };
    var svg = el("svg", { viewBox: "0 0 " + W + " " + H, role: "img",
      "aria-label": "四任總統在同一總統週期軸上的 NDX 表現比較（就職日=100）" });
    for (var g = lo; g <= hi; g += (hi - lo) / 5) {
      svg.appendChild(el("line", { x1: mL, y1: Y(g), x2: mL + iw, y2: Y(g), stroke: "var(--line)", "stroke-width": .7, opacity: .55 }));
      svg.appendChild(txt(el("text", { x: mL - 9, y: Y(g) + 4, "text-anchor": "end", fill: "var(--muted)", "font-size": "10" }), Math.round(g)));
    }
    svg.appendChild(el("line", { x1: mL, y1: Y(100), x2: mL + iw, y2: Y(100), stroke: "rgba(255,255,255,.3)", "stroke-width": 1.2, "stroke-dasharray": "5 4" }));
    svg.appendChild(txt(el("text", { x: mL + 7, y: Y(100) - 6, fill: "var(--ink2)", "font-size": "10", "font-weight": "700", opacity: .8 }), "就職日 = 100"));
    drawMilestones(svg, X, mT, ih, false);
    drawSeries(svg, X, Y, "ndx", mL, iw, mT, ih);
    host.appendChild(svg);
    attachHover(host, svg, X, Y, W, H, mL, iw, mT, ih, "ndx");
  }

  function drawMilestones(svg, X, mT, ih, withLabels) {
    CY.milestones.forEach(function (m, i) {
      var x = X(m.day);
      svg.appendChild(el("line", { x1: x, y1: mT, x2: x, y2: mT + ih,
        stroke: m.day === 0 ? "rgba(255,255,255,.42)" : "rgba(255,255,255,.20)",
        "stroke-width": m.day === 0 ? 1.4 : 1, "stroke-dasharray": m.day === 0 ? "" : "3 4" }));
      if (!withLabels) return;
      var row = i % 2;                       // stagger to avoid collisions
      var y = mT - 32 + row * 15;
      svg.appendChild(el("line", { x1: x, y1: y + 3, x2: x, y2: mT, stroke: "rgba(255,255,255,.16)", "stroke-width": .8 }));
      var anchor = i === 0 ? "start" : (i === CY.milestones.length - 1 ? "end" : "middle");
      var t = el("text", { x: x, y: y, "text-anchor": anchor, fill: "#c3d2e8", "font-size": "10", "font-weight": "700" });
      svg.appendChild(txt(t, m.label.split(" ")[0]));
    });
  }

  function drawSeries(svg, X, Y, kind, mL, iw, mT, ih) {
    var ends = [];
    ORDER.forEach(function (n) {
      var pts = CY.series[n];
      if (!pts || !visible[n]) return;
      var key = kind === "ndx" ? "ix" : (mode === "sm" ? "sm" : "s");
      if (kind !== "ndx" && mode === "raw") {
        var dr = pts.map(function (p, i) { return (i ? "L" : "M") + X(p.cd).toFixed(1) + " " + Y(p.s).toFixed(1); }).join("");
        svg.appendChild(el("path", { d: dr, fill: "none", stroke: COL[n], "stroke-width": .8, opacity: .28 }));
      }
      var d = pts.map(function (p, i) { return (i ? "L" : "M") + X(p.cd).toFixed(1) + " " + Y(p[key]).toFixed(1); }).join("");
      svg.appendChild(el("path", { d: d, fill: "none", stroke: COL[n], "stroke-width": 2,
        "stroke-linejoin": "round", "stroke-linecap": "round" }));
      var last = pts[pts.length - 1];
      ends.push({ n: n, x: X(last.cd), y: Y(last[key]) });
    });
    // de-overlap direct labels: cluster by x, then push apart vertically
    ends.sort(function (a, b) { return a.y - b.y; });
    var MINGAP = 14;
    ends.forEach(function (e, i) {
      e.ly = e.y;
      for (var j = 0; j < i; j++) {
        var o = ends[j];
        if (Math.abs(o.x - e.x) < 90 && Math.abs(o.ly - e.ly) < MINGAP) e.ly = o.ly + MINGAP;
      }
      e.ly = Math.max(mT + 8, Math.min(mT + ih - 4, e.ly));
    });
    ends.forEach(function (e) {
      svg.appendChild(el("circle", { cx: e.x, cy: e.y, r: 3.4, fill: COL[e.n], stroke: "#0b111b", "stroke-width": 1.6 }));
      if (Math.abs(e.ly - e.y) > 2) {   // leader line when the label was displaced
        svg.appendChild(el("line", { x1: e.x + 3, y1: e.y, x2: e.x + 6, y2: e.ly - 3,
          stroke: COL[e.n], "stroke-width": .9, opacity: .55 }));
      }
      var lab = el("text", { x: Math.min(e.x + 8, mL + iw + 5), y: e.ly + 3.5, fill: COL[e.n],
        "font-size": "10.5", "font-weight": "800" });
      svg.appendChild(txt(lab, CN[e.n] + (CY.meta[e.n].partial ? "＊" : "")));
    });
  }

  function attachHover(host, svg, X, Y, W, H, mL, iw, mT, ih, kind) {
    var tip = document.createElement("div"); tip.className = "cy-tip"; tip.style.display = "none"; host.appendChild(tip);
    var cross = el("line", { x1: 0, y1: mT, x2: 0, y2: mT + ih, stroke: "rgba(255,255,255,.5)", "stroke-width": 1, opacity: 0 });
    svg.appendChild(cross);
    var dots = [];
    svg.style.cursor = "crosshair";
    svg.addEventListener("mousemove", function (e) {
      var r = svg.getBoundingClientRect();
      var cd = Math.round(CD0 + ((e.clientX - r.left) / r.width * W - mL) / iw * (CD1 - CD0));
      if (cd < CD0 || cd > CD1) return;
      cross.setAttribute("x1", X(cd)); cross.setAttribute("x2", X(cd)); cross.setAttribute("opacity", 1);
      dots.forEach(function (d) { d.remove(); }); dots = [];
      var rows = [];
      ORDER.forEach(function (n) {
        var pts = CY.series[n]; if (!pts || !visible[n]) return;
        var best = null, bd = 1e9;
        for (var i = 0; i < pts.length; i++) { var dd = Math.abs(pts[i].cd - cd); if (dd < bd) { bd = dd; best = pts[i]; } }
        if (!best || bd > 25) return;
        var v = kind === "ndx" ? best.ix : (mode === "sm" ? best.sm : best.s);
        var dot = el("circle", { cx: X(best.cd), cy: Y(v), r: 4, fill: COL[n], stroke: "#0b111b", "stroke-width": 1.5 });
        svg.appendChild(dot); dots.push(dot);
        rows.push({ n: n, v: v, t: best.t, z: best.z });
      });
      if (!rows.length) { tip.style.display = "none"; return; }
      rows.sort(function (a, b) { return b.v - a.v; });
      var yy = Math.round(cd / 365.25 * 10) / 10;
      tip.style.display = "block";
      tip.innerHTML = '<div class="cy-tip-h">週期第 ' + cd + ' 日 <span>(就職後 ' + yy + ' 年)</span></div>' +
        rows.map(function (r) {
          return '<div class="cy-tip-r"><i style="background:' + COL[r.n] + '"></i>' +
            '<span class="cy-tip-n">' + CN[r.n] + '</span>' +
            '<b>' + r.v.toFixed(1) + '</b>' +
            '<em class="z-' + r.z + '">' + (r.z === "E" ? "EASY" : r.z === "U" ? "UNC" : "HARD") + '</em>' +
            '<span class="cy-tip-d">' + r.t + '</span></div>';
        }).join("");
      var px = X(cd) / W * 100;
      tip.style.left = Math.max(12, Math.min(88, px)) + "%";
      tip.style.top = "8px";
    });
    svg.addEventListener("mouseleave", function () {
      tip.style.display = "none"; cross.setAttribute("opacity", 0);
      dots.forEach(function (d) { d.remove(); }); dots = [];
    });
  }

  function redraw() {
    var a = document.getElementById("cy-index"), b = document.getElementById("cy-ndx");
    if (a) drawIndex(a);
    if (b) drawNdx(b);
  }

  // legend toggles + smoothing switch
  function buildLegend() {
    var host = document.getElementById("cy-legend"); if (!host) return;
    ORDER.forEach(function (n) {
      if (!CY.series[n]) return;
      var m = CY.meta[n];
      var b = document.createElement("button");
      b.className = "cy-lg on"; b.style.setProperty("--c", COL[n]);
      b.innerHTML = '<i></i><span>' + CN[n] + '</span><em>' + m.inaug.slice(0, 4) + '–' + m.end.slice(0, 4) +
        (m.partial ? ' ＊部分' : '') + '</em>';
      b.addEventListener("click", function () {
        visible[n] = !visible[n];
        b.classList.toggle("on", visible[n]);
        redraw();
      });
      host.appendChild(b);
    });
    var sw = document.getElementById("cy-smooth");
    if (sw) sw.addEventListener("click", function () {
      mode = mode === "sm" ? "raw" : "sm";
      sw.textContent = mode === "sm" ? "顯示：21日平滑" : "顯示：每日原始＋平滑";
      redraw();
    });
  }

  buildLegend();
  redraw();
})();
