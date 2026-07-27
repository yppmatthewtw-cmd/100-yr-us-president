/* R5 — R4 plus: dark/light theme, per-president expand/collapse inside PANE 1,
   deeper EASY green, curated EASY-exit triggers, and Fed hike/cut markers on PANE 3 bars.
   PANE 1  current president's index line, with all 25 predecessors overlaid for
           context and the current term highlighted; month-resolution X axis.
   PANE 3  vertically compact stack of all 26 terms on the SAME axis (one page),
           current term highlighted; each row expands in place.
   PANE 2  at-now cross-section (rendered last, at the bottom of the page).      */
(function () {
  var NS = "http://www.w3.org/2000/svg";
  var A = DATA.anchor, TERMS = A.terms, AN = A.anchor;
  var CD0 = -90, CD1 = 1461;
  function cssv(n, fb) {
    var v = getComputedStyle(document.documentElement).getPropertyValue(n).trim();
    return v || fb;
  }
  var ZC, ZBG, THEME = {};
  function readTheme() {
    ZC = { E: cssv("--easy-strip", "#12a06a"), U: cssv("--unc-strip", "#c99a2e"), H: cssv("--hard-strip", "#d2566c") };
    ZBG = { E: cssv("--easy-band", "rgba(18,160,106,.30)"), U: cssv("--unc-band", "rgba(230,178,61,.15)"), H: cssv("--hard-band", "rgba(242,107,127,.17)") };
    THEME = {
      ink: cssv("--chart-ink", "#c3d2e8"), grid: cssv("--chart-grid", "rgba(255,255,255,.055)"),
      gridY: cssv("--chart-grid-y", "rgba(255,255,255,.2)"), ms: cssv("--chart-ms", "rgba(127,180,255,.32)"),
      zero: cssv("--chart-zero", "rgba(255,255,255,.5)"), halo: cssv("--chart-halo", "#05070c"),
      hi: cssv("--chart-hi", "#fff"), prev: cssv("--chart-prev", "#7f93b3"),
      band: cssv("--chart-band", "rgba(255,255,255,.03)"), future: cssv("--chart-future", "rgba(255,255,255,.055)"),
      now: cssv("--chart-now", "#7fd4ff")
    };
  }
  readTheme();
  var ZN = { E: "EASY", U: "UNCERTAIN", H: "HARD" };
  var IG = Date.UTC(2025, 0, 20);
  var ECOL = { A: "#3987e5", B: "#d95926", C: "#9085e9" };
  var showEngines = true;
  // presidents expanded in PANE 1 get a distinct highlight colour (validated set)
  var HL = ["#3987e5", "#d95926", "#9085e9", "#d55181", "#1aa3b8", "#c98500"];
  var sel = [];                       // names of presidents highlighted in PANE 1
  function selColor(n) { var i = sel.indexOf(n); return i < 0 ? null : HL[i % HL.length]; }

  function el(t, a) { var e = document.createElementNS(NS, t); for (var k in a) e.setAttribute(k, a[k]); return e; }
  function tx(e, s) { e.textContent = s; return e; }
  function fmtA(iso) { return iso.slice(0, 7).replace("-", "."); }

  /* ---- month ticks across the whole term ---- */
  var MONTHS = (function () {
    var out = [], d = new Date(Date.UTC(2024, 9, 1));           // Oct 2024
    var end = Date.UTC(2029, 2, 1);
    while (d.getTime() <= end) {
      var cd = Math.round((d.getTime() - IG) / 86400000);
      if (cd >= CD0 - 32 && cd <= CD1 + 32)
        out.push({ cd: cd, m: d.getUTCMonth() + 1, y: d.getUTCFullYear() });
      d = new Date(Date.UTC(d.getUTCFullYear(), d.getUTCMonth() + 1, 1));
    }
    return out;
  })();
  var YEARS = (function () {
    var m = {};
    MONTHS.forEach(function (t) { if (!m[t.y]) m[t.y] = { y: t.y, cd0: t.cd, cd1: t.cd }; else m[t.y].cd1 = t.cd; });
    return Object.keys(m).map(function (k) { return m[k]; });
  })();

  /* Draw the month/year axis. Returns the height it consumed. */
  function monthAxis(svg, mL, iw, yTop, opts) {
    opts = opts || {};
    var W = iw, xs = function (cd) { return mL + (cd - CD0) / (CD1 - CD0) * iw; };
    MONTHS.forEach(function (t) {
      var x = xs(t.cd);
      if (x < mL - 1 || x > mL + iw + 1) return;
      var jan = t.m === 1;
      svg.appendChild(el("line", { x1: x, y1: yTop, x2: x, y2: yTop + (jan ? 7 : 4),
        stroke: jan ? THEME.zero : THEME.gridY, "stroke-width": jan ? 1.2 : .8 }));
      if (opts.months !== false)
        svg.appendChild(tx(el("text", { x: x + (iw / MONTHS.length) / 2, y: yTop + 14, "text-anchor": "middle",
          fill: jan ? THEME.ink : "var(--muted)", "font-size": "7.6",
          "font-weight": jan ? "800" : "400" }), t.m));
    });
    if (opts.years !== false) YEARS.forEach(function (y) {
      var x1 = Math.max(xs(y.cd0), mL), x2 = Math.min(xs(y.cd1) + iw / MONTHS.length, mL + iw);
      if (x2 - x1 < 26) return;
      svg.appendChild(tx(el("text", { x: (x1 + x2) / 2, y: yTop + 26, "text-anchor": "middle",
        fill: THEME.ink, "font-size": "10", "font-weight": "800" }), y.y));
    });
    return opts.years === false ? 18 : 30;
  }

  /* Vertical guides: month grid + year boundaries + milestones + now */
  function guides(svg, mL, iw, top, h, opts) {
    opts = opts || {};
    var xs = function (cd) { return mL + (cd - CD0) / (CD1 - CD0) * iw; };
    MONTHS.forEach(function (t) {
      var x = xs(t.cd);
      if (x < mL || x > mL + iw) return;
      svg.appendChild(el("line", { x1: x, y1: top, x2: x, y2: top + h,
        stroke: t.m === 1 ? THEME.gridY : THEME.grid,
        "stroke-width": t.m === 1 ? 1 : .6 }));
    });
    A.milestones.forEach(function (m, i) {
      var x = xs(m.cd);
      svg.appendChild(el("line", { x1: x, y1: top, x2: x, y2: top + h,
        stroke: m.cd === 0 ? THEME.zero : THEME.ms,
        "stroke-width": m.cd === 0 ? 1.3 : 1, "stroke-dasharray": m.cd === 0 ? "" : "4 3" }));
      if (opts.msLabels) {
        var y = top - 26 + (i % 2) * 12;
        var anc = i === 0 ? "start" : (i === A.milestones.length - 1 ? "end" : "middle");
        var lb = el("text", { x: x, y: y, "text-anchor": anc, fill: THEME.ink, "font-size": "9.5", "font-weight": "700" });
        tx(lb, m.label);
        var ttl = el("title"); ttl.textContent = m.date + " · " + m.note; lb.appendChild(ttl);
        svg.appendChild(lb);
      }
    });
    var xn = xs(AN.cd_now);
    svg.appendChild(el("line", { x1: xn, y1: top, x2: xn, y2: top + h, stroke: THEME.now, "stroke-width": 1.5 }));
    return xn;
  }

  /* ================= PANE 1 ================= */
  function drawPane1() {
    var host = document.getElementById("p1-chart"); if (!host) return;
    host.innerHTML = "";
    var cur = TERMS.filter(function (t) { return t.name === AN.name; })[0];
    var W = 1000, mL = 42, mR = 12, mT = 52, axisH = 32;
    var ih = 250, stripH = 16, gapS = 10;
    var H = mT + ih + gapS + stripH + axisH + 12;
    var iw = W - mL - mR;
    var xs = function (cd) { return mL + (cd - CD0) / (CD1 - CD0) * iw; };
    var Y = function (v) { return mT + ih - (v / 100) * ih; };
    var svg = el("svg", { viewBox: "0 0 " + W + " " + H, role: "img",
      "aria-label": "PANE 1 現任總統真實時間軸的 Easy/Hard 指數，並疊上 25 屆前任作對比" });

    [[70, 100, "E"], [40, 70, "U"], [0, 40, "H"]].forEach(function (b) {
      svg.appendChild(el("rect", { x: mL, y: Y(b[1]), width: iw, height: Y(b[0]) - Y(b[1]), fill: ZBG[b[2]], opacity: .45 }));
    });
    [0, 40, 70, 100].forEach(function (v) {
      svg.appendChild(el("line", { x1: mL, y1: Y(v), x2: mL + iw, y2: Y(v), stroke: THEME.grid, "stroke-width": .8, "stroke-dasharray": "4 4" }));
      svg.appendChild(tx(el("text", { x: mL - 6, y: Y(v) + 4, "text-anchor": "end", fill: "var(--muted)", "font-size": "9.5" }), v));
    });
    guides(svg, mL, iw, mT, ih, { msLabels: true });

    // ---- 25 predecessors overlaid (context cloud) ----
    TERMS.forEach(function (T) {
      if (T.name === AN.name || !T.line) return;
      var d = T.line.map(function (p, i) { return (i ? "L" : "M") + xs(p.cd).toFixed(1) + " " + Y(p.v).toFixed(1); }).join("");
      var path = el("path", { d: d, fill: "none", stroke: THEME.prev, "stroke-width": .8, opacity: .17,
        "stroke-linejoin": "round", class: "p1-prev", "data-term": T.name });
      var ttl = el("title"); ttl.textContent = T.cn + " " + T.inaug.slice(0, 4) + "–" + T.end.slice(0, 4); path.appendChild(ttl);
      svg.appendChild(path);
    });
    // ---- presidents expanded in the list below: highlighted comparison lines ----
    sel.forEach(function (nm) {
      var T = TERMS.filter(function (x) { return x.name === nm; })[0];
      if (!T || !T.line) return;
      var col = selColor(nm);
      var d = T.line.map(function (p, i) { return (i ? "L" : "M") + xs(p.cd).toFixed(1) + " " + Y(p.v).toFixed(1); }).join("");
      svg.appendChild(el("path", { d: d, fill: "none", stroke: THEME.halo, "stroke-width": 4, opacity: .55, "stroke-linejoin": "round" }));
      svg.appendChild(el("path", { d: d, fill: "none", stroke: col, "stroke-width": 2, "stroke-linejoin": "round" }));
      // mark that president's EASY exits on the chart
      (T.easy_exits || []).forEach(function (ex) {
        var x = xs(ex.cd);
        if (x < mL || x > mL + iw) return;
        var pt = T.line.filter(function (q) { return q.cd >= ex.cd; })[0] || T.line[T.line.length - 1];
        svg.appendChild(el("circle", { cx: x, cy: Y(pt.v), r: 4.6, fill: "none", stroke: col, "stroke-width": 1.8 }));
        var mk = el("path", { d: "M" + (x - 4) + " " + (Y(pt.v) - 9) + "l4 5l4-5z", fill: col });
        var tl2 = el("title");
        tl2.textContent = T.cn + " 離開 EASY  " + ex.own + "\n觸發: " + ex.trigger_date + " " + ex.trigger;
        mk.appendChild(tl2); svg.appendChild(mk);
      });
      var last = T.line[T.line.length - 1];
      svg.appendChild(tx(el("text", { x: Math.min(xs(last.cd) + 7, mL + iw - 30), y: Y(last.v) + 3.5,
        fill: col, "font-size": "10", "font-weight": "800" }), T.cn));
    });

    // 26-term median
    if (A.median && A.median.length) {
      var md = A.median.map(function (p, i) { return (i ? "L" : "M") + xs(p.cd).toFixed(1) + " " + Y(p.med).toFixed(1); }).join("");
      svg.appendChild(el("path", { d: md, fill: "none", stroke: "#ffd479", "stroke-width": 1.8, "stroke-dasharray": "6 4", opacity: .85 }));
    }

    // ---- three engine lines (normalised to the canonical 40/70 bands) ----
    if (showEngines) ["A", "B", "C"].forEach(function (k) {
      var d = A.master.map(function (p, i) { return (i ? "L" : "M") + xs(p.cd).toFixed(1) + " " + Y(p[k + "m"]).toFixed(1); }).join("");
      var pa = el("path", { d: d, fill: "none", stroke: ECOL[k], "stroke-width": 1.3, opacity: .62, "stroke-linejoin": "round" });
      var tl = el("title"); tl.textContent = "引擎 " + k + "（標準化分數，21日平滑）"; pa.appendChild(tl);
      svg.appendChild(pa);
    });

    // ---- current president: bold highlighted line ----
    var pts = A.master;
    if (pts.length) {
      var d = pts.map(function (p, i) { return (i ? "L" : "M") + xs(p.cd).toFixed(1) + " " + Y(p.sm).toFixed(1); }).join("");
      svg.appendChild(el("path", { d: d, fill: "none", stroke: THEME.halo, "stroke-width": 5.4, "stroke-linejoin": "round", opacity: .85 }));
      svg.appendChild(el("path", { d: d, fill: "none", stroke: THEME.hi, "stroke-width": 2.6, "stroke-linejoin": "round" }));
      var last = pts[pts.length - 1];
      svg.appendChild(el("circle", { cx: xs(last.cd), cy: Y(last.sm), r: 4.4, fill: THEME.now, stroke: THEME.halo, "stroke-width": 1.6 }));
    }

    // ---- zone strip (current) ----
    var sy = mT + ih + gapS;
    cur.zones.forEach(function (z) {
      var x1 = xs(Math.max(z.cd0, CD0)), x2 = xs(Math.min(z.cd1, CD1));
      var r = el("rect", { x: x1, y: sy, width: Math.max(1, x2 - x1), height: stripH, fill: ZC[z.z], rx: 2 });
      var ttl = el("title"); ttl.textContent = ZN[z.z] + "  " + z.own0 + " → " + z.own1 + "\n" + (z.note || "");
      r.appendChild(ttl); svg.appendChild(r);
    });
    var xn = xs(AN.cd_now);
    svg.appendChild(el("rect", { x: xn, y: sy, width: xs(CD1) - xn, height: stripH, fill: THEME.future, rx: 2 }));
    svg.appendChild(tx(el("text", { x: (xn + xs(CD1)) / 2, y: sy + 11.5, "text-anchor": "middle", fill: "var(--muted)", "font-size": "8.6" }), "未來（未有數據）"));
    // now marker on top of everything
    svg.appendChild(el("line", { x1: xn, y1: mT, x2: xn, y2: sy + stripH, stroke: THEME.now, "stroke-width": 1.6 }));
    svg.appendChild(tx(el("text", { x: xn + 5, y: mT + 12, fill: THEME.now, "font-size": "9.6", "font-weight": "800" }), "現在 " + AN.now));

    // ---- numbered transition flags ----
    cur.transitions.forEach(function (t, i) {
      var x = xs(t.cd);
      svg.appendChild(el("line", { x1: x, y1: sy - 9, x2: x, y2: sy + stripH, stroke: THEME.hi, "stroke-width": 1, opacity: .8 }));
      var c = el("circle", { cx: x, cy: sy - 16, r: 8.4, fill: ZC[t.to], stroke: THEME.halo, "stroke-width": 1.5 });
      var ttl = el("title");
      ttl.textContent = "#" + (i + 1) + "  " + t.own + "  " + ZN[t.frm] + "→" + ZN[t.to] + "\n" + (t.reason || "") + (t.event ? "\n事件: " + t.event : "");
      c.appendChild(ttl); svg.appendChild(c);
      svg.appendChild(tx(el("text", { x: x, y: sy - 12.6, "text-anchor": "middle", fill: THEME.halo, "font-size": "9.4", "font-weight": "800" }), i + 1));
    });

    // ---- consensus vote strip: how many of the 3 engines said EASY / HARD ----
    var vy = sy + stripH + 3, vh = 11;
    A.master.forEach(function (p, i) {
      if (i % 2) return;
      var x1 = xs(p.cd), x2 = xs(p.cd + 2);
      var net = (p.ev || 0) - (p.hv || 0);
      var col = net > 0 ? "#2e9b6f" : (net < 0 ? "#d2566c" : "rgba(255,255,255,.10)");
      var op = Math.min(1, Math.abs(net) / 3 * .85 + .15);
      svg.appendChild(el("rect", { x: x1, y: vy, width: Math.max(1, x2 - x1), height: vh,
        fill: col, opacity: net === 0 ? .25 : op }));
    });
    svg.appendChild(tx(el("text", { x: mL - 6, y: vy + 8.6, "text-anchor": "end",
      fill: "var(--muted)", "font-size": "7.8", "font-weight": "700" }), "票數"));

    monthAxis(svg, mL, iw, vy + vh + 4, {});
    host.appendChild(svg);

    // ---- hover on PANE 1 ----
    var tip = document.createElement("div"); tip.className = "cy-tip"; tip.style.display = "none"; host.appendChild(tip);
    var cr = el("line", { x1: 0, y1: mT, x2: 0, y2: vy + vh, stroke: THEME.hi, "stroke-width": 1, opacity: 0 });
    svg.appendChild(cr); svg.style.cursor = "crosshair";
    svg.addEventListener("mousemove", function (e) {
      var r = svg.getBoundingClientRect();
      var cd = Math.round(CD0 + ((e.clientX - r.left) / r.width * W - mL) / iw * (CD1 - CD0));
      var best = null, bd = 1e9;
      A.master.forEach(function (p) { var k = Math.abs(p.cd - cd); if (k < bd) { bd = k; best = p; } });
      if (!best || bd > 20) { tip.style.display = "none"; cr.setAttribute("opacity", 0); return; }
      cr.setAttribute("x1", xs(best.cd)); cr.setAttribute("x2", xs(best.cd)); cr.setAttribute("opacity", .7);
      tip.style.display = "block";
      tip.innerHTML = '<div class="cy-tip-h">' + best.t + ' <span>(週期第 ' + best.cd + ' 日)</span></div>' +
        '<div class="cy-tip-r"><i style="background:#fff"></i><span class="cy-tip-n">整合指數</span><b>' + best.s.toFixed(0) + '</b>' +
        '<em class="z-' + best.z + '">' + ZN[best.z] + '</em></div>' +
        '<div class="cy-tip-r"><i style="background:' + ECOL.A + '"></i><span class="cy-tip-n">A Fable</span><b>' + best.A.toFixed(0) + '</b></div>' +
        '<div class="cy-tip-r"><i style="background:' + ECOL.B + '"></i><span class="cy-tip-n">B Sol</span><b>' + best.B.toFixed(0) + '</b></div>' +
        '<div class="cy-tip-r"><i style="background:' + ECOL.C + '"></i><span class="cy-tip-n">C Grok</span><b>' + best.C.toFixed(0) + '</b></div>' +
        '<div class="cy-tip-r" style="border-top:1px solid var(--line);margin-top:4px;padding-top:5px">' +
        '<span class="cy-tip-n">票數</span><b style="color:#2e9b6f">E' + best.ev + '</b><b style="color:#d2566c">H' + best.hv + '</b>' +
        '<span class="cy-tip-d">分歧 ' + best.spread.toFixed(0) + '</span></div>';
      tip.style.left = Math.max(12, Math.min(88, xs(best.cd) / W * 100)) + "%";
      tip.style.top = "6px";
    });
    svg.addEventListener("mouseleave", function () { tip.style.display = "none"; cr.setAttribute("opacity", 0); });

    var tt = document.getElementById("p1-tt");
    if (tt) tt.innerHTML = transTable(cur);
  }

  /* ---- transitions table (shared) ---- */
  function transTable(T) {
    if (!T.transitions.length)
      return '<p class="muted" style="margin:8px 0 0">任內無制度級轉區（全程 ' + ZN[T.zones[0].z] + '）。</p>';
    var rows = T.transitions.map(function (t, i) {
      return '<tr><td class="am-num"><span class="am-flag" style="background:' + ZC[t.to] + '">' + (i + 1) + '</span></td>' +
        '<td class="mono">' + t.own + '</td><td class="mono am-anchor-d">' + fmtA(t.anchor) + '</td>' +
        '<td><span class="zbadge ' + (t.frm === "E" ? "easy" : t.frm === "U" ? "unc" : "hard") + '">' + ZN[t.frm] + '</span>' +
        '<span class="am-arrow">→</span><span class="zbadge ' + (t.to === "E" ? "easy" : t.to === "U" ? "unc" : "hard") + '">' + ZN[t.to] + '</span></td>' +
        '<td class="am-reason">' + (t.reason || "—") + (t.event ? '<div class="am-ev">⚡ ' + t.event + '</div>' : "") + '</td></tr>';
    }).join("");
    return '<div class="pm-wrap"><table class="am-tt"><thead><tr><th>#</th><th>自家日期</th><th>對標現任</th><th>轉區</th><th>主因與大事件</th></tr></thead><tbody>' + rows + '</tbody></table></div>';
  }

  /* ---- PANE 1 president list: each expands to compare + show EASY-exit events ---- */
  function easyExitTable(T) {
    if (!T.easy_exits || !T.easy_exits.length)
      return '<p class="muted" style="margin:6px 0 0">此任期在本標準下<b>沒有 EASY 段</b>，故無「離開 EASY」事件。</p>';
    var rows = T.easy_exits.map(function (e, i) {
      return '<tr><td class="am-num"><span class="am-flag" style="background:' + ZC[e.to] + '">' + (i + 1) + '</span></td>' +
        '<td class="mono">' + e.own + '</td><td class="mono am-anchor-d">' + fmtA(e.anchor) + '</td>' +
        '<td><span class="zbadge easy">EASY</span><span class="am-arrow">→</span>' +
        '<span class="zbadge ' + (e.to === "U" ? "unc" : "hard") + '">' + ZN[e.to] + '</span></td>' +
        '<td class="am-reason"><b class="ex-trig">' + e.trigger + '</b>' +
        '<div class="am-ev">📅 ' + e.trigger_date + (e.detail ? ' · ' + e.detail : '') + '</div></td></tr>';
    }).join("");
    return '<div class="pm-wrap"><table class="am-tt ex-tt"><thead><tr><th>#</th><th>離場日</th><th>對標現任</th>' +
      '<th>轉往</th><th>促使離開 EASY 的重大事件</th></tr></thead><tbody>' + rows + '</tbody></table></div>';
  }

  function buildP1List() {
    var host = document.getElementById("p1-list"); if (!host) return;
    host.innerHTML = "";
    TERMS.slice().reverse().forEach(function (T) {
      var det = document.createElement("details");
      det.className = "p1-pcard" + (T.name === AN.name ? " is-cur" : "");
      det.id = "p1card-" + T.name.replace(/[^A-Za-z0-9]/g, "");
      var nEx = (T.easy_exits || []).length;
      det.innerHTML = '<summary class="p1-psum">' +
        '<span class="am-chev">▸</span>' +
        '<span class="p1-sw"></span>' +
        '<span class="p1-pn">' + (T.name === AN.name ? '<span class="cur-tag">現任</span> ' : '') + T.cn +
        '<small>' + T.inaug.slice(0, 4) + '–' + T.end.slice(0, 4) + '</small></span>' +
        '<span class="std-tag std-' + (T.standard.indexOf("整合") === 0 ? "c" : "r") + '">' + T.standard + '</span>' +
        '<span class="p1-ex">' + (nEx ? nEx + ' 次離開 EASY' : '無 EASY 段') + '</span></summary>' +
        '<div class="p1-pbody"></div>';
      host.appendChild(det);
      det.addEventListener("toggle", function () {
        var i = sel.indexOf(T.name);
        if (det.open) { if (i < 0) sel.push(T.name); }
        else if (i >= 0) sel.splice(i, 1);
        var col = selColor(T.name);
        det.querySelector(".p1-sw").style.background = col || "transparent";
        det.querySelector(".p1-sw").style.borderColor = col || "var(--line2)";
        if (det.open && !det.dataset.drawn) {
          det.querySelector(".p1-pbody").innerHTML = easyExitTable(T);
          det.dataset.drawn = "1";
        }
        drawPane1();
        document.querySelectorAll(".p1-pcard").forEach(function (d) {
          var nm = d.id.replace("p1card-", ""), c2 = null;
          TERMS.forEach(function (x) { if (x.name.replace(/[^A-Za-z0-9]/g, "") === nm) c2 = selColor(x.name); });
          var sw = d.querySelector(".p1-sw");
          sw.style.background = c2 || "transparent";
          sw.style.borderColor = c2 || "var(--line2)";
        });
      });
    });
  }

  var p1e = document.getElementById("p1-expand"), p1c = document.getElementById("p1-collapse");
  if (p1e) p1e.addEventListener("click", function () {
    var open = document.querySelectorAll(".p1-pcard:not([open])");
    for (var i = 0; i < Math.min(6, open.length); i++) open[i].open = true;   // colour set holds 6
  });
  if (p1c) p1c.addEventListener("click", function () {
    document.querySelectorAll(".p1-pcard[open]").forEach(function (d) { d.open = false; });
  });

  /* ================= PANE 3 — compact stack, all 26 on one screen ================= */
  var RH = 19, GAP = 4;
  function drawStack() {
    var host = document.getElementById("p3-stack"); if (!host) return;
    host.innerHTML = "";
    var W = 1000, mL = 116, mR = 78, mT = 46;
    var rows = TERMS.length, gh = rows * (RH + GAP);
    var axisH = 32, H = mT + gh + axisH + 10, iw = W - mL - mR;
    var xs = function (cd) { return mL + (cd - CD0) / (CD1 - CD0) * iw; };
    var svg = el("svg", { viewBox: "0 0 " + W + " " + H, role: "img",
      "aria-label": "PANE 3 全部 26 屆總統的資金區在同一時間軸上的壓縮對照" });
    guides(svg, mL, iw, mT, gh, { msLabels: true });

    TERMS.slice().reverse().forEach(function (T, ri) {
      var y = mT + ri * (RH + GAP);
      var isCur = T.name === AN.name;
      if (isCur) svg.appendChild(el("rect", { x: mL - 112, y: y - 2.5, width: W - mR - mL + 188, height: RH + 5,
        fill: "rgba(127,212,255,.11)", stroke: THEME.now, "stroke-width": 1.1, rx: 3 }));
      svg.appendChild(el("rect", { x: mL, y: y, width: iw, height: RH, fill: THEME.band, rx: 2 }));
      T.zones.forEach(function (z) {
        var x1 = xs(Math.max(z.cd0, CD0)), x2 = xs(Math.min(z.cd1, CD1));
        var r = el("rect", { x: x1, y: y, width: Math.max(1, x2 - x1), height: RH,
          fill: ZC[z.z], opacity: isCur ? 1 : (T.tier === "B" ? .82 : .95), rx: 1.5 });
        var ttl = el("title");
        ttl.textContent = T.cn + "  " + ZN[z.z] + "  " + z.own0 + " → " + z.own1 + "\n" + (z.note || "");
        r.appendChild(ttl); svg.appendChild(r);
      });
      if (isCur) {
        var xn2 = xs(AN.cd_now);
        svg.appendChild(el("rect", { x: xn2, y: y, width: xs(CD1) - xn2, height: RH, fill: "rgba(255,255,255,.05)", rx: 1.5 }));
      }
      // ---- Fed policy turning points written onto the bar ----
      var lastLx = -999;
      (T.fed_turns || []).forEach(function (f) {
        if (f.cd < CD0 || f.cd > CD1) return;
        var x = xs(f.cd), up = f.kind === "H";
        var col = up ? "#ff8f6b" : "#63e6c3";
        svg.appendChild(el("line", { x1: x, y1: y - 1, x2: x, y2: y + RH + 1,
          stroke: col, "stroke-width": 1.5, opacity: .95 }));
        var g = up ? "M" + (x - 3.6) + " " + (y - 2) + "l3.6-4.4l3.6 4.4z"
                   : "M" + (x - 3.6) + " " + (y + RH + 2) + "l3.6 4.4l3.6-4.4z";
        var tri = el("path", { d: g, fill: col });
        var tt2 = el("title");
        tt2.textContent = (up ? "▲ 開始加息  " : "▼ 開始減息  ") + f.date + "  " + f.label + "\n" + f.note;
        tri.appendChild(tt2); svg.appendChild(tri);
        if (x - lastLx > 30) {              // label only when there is room
          // flip the label to the left near the right edge so it never spills
          // out of the plot area into the at-now chip column
          var flip = x + 34 > mL + iw;
          svg.appendChild(tx(el("text", { x: x + (flip ? -4.5 : 4.5), y: y + RH - 4, fill: col,
            "text-anchor": flip ? "end" : "start",
            "font-size": "6.8", "font-weight": "800" }), (up ? "↑" : "↓") + f.date.slice(2, 7)));
          lastLx = x;
        }
      });
      // trough
      if (T.trough && T.trough.cd >= CD0 && T.trough.cd <= CD1) {
        var xt = xs(T.trough.cd);
        var p = el("path", { d: "M" + (xt - 3.4) + " " + (y + RH + 1) + "l3.4 4.4l3.4-4.4z", fill: T.trough.midterm_low ? "#ffd479" : THEME.hi, opacity: .95 });
        var t2 = el("title"); t2.textContent = "任內大底 " + T.trough.date + "（" + T.trough.year + "）" + T.trough.note; p.appendChild(t2);
        svg.appendChild(p);
      }
      // name
      var lb = el("text", { x: mL - 7, y: y + RH - 3.5, "text-anchor": "end",
        fill: isCur ? THEME.now : "var(--ink2)", "font-size": "9.6", "font-weight": isCur ? "800" : "500", style: "cursor:pointer" });
      tx(lb, (isCur ? "▶ " : "") + T.cn + " " + T.inaug.slice(2, 4) + "–" + T.end.slice(2, 4));
      lb.addEventListener("click", function () { openCard(T.name); });
      svg.appendChild(lb);
      // left bar encodes the STANDARD used, not the tier — that is the axis on which
      // these rows are NOT comparable (consensus vs A-calibrated reconstruction)
      var isComb = T.standard.indexOf("整合") === 0;
      var bar = el("rect", { x: mL - 4.5, y: y, width: 3.5, height: RH, rx: 1,
        fill: isComb ? "#7fd4ff" : "#4a5a72" });
      var bt = el("title"); bt.textContent = T.standard; bar.appendChild(bt);
      svg.appendChild(bar);
      // right: at-now chip
      if (T.at_now) {
        var z = T.at_now.z;
        svg.appendChild(el("rect", { x: W - mR + 4, y: y + 1, width: 62, height: RH - 2, rx: 3,
          fill: ZBG[z], stroke: ZC[z], "stroke-width": .9 }));
        svg.appendChild(tx(el("text", { x: W - mR + 35, y: y + RH - 4, "text-anchor": "middle",
          fill: ZC[z], "font-size": "8.4", "font-weight": "800" }), ZN[z].slice(0, 4) + " " + Math.round(T.at_now.v)));
      }
    });
    monthAxis(svg, mL, iw, mT + gh + 6, {});
    host.appendChild(svg);
  }

  /* ---- expandable detail cards (below the stack) ---- */
  function buildCards() {
    var host = document.getElementById("p3-cards"); if (!host) return;
    host.innerHTML = "";
    TERMS.slice().reverse().forEach(function (T) {
      var det = document.createElement("details");
      det.className = "am-card p3-card" + (T.name === AN.name ? " is-cur" : "");
      det.id = "card-" + T.name.replace(/[^A-Za-z0-9]/g, "");
      var tierCls = T.tier === "A" ? "A" : (T.tier === "B" ? "B" : "M");
      var chip = T.at_now
        ? '<span class="am-chip" style="background:' + ZBG[T.at_now.z] + ';color:' + ZC[T.at_now.z] + ';border-color:' + ZC[T.at_now.z] + '">同位 ' + T.at_now.own.slice(0, 7).replace("-", ".") + ' · ' + ZN[T.at_now.z] + ' ' + Math.round(T.at_now.v) + '</span>'
        : '<span class="am-chip am-chip-na">同位無數據</span>';
      det.innerHTML = '<summary class="am-sum p3-sum"><span class="am-chev">▸</span>' +
        '<span class="am-name">' + (T.name === AN.name ? '<span class="cur-tag">現任</span> ' : '') + T.cn +
        '<small>' + T.inaug.slice(0, 4) + '–' + T.end.slice(0, 4) + ' · ' + T.era + '</small></span>' +
        '<span class="sm-t sm-t-' + tierCls + '">' + T.tier + '</span>' + '<span class="std-tag std-' + (T.standard.indexOf('整合') === 0 ? 'c' : 'r') + '">' + T.standard + '</span>' + chip +
        '<span class="am-ntr">' + T.transitions.length + ' 次轉區</span></summary>' +
        '<div class="am-body"><div class="am-bigstrip"></div><div class="am-tt-wrap"></div>' +
        (T.trough ? '<p class="am-trough">▾ 任內大底 <b class="mono">' + T.trough.date + '</b>（' + T.trough.year + '，對標現任時間 <b class="mono">' + fmtA(T.trough.anchor) + '</b>）' + (T.trough.midterm_low ? ' <span class="cov-b">★中期年樣本</span>' : '') + ' — ' + T.trough.note + '</p>' : '') +
        '</div>';
      host.appendChild(det);
      det.addEventListener("toggle", function () {
        if (det.open && !det.dataset.drawn) {
          drawBigStrip(det.querySelector(".am-bigstrip"), T);
          det.querySelector(".am-tt-wrap").innerHTML = transTable(T);
          det.dataset.drawn = "1";
        }
      });
    });
  }

  function drawBigStrip(host, T) {
    host.innerHTML = "";
    var W = 1000, mL = 8, mR = 8, mT = 34, RHb = 30, axisH = 32;
    var H = mT + RHb + axisH + 6, iw = W - mL - mR;
    var xs = function (cd) { return mL + (cd - CD0) / (CD1 - CD0) * iw; };
    var svg = el("svg", { viewBox: "0 0 " + W + " " + H });
    guides(svg, mL, iw, mT, RHb, { msLabels: true });
    T.zones.forEach(function (z) {
      var x1 = xs(Math.max(z.cd0, CD0)), x2 = xs(Math.min(z.cd1, CD1));
      var r = el("rect", { x: x1, y: mT, width: Math.max(1, x2 - x1), height: RHb, fill: ZC[z.z], rx: 2 });
      var ttl = el("title"); ttl.textContent = ZN[z.z] + "  " + z.own0 + " → " + z.own1 + "\n" + (z.note || "");
      r.appendChild(ttl); svg.appendChild(r);
    });
    if (T.trough && T.trough.cd >= CD0 && T.trough.cd <= CD1)
      svg.appendChild(el("path", { d: "M" + (xs(T.trough.cd) - 4) + " " + (mT + RHb + 2) + "l4 5.4l4-5.4z", fill: T.trough.midterm_low ? "#ffd479" : THEME.hi }));
    T.transitions.forEach(function (t, i) {
      var x = xs(t.cd);
      svg.appendChild(el("line", { x1: x, y1: mT - 8, x2: x, y2: mT + RHb, stroke: THEME.hi, "stroke-width": 1, opacity: .7 }));
      var c = el("circle", { cx: x, cy: mT - 14, r: 8, fill: ZC[t.to], stroke: THEME.halo, "stroke-width": 1.4 });
      var ttl = el("title");
      ttl.textContent = "#" + (i + 1) + "  " + t.own + "  " + ZN[t.frm] + "→" + ZN[t.to] + "\n" + (t.reason || "") + (t.event ? "\n事件: " + t.event : "");
      c.appendChild(ttl); svg.appendChild(c);
      svg.appendChild(tx(el("text", { x: x, y: mT - 10.6, "text-anchor": "middle", fill: THEME.halo, "font-size": "9", "font-weight": "800" }), i + 1));
    });
    monthAxis(svg, mL, iw, mT + RHb + 4, {});
    host.appendChild(svg);
  }

  function openCard(name) {
    var id = "card-" + name.replace(/[^A-Za-z0-9]/g, "");
    var d = document.getElementById(id);
    if (!d) return;
    d.open = true;
    d.scrollIntoView({ behavior: "smooth", block: "center" });
  }

  var ea = document.getElementById("p3-expand"), ca = document.getElementById("p3-collapse");
  if (ea) ea.addEventListener("click", function () { document.querySelectorAll(".p3-card").forEach(function (d) { d.open = true; }); });
  if (ca) ca.addEventListener("click", function () { document.querySelectorAll(".p3-card").forEach(function (d) { d.open = false; }); });

  var etg = document.getElementById("p1-engines");
  if (etg) etg.addEventListener("click", function () {
    showEngines = !showEngines;
    etg.classList.toggle("on", showEngines);
    etg.textContent = showEngines ? "☑ 顯示 A/B/C 三引擎分線" : "☐ 顯示 A/B/C 三引擎分線";
    drawPane1();
  });

  // ---- dark / light theme ----
  function applyTheme(m) {
    document.documentElement.setAttribute("data-theme", m);
    try { localStorage.setItem("ehm-theme", m); } catch (e) {}
    var b = document.getElementById("theme-btn");
    if (b) b.textContent = m === "light" ? "🌙 深色模式" : "☀️ 淺色模式";
    readTheme();
    drawPane1(); drawStack();
    document.querySelectorAll(".p3-card[open]").forEach(function (d) {
      var nm = d.id.replace("card-", "");
      TERMS.forEach(function (T) {
        if (T.name.replace(/[^A-Za-z0-9]/g, "") === nm) drawBigStrip(d.querySelector(".am-bigstrip"), T);
      });
    });
  }
  var saved = null;
  try { saved = localStorage.getItem("ehm-theme"); } catch (e) {}
  // the design is dark-native; light is an explicit opt-in via the button (remembered)
  var initial = saved || "dark";
  document.documentElement.setAttribute("data-theme", initial);
  readTheme();
  var tb = document.getElementById("theme-btn");
  if (tb) {
    tb.textContent = initial === "light" ? "🌙 深色模式" : "☀️ 淺色模式";
    tb.addEventListener("click", function () {
      applyTheme(document.documentElement.getAttribute("data-theme") === "light" ? "dark" : "light");
    });
  }

  drawPane1();
  drawStack();
  buildCards();
  buildP1List();
})();
