/* R9 — R7/R8 plus: 45 high-importance recurring nodes (score>60 from the 100-node
   scoring model) rendered as a dedicated PANE 1 layer (triangle markers + tooltip).
   itself as a lane-packed label with a leader line down to the exact point on the
   president's line (not only in tooltips / the table below).
   PANE 4 = compact toggle list of all 26 presidents with a single expand/collapse button.
   PANE 1 = every data line has its own toggle plus a single master button, and ALL zone
   transitions of the current + selected presidents are listed synchronously.
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

  // presidents expanded in PANE 1 get a distinct highlight colour (validated set)
  var HL = ["#3987e5", "#d95926", "#9085e9", "#d55181", "#1aa3b8", "#c98500", "#4fb3a3", "#b0587f"];
  var sel = [];                       // presidents toggled on from PANE 4
  function selColor(n) { var i = sel.indexOf(n); return i < 0 ? null : HL[i % HL.length]; }

  // every drawable data line in PANE 1 is a switchable layer
  var LAYERS = [
    { k: "master",  t: "現屆整合指數" },
    { k: "engines", t: "A/B/C 三引擎" },
    { k: "cloud",   t: "25 屆背景雲" },
    { k: "median",  t: "26 屆中位數" },
    { k: "strip",   t: "資金區色帶" },
    { k: "votes",   t: "共識票數帶" },
    { k: "flags",   t: "轉區旗標" },
    { k: "evlabels", t: "事件標籤(線上)" },
    { k: "hinodes", t: "重要節點(>60分)" }
  ];
  var layer = {};
  LAYERS.forEach(function (l) { layer[l.k] = true; });

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
        var y = (opts.msLabelY != null ? opts.msLabelY : top - 26) + (i % 2) * 12;
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
    var W = 1000, mL = 42, mR = 12, axisH = 32;
    var ih = 250, stripH = 16, gapS = 10;
    var iw = W - mL - mR;
    var xs = function (cd) { return mL + (cd - CD0) / (CD1 - CD0) * iw; };

    // ---------- collect every major event to render ON the chart ----------
    function lineV(T, cd) {
      var pt = (T.line || []).filter(function (q) { return q.cd >= cd; })[0];
      return pt ? pt.v : (T.line && T.line.length ? T.line[T.line.length - 1].v : 50);
    }
    function masterV(cd) {
      var best = null, bd = 1e9;
      A.master.forEach(function (p) { var k = Math.abs(p.cd - cd); if (k < bd) { bd = k; best = p; } });
      return best ? best.sm : 50;
    }
    function shortTxt(s, n) { s = s || ""; return s.length > n ? s.slice(0, n) + "…" : s; }
    var evts = [];
    if (layer.evlabels) {
      cur.transitions.forEach(function (x) {
        var ex = (cur.easy_exits || []).filter(function (e) { return e.own === x.own; })[0];
        var body = ex ? ex.trigger : (x.event ? x.event.replace(/^[-0-9/→ ]+\s*/, "") : (x.reason || ""));
        evts.push({ cd: x.cd, v: masterV(x.cd), col: THEME.now, halo: true, isCur: true,
          text: x.own.slice(2, 7) + " " + shortTxt(body, 12),
          full: cur.cn + "  " + x.own + "  " + ZN[x.frm] + "→" + ZN[x.to] + "\n" + (ex ? ex.trigger_date + " " + ex.trigger : (x.reason || "")), z: x.to });
      });
      sel.forEach(function (nm) {
        if (nm === cur.name) return;
        var T = TERMS.filter(function (q) { return q.name === nm; })[0];
        if (!T) return;
        var col = selColor(nm);
        (T.transitions || []).forEach(function (x) {
          var ex = (T.easy_exits || []).filter(function (e) { return e.own === x.own; })[0];
          var body = ex ? ex.trigger : (x.reason || "");
          evts.push({ cd: x.cd, v: lineV(T, x.cd), col: col, isCur: false,
            pres: T.cn.replace(/\s+/g, ""), date: x.own.slice(2, 7),
            text: T.cn + "·" + x.own.slice(2, 7) + " " + shortTxt(body, 9),
            full: T.cn + "  " + x.own + "  " + ZN[x.frm] + "→" + ZN[x.to] + "\n" +
                  (ex ? "觸發: " + ex.trigger_date + " " + ex.trigger + (ex.detail ? "\n" + ex.detail : "") : (x.reason || "")), z: x.to });
        });
      });
    }
    // ---------- lane allocation (greedy, current president first) ----------
    // dense mode: when many presidents are on, compact every label to 「總統·日期」
    // so ALL events still fit on the chart (full text remains in the tooltip)
    var dense = evts.length > 30;
    if (dense) evts.forEach(function (e) {
      e.text = e.isCur ? e.text.slice(0, 5) + " " + (e.z === "H" ? "▼H" : e.z === "E" ? "▲E" : "→U")
                       : e.pres + "·" + e.date;
    });
    var laneH = 13, CW = dense ? 7.4 : 7.9, PAD = dense ? 4 : 9;
    var nLanes = evts.length ? Math.min(12, Math.max(2, Math.ceil(evts.length / (dense ? 8 : 8)))) : 0;
    var laneEnd = [], placed = [], dropped = 0;
    for (var li = 0; li < nLanes; li++) laneEnd.push(-1e9);
    function widthOf(e) { return e.text.length * CW + PAD * 2; }
    function tryPlace(e) {
      var w = widthOf(e), x = xs(e.cd);
      var x0 = Math.max(mL, Math.min(x - w / 2, mL + iw - w));
      for (var li2 = 0; li2 < nLanes; li2++) {
        if (x0 > laneEnd[li2] + 4) { laneEnd[li2] = x0 + w; e.lane = li2; e.x0 = x0; e.w = w; placed.push(e); return true; }
      }
      // shifted placement: slide right after the least-advanced lane's end
      var best = 0;
      for (var li3 = 1; li3 < nLanes; li3++) if (laneEnd[li3] < laneEnd[best]) best = li3;
      var xs0 = laneEnd[best] + 4;
      if (xs0 + w <= mL + iw) {
        laneEnd[best] = xs0 + w; e.lane = best; e.x0 = xs0; e.w = w; placed.push(e); return true;
      }
      dropped++; return false;
    }
    evts.sort(function (a, b) { return a.cd - b.cd; });
    evts.filter(function (e) { return e.isCur; }).forEach(tryPlace);
    evts.filter(function (e) { return !e.isCur; }).forEach(tryPlace);
    // grow lanes until everything fits (hard cap 14)
    while (dropped > 0 && nLanes < 16) {
      nLanes++; laneEnd.push(-1e9);
      var retry = evts.filter(function (e) { return e.lane === undefined; });
      dropped = 0;
      retry.forEach(tryPlace);
    }
    var band = nLanes ? nLanes * laneH + 6 : 0;

    var mT = 52 + band;
    var hiRow = (layer.hinodes && A.hi_nodes && A.hi_nodes.length) ? 16 : 0;
    var H = mT + ih + gapS + stripH + axisH + 12 + hiRow;
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
    guides(svg, mL, iw, mT, ih, { msLabels: true, msLabelY: 16 });

    // ---- 25 predecessors overlaid (context cloud) ----
    if (layer.cloud) TERMS.forEach(function (T) {
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
      // mark EVERY zone transition of this president on the chart
      if (layer.flags) (T.transitions || []).forEach(function (tr, ti) {
        var x = xs(tr.cd);
        if (x < mL || x > mL + iw) return;
        var pt = T.line.filter(function (q) { return q.cd >= tr.cd; })[0] || T.line[T.line.length - 1];
        var isEx = tr.frm === "E";
        svg.appendChild(el("circle", { cx: x, cy: Y(pt.v), r: 4.4, fill: ZC[tr.to],
          stroke: col, "stroke-width": 1.6 }));
        if (isEx) {                       // EASY exits get an extra downward flag
          var mk = el("path", { d: "M" + (x - 4) + " " + (Y(pt.v) - 9) + "l4 5l4-5z", fill: col });
          var tl3 = el("title"); tl3.textContent = T.cn + " 離開 EASY " + tr.own; mk.appendChild(tl3);
          svg.appendChild(mk);
        }
        var tl2 = el("title");
        tl2.textContent = T.cn + "  " + tr.own + "  " + ZN[tr.frm] + "→" + ZN[tr.to] + "\n" + (tr.reason || "");
        svg.lastChild.appendChild ? null : null;
      });
      var last = T.line[T.line.length - 1];
      svg.appendChild(tx(el("text", { x: Math.min(xs(last.cd) + 7, mL + iw - 30), y: Y(last.v) + 3.5,
        fill: col, "font-size": "10", "font-weight": "800" }), T.cn));
    });

    // 26-term median
    if (layer.median && A.median && A.median.length) {
      var md = A.median.map(function (p, i) { return (i ? "L" : "M") + xs(p.cd).toFixed(1) + " " + Y(p.med).toFixed(1); }).join("");
      svg.appendChild(el("path", { d: md, fill: "none", stroke: "#ffd479", "stroke-width": 1.8, "stroke-dasharray": "6 4", opacity: .85 }));
    }

    // ---- three engine lines (normalised to the canonical 40/70 bands) ----
    if (layer.engines) ["A", "B", "C"].forEach(function (k) {
      var d = A.master.map(function (p, i) { return (i ? "L" : "M") + xs(p.cd).toFixed(1) + " " + Y(p[k + "m"]).toFixed(1); }).join("");
      var pa = el("path", { d: d, fill: "none", stroke: ECOL[k], "stroke-width": 1.3, opacity: .62, "stroke-linejoin": "round" });
      var tl = el("title"); tl.textContent = "引擎 " + k + "（標準化分數，21日平滑）"; pa.appendChild(tl);
      svg.appendChild(pa);
    });

    // ---- current president: bold highlighted line ----
    var pts = A.master;
    if (layer.master && pts.length) {
      var d = pts.map(function (p, i) { return (i ? "L" : "M") + xs(p.cd).toFixed(1) + " " + Y(p.sm).toFixed(1); }).join("");
      svg.appendChild(el("path", { d: d, fill: "none", stroke: THEME.halo, "stroke-width": 5.4, "stroke-linejoin": "round", opacity: .85 }));
      svg.appendChild(el("path", { d: d, fill: "none", stroke: THEME.hi, "stroke-width": 2.6, "stroke-linejoin": "round" }));
      var last = pts[pts.length - 1];
      svg.appendChild(el("circle", { cx: xs(last.cd), cy: Y(last.sm), r: 4.4, fill: THEME.now, stroke: THEME.halo, "stroke-width": 1.6 }));
    }

    // ---- zone strip (current) ----
    var sy = mT + ih + gapS;
    if (layer.strip) cur.zones.forEach(function (z) {
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
    if (layer.flags) cur.transitions.forEach(function (t, i) {
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
    if (layer.votes) A.master.forEach(function (p, i) {
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

    // ---- 45 high-importance recurring nodes (score>60), independent of the
    // current term's own transitions — these are STRUCTURAL calendar dates.
    // Drawn BELOW the vote strip so the two layers never overlap. ----
    if (layer.hinodes && A.hi_nodes && A.hi_nodes.length) {
      var hy0 = vy + vh + 3, hy1 = hy0 + 11;
      svg.appendChild(tx(el("text", { x: mL - 6, y: hy1 - 2, "text-anchor": "end",
        fill: "var(--muted)", "font-size": "7.5", "font-weight": "700" }), "重要節點"));
      A.hi_nodes.forEach(function (hn) {
        var x = xs(hn.cd);
        if (x < mL || x > mL + iw) return;
        var bandCol = hn.score >= 85 ? "#ff5d7a" : (hn.score >= 70 ? "#ffb454" : "#7fd4ff");
        svg.appendChild(el("line", { x1: x, y1: mT, x2: x, y2: hy1,
          stroke: bandCol, "stroke-width": .8, "stroke-dasharray": "1 3", opacity: .4 }));
        var tri = el("path", { d: "M" + (x - 4.2) + " " + hy1 + "L" + (x + 4.2) + " " + hy1 + "L" + x + " " + hy0 + "Z",
          fill: bandCol, stroke: THEME.halo, "stroke-width": 1 });
        var ttl2 = el("title");
        ttl2.textContent = "【" + hn.band + " " + hn.score + "分】" + hn.node + "\n" + hn.date + "（" + hn.when + "）\n" + hn.why;
        tri.appendChild(ttl2); svg.appendChild(tri);
      });
    }

    // ---------- on-chart event labels (lane band above the plot) ----------
    placed.forEach(function (e) {
      var x = xs(e.cd), ly = 46 + (nLanes - 1 - e.lane) * laneH;
      var cx = e.x0 + e.w / 2;
      // leader: label bottom → exact point on the line
      svg.appendChild(el("line", { x1: cx, y1: ly + 10, x2: x, y2: Y(e.v) - 4,
        stroke: e.col, "stroke-width": .8, "stroke-dasharray": "2 2", opacity: .75 }));
      svg.appendChild(el("circle", { cx: x, cy: Y(e.v), r: 3.2, fill: ZC[e.z],
        stroke: e.col, "stroke-width": 1.5 }));
      var g = el("g", { class: "ev-lab" });
      var bg = el("rect", { x: e.x0, y: ly - 1, width: e.w, height: 11.5, rx: 3.5,
        fill: THEME.halo, opacity: .92, stroke: e.col, "stroke-width": e.isCur ? 1.2 : .8 });
      var txel = el("text", { x: e.x0 + PAD, y: ly + 8, fill: e.col,
        "font-size": dense ? "7.8" : "8.3", "font-weight": e.isCur ? "800" : "600" });
      tx(txel, e.text);
      var ttl = el("title"); ttl.textContent = e.full;
      g.appendChild(bg); g.appendChild(txel); g.appendChild(ttl);
      svg.appendChild(g);
    });
    if (dropped > 0) {
      svg.appendChild(tx(el("text", { x: mL + iw, y: 44 + nLanes * laneH, "text-anchor": "end",
        fill: "var(--muted)", "font-size": "8.5" }),
        "另有 " + dropped + " 個事件放不下標籤（圓點懸停可看）"));
    }

    monthAxis(svg, mL, iw, vy + vh + 4 + hiRow, {});
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
    if (tt) tt.innerHTML = combinedTransTable(cur);
  }

  /* ---- PANE 1: every zone transition of the current + selected presidents,
         listed synchronously in one chronological table ---- */
  function combinedTransTable(cur) {
    var rows = [];
    function push(T, col, isCur) {
      (T.transitions || []).forEach(function (x, i) {
        var ex = (T.easy_exits || []).filter(function (e) { return e.own === x.own; })[0];
        rows.push({ cd: x.cd, T: T, col: col, isCur: isCur, i: i, x: x, ex: ex });
      });
    }
    push(cur, THEME.hi, true);
    sel.forEach(function (nm) {
      if (nm === cur.name) return;
      var T = TERMS.filter(function (q) { return q.name === nm; })[0];
      if (T) push(T, selColor(nm), false);
    });
    if (!rows.length) return '<p class="muted" style="margin:8px 0 0">現屆任內無制度級轉區。</p>';
    rows.sort(function (a, b) { return a.cd - b.cd || (b.isCur - a.isCur); });
    var body = rows.map(function (r) {
      var x = r.x, ex = r.ex;
      var trig = ex ? ex.trigger : (x.reason || "—");
      var meta = ex ? ("📅 " + ex.trigger_date + (ex.detail ? " · " + ex.detail : ""))
                    : (x.event ? "⚡ " + x.event : "");
      return '<tr class="' + (r.isCur ? "tt-cur" : "") + '">' +
        '<td class="am-num"><span class="am-flag" style="background:' + ZC[x.to] + '">' + (r.i + 1) + '</span></td>' +
        '<td class="tt-p"><span class="tt-dot" style="background:' + r.col + '"></span>' +
          (r.isCur ? '<b>' + r.T.cn + '</b>' : r.T.cn) + '</td>' +
        '<td class="mono">' + x.own + '</td><td class="mono am-anchor-d">' + fmtA(x.anchor) + '</td>' +
        '<td><span class="zbadge ' + (x.frm === "E" ? "easy" : x.frm === "U" ? "unc" : "hard") + '">' + ZN[x.frm] + '</span>' +
        '<span class="am-arrow">→</span><span class="zbadge ' + (x.to === "E" ? "easy" : x.to === "U" ? "unc" : "hard") + '">' + ZN[x.to] + '</span></td>' +
        '<td class="am-reason">' + (x.frm === "E" ? '<span class="ex-badge">離開 EASY</span> ' : '') +
        '<b class="ex-trig">' + trig + '</b>' + (meta ? '<div class="am-ev">' + meta + '</div>' : '') + '</td></tr>';
    }).join("");
    var n = sel.filter(function (s) { return s !== cur.name; }).length;
    return '<p class="tt-cap">共 ' + rows.length + ' 次轉區（現屆 + PANE 4 已開啟的 ' + n + ' 位前任），依週期位置排序</p>' +
      '<div class="pm-wrap"><table class="am-tt tt-comb"><thead><tr><th>#</th><th>總統</th><th>自家日期</th>' +
      '<th>對標現任</th><th>轉區</th><th>轉區主因與大事件</th></tr></thead><tbody>' + body + '</tbody></table></div>';
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

  /* ================= PANE 4 — compact president toggle list ================= */
  function buildP4() {
    var host = document.getElementById("p4-list"); if (!host) return;
    host.innerHTML = "";
    TERMS.slice().reverse().forEach(function (T) {
      var b = document.createElement("button");
      b.type = "button";
      b.className = "p4-row" + (T.name === AN.name ? " is-cur" : "");
      b.setAttribute("data-term", T.name);
      var nEx = (T.easy_exits || []).length, nTr = (T.transitions || []).length;
      b.innerHTML = '<span class="p4-sw"></span>' +
        '<span class="p4-n">' + T.cn + '<small>' + T.inaug.slice(2, 4) + '–' + T.end.slice(2, 4) + '</small></span>' +
        '<span class="p4-m">' + nTr + '轉' + (nEx ? '<i>·' + nEx + '離E</i>' : '') + '</span>';
      b.addEventListener("click", function () { toggleTerm(T.name); });
      host.appendChild(b);
    });
    syncP4();
  }
  function toggleTerm(nm) {
    var i = sel.indexOf(nm);
    if (i >= 0) sel.splice(i, 1); else sel.push(nm);
    syncP4(); drawPane1();
  }
  function syncP4() {
    document.querySelectorAll(".p4-row").forEach(function (b) {
      var nm = b.getAttribute("data-term"), c = selColor(nm), on = c !== null;
      b.classList.toggle("on", on);
      var sw = b.querySelector(".p4-sw");
      sw.style.background = on ? c : "transparent";
      sw.style.borderColor = on ? c : "var(--line2)";
      if (on) b.style.borderColor = c; else b.style.removeProperty("border-color");
    });
    var c = document.getElementById("p4-count");
    if (c) c.textContent = sel.length + " / " + TERMS.length;
    var ab = document.getElementById("p4-all");
    if (ab) ab.textContent = sel.length ? "✕ 全部關閉" : "＋ 全部開啟";
  }
  var p4all = document.getElementById("p4-all");
  if (p4all) p4all.addEventListener("click", function () {
    // ONE button toggles every president open / closed
    sel = sel.length ? [] : TERMS.map(function (T) { return T.name; });
    syncP4(); drawPane1();
  });

  /* ---- PANE 1 layer switches (each data line + one master button) ---- */
  function buildLayers() {
    var host = document.getElementById("p1-layers"); if (!host) return;
    host.innerHTML = "";
    LAYERS.forEach(function (l) {
      var b = document.createElement("button");
      b.type = "button"; b.className = "lay-btn on"; b.setAttribute("data-k", l.k);
      b.innerHTML = '<i></i>' + l.t;
      b.addEventListener("click", function () {
        layer[l.k] = !layer[l.k];
        b.classList.toggle("on", layer[l.k]);
        syncLayerAll(); drawPane1();
      });
      host.appendChild(b);
    });
  }
  function syncLayerAll() {
    var anyOn = LAYERS.some(function (l) { return layer[l.k]; });
    var b = document.getElementById("p1-lay-all");
    if (b) b.textContent = anyOn ? "✕ 全部關閉" : "＋ 全部開啟";
  }
  var layAll = document.getElementById("p1-lay-all");
  if (layAll) layAll.addEventListener("click", function () {
    // ONE button toggles every PANE 1 data line
    var anyOn = LAYERS.some(function (l) { return layer[l.k]; });
    LAYERS.forEach(function (l) { layer[l.k] = !anyOn; });
    document.querySelectorAll(".lay-btn").forEach(function (x) { x.classList.toggle("on", !anyOn); });
    syncLayerAll(); drawPane1();
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
    drawPane1(); drawStack(); syncP4();
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

  buildLayers();
  buildP4();
  drawPane1();
  drawStack();
  buildCards();
})();
