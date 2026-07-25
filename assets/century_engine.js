/* R2 — 100-year presidency-cycle comparison.
   26 terms on ONE cycle axis: spaghetti + median + interquartile band,
   colour-by mode switch, hover highlight, and 26 small multiples. */
(function () {
  var NS = "http://www.w3.org/2000/svg";
  var C = DATA.century, S = C.series, M = C.meta, ORDER = C.order;
  var CD0 = -130, CD1 = 1461;

  // era is ORDINAL (time-ordered) → sequential ramp, dim = older, bright = newer
  var ERA5 = ["戰前", "戰後", "滯脹", "大緩和", "現代"];
  var ERAMAP = { "戰前": "戰前", "戰後": "戰後", "滯脹": "滯脹", "大緩和": "大緩和",
                 "科網": "大緩和", "金融海嘯": "現代", "QE": "現代", "現代": "現代" };
  var ERACOL = { "戰前": "#1f4d80", "戰後": "#2a6ba8", "滯脹": "#3987e5", "大緩和": "#6ba7e8", "現代": "#a3cdf7" };
  var PARTYCOL = { D: "#3987e5", R: "#d95926" };
  var TIERCOL = { A: "#3ecf8e", "混合": "#e6b23d", B: "#6b7d99" };
  var NEUTRAL = "#5a6d88";
  var mode = "era", focus = null;

  // the median/quartiles across 26 step functions are inherently jumpy —
  // smooth them so the archetype SHAPE is readable (labelled as smoothed in the UI)
  function smoothEnv(env, w) {
    var h = Math.floor(w / 2);
    return env.map(function (e, i) {
      var a = Math.max(0, i - h), b = Math.min(env.length, i + h + 1), sl = env.slice(a, b);
      function avg(k) { return sl.reduce(function (s, x) { return s + x[k]; }, 0) / sl.length; }
      return { cd: e.cd, n: e.n, med: avg("med"), p25: avg("p25"), p75: avg("p75"), hardpct: avg("hardpct") };
    });
  }

  function el(t, a) { var e = document.createElementNS(NS, t); for (var k in a) e.setAttribute(k, a[k]); return e; }
  function tx(e, s) { e.textContent = s; return e; }
  function era5(n) { return ERAMAP[M[n].era] || "現代"; }
  function colorOf(n) {
    if (mode === "party") return PARTYCOL[M[n].party];
    if (mode === "tier") return TIERCOL[M[n].tier];
    if (mode === "era") return ERACOL[era5(n)];
    return NEUTRAL;
  }


  /* ---------------- zone heatmap: 26 terms x cycle time (PRIMARY) ---------------- */
  var ZC = { E: "#2e9b6f", U: "#c99a2e", H: "#d2566c" };
  // Tier A rows come from daily data and Tier B from segments; to compare REGIME SHAPE
  // across rows fairly, collapse runs shorter than MINRUN samples into their neighbours.
  // Applied uniformly to every row (Tier B runs are already long, so they are unaffected).
  var MINRUN = 4;   // 4 weekly samples ≈ 1 month
  function regimeRuns(pts) {
    var runs = [];
    pts.forEach(function (p) {
      var last = runs[runs.length - 1];
      if (last && last.z === p.z) { last.end = p.cd; last.n++; }
      else runs.push({ z: p.z, cd: p.cd, end: p.cd, n: 1 });
    });
    var changed = true;
    while (changed && runs.length > 1) {
      changed = false;
      for (var i = 0; i < runs.length; i++) {
        if (runs[i].n >= MINRUN) continue;
        var L = runs[i - 1], R = runs[i + 1];
        var host = (L && R) ? (L.n >= R.n ? L : R) : (L || R);
        if (!host) break;
        host.z = host.z;
        runs[i].z = host.z;
        var merged = [];
        runs.forEach(function (r) {
          var m = merged[merged.length - 1];
          if (m && m.z === r.z) { m.end = r.end; m.n += r.n; }
          else merged.push({ z: r.z, cd: r.cd, end: r.end, n: r.n });
        });
        runs = merged; changed = true; break;
      }
    }
    return runs;
  }
  function drawHeat() {
    var host = document.getElementById("ct-heat"); if (!host) return;
    host.innerHTML = "";
    var rows = ORDER.length, RH = 13, GAP = 2;
    var mL = 132, mR = 26, mT = 50, mB = 30, strip = 56;
    var W = 1000, gh = rows * (RH + GAP), H = mT + gh + strip + mB;
    var iw = W - mL - mR;
    var X = function (cd) { return mL + (cd - CD0) / (CD1 - CD0) * iw; };
    var svg = el("svg", { viewBox: "0 0 " + W + " " + H, role: "img",
      "aria-label": "26 屆總統任期的資金區熱圖，橫軸為總統週期日" });

    // milestone guides + labels
    C.milestones.forEach(function (m, i) {
      var x = X(m.day);
      svg.appendChild(el("line", { x1: x, y1: mT - 4, x2: x, y2: mT + gh + strip,
        stroke: m.day === 0 ? "rgba(255,255,255,.5)" : "rgba(255,255,255,.28)",
        "stroke-width": m.day === 0 ? 1.4 : 1, "stroke-dasharray": m.day === 0 ? "" : "3 4" }));
      var y = mT - 34 + (i % 2) * 14;
      var anc = i === 0 ? "start" : (i === C.milestones.length - 1 ? "end" : "middle");
      svg.appendChild(tx(el("text", { x: x, y: y, "text-anchor": anc, fill: "#c3d2e8",
        "font-size": "10", "font-weight": "700" }), m.label.split(" ")[0]));
    });

    // one row per term: merge consecutive same-zone samples into rects
    ORDER.forEach(function (n, ri) {
      var y = mT + ri * (RH + GAP), pts = S[n], m = M[n];
      var dim = focus && focus !== n;
      svg.appendChild(el("rect", { x: mL, y: y, width: iw, height: RH, fill: "rgba(255,255,255,.03)", rx: 2 }));
      regimeRuns(pts).forEach(function (r) {
        var x1 = X(r.cd), x2 = X(r.end + C.step);
        svg.appendChild(el("rect", { x: x1, y: y, width: Math.max(1, x2 - x1), height: RH,
          fill: ZC[r.z], opacity: dim ? .2 : (m.tier === "B" ? .8 : 1), rx: 1 }));
      });
      // documented trough marker
      var tr = C.troughs[n];
      if (tr && tr.cd >= CD0 && tr.cd <= CD1) {
        svg.appendChild(el("path", { d: "M" + (X(tr.cd) - 3.6) + " " + (y - 1.5) + "l3.6 4.6l3.6-4.6z",
          fill: tr.midterm_low ? "#ffd479" : "#ffffff", opacity: dim ? .3 : .95 }));
      }
      // label
      var lb = el("text", { x: mL - 8, y: y + RH - 3, "text-anchor": "end",
        fill: focus === n ? "#fff" : "var(--ink2)", "font-size": "9.5",
        "font-weight": focus === n ? "800" : "500", opacity: dim ? .45 : 1, style: "cursor:pointer" });
      tx(lb, m.cn + " " + m.inaug.slice(2, 4) + "–" + m.end.slice(2, 4));
      lb.addEventListener("click", function () { focus = (focus === n ? null : n); render(); });
      svg.appendChild(lb);
      var td = el("rect", { x: mL - 6, y: y, width: 4, height: RH, rx: 1,
        fill: m.tier === "A" ? "#3ecf8e" : (m.tier === "B" ? "#4a5a72" : "#e6b23d") });
      svg.appendChild(td);
    });

    // bottom strip: share of terms in HARD at each cycle day
    var sy = mT + gh + 16, sh = strip - 22;
    svg.appendChild(el("rect", { x: mL, y: sy, width: iw, height: sh, fill: "rgba(255,255,255,.04)", rx: 3 }));
    var env = C.envelope, mx = Math.ceil(Math.max.apply(null, env.map(function (e) { return e.hardpct; })) / 10) * 10;
    var area = env.map(function (e, i) {
      return (i ? "L" : "M") + X(e.cd).toFixed(1) + " " + (sy + sh - Math.min(1, e.hardpct / mx) * sh).toFixed(1);
    }).join("");
    if (env.length) {
      svg.appendChild(el("path", { d: area + "L" + X(env[env.length - 1].cd) + " " + (sy + sh) + "L" + X(env[0].cd) + " " + (sy + sh) + "Z",
        fill: "rgba(210,86,108,.3)" }));
      svg.appendChild(el("path", { d: area, fill: "none", stroke: "#d2566c", "stroke-width": 1.8 }));
    }
    svg.appendChild(tx(el("text", { x: mL - 8, y: sy + sh / 2 + 3, "text-anchor": "end",
      fill: "var(--ink2)", "font-size": "9.5", "font-weight": "700" }), "同期處 HARD 的屆數%"));
    svg.appendChild(tx(el("text", { x: mL + 4, y: sy + 10, fill: "var(--muted)", "font-size": "8.5" }), "0–" + mx + "%"));
    host.appendChild(svg);

    // hover
    var tip = document.createElement("div"); tip.className = "cy-tip"; tip.style.display = "none"; host.appendChild(tip);
    var cr = el("line", { x1: 0, y1: mT, x2: 0, y2: mT + gh + strip, stroke: "#fff", "stroke-width": 1, opacity: 0 });
    svg.appendChild(cr);
    svg.style.cursor = "crosshair";
    svg.addEventListener("mousemove", function (e) {
      var r = svg.getBoundingClientRect();
      var px = (e.clientX - r.left) / r.width * W, py = (e.clientY - r.top) / r.height * H;
      var cd = Math.round(CD0 + (px - mL) / iw * (CD1 - CD0));
      if (cd < CD0 || cd > CD1) { tip.style.display = "none"; cr.setAttribute("opacity", 0); return; }
      cr.setAttribute("x1", X(cd)); cr.setAttribute("x2", X(cd)); cr.setAttribute("opacity", .7);
      var ri = Math.floor((py - mT) / (RH + GAP));
      var best = null, bd = 1e9;
      for (var i = 0; i < C.envelope.length; i++) { var q = Math.abs(C.envelope[i].cd - cd); if (q < bd) { bd = q; best = C.envelope[i]; } }
      var rowHtml = "";
      if (ri >= 0 && ri < ORDER.length) {
        var n = ORDER[ri], pts = S[n], pb = null, pd = 1e9;
        for (var j = 0; j < pts.length; j++) { var w = Math.abs(pts[j].cd - cd); if (w < pd) { pd = w; pb = pts[j]; } }
        if (pb && pd <= 14) rowHtml = '<div class="cy-tip-r" style="border-top:1px solid var(--line);margin-top:4px;padding-top:5px">' +
          '<i style="background:' + ZC[pb.z] + '"></i><span class="cy-tip-n">' + M[n].cn + '</span><b>' + pb.v.toFixed(0) + '</b>' +
          '<em class="z-' + pb.z + '">' + (pb.z === "E" ? "EASY" : pb.z === "U" ? "UNC" : "HARD") + '</em>' +
          '<span class="cy-tip-d">' + pb.t + '</span></div>';
      }
      var yy = Math.round(cd / 365.25 * 10) / 10;
      tip.style.display = "block";
      tip.innerHTML = '<div class="cy-tip-h">週期第 ' + cd + ' 日 <span>(就職後 ' + yy + ' 年)</span></div>' +
        (best ? '<div class="cy-tip-r"><i style="background:#d2566c"></i><span class="cy-tip-n">處 HARD</span><b>' + best.hardpct + '%</b><span class="cy-tip-d">' + best.n + ' 屆中</span></div>' +
                '<div class="cy-tip-r"><i style="background:#ffd479"></i><span class="cy-tip-n">中位數</span><b>' + best.med.toFixed(0) + '</b></div>' : "") + rowHtml;
      tip.style.left = Math.max(12, Math.min(88, X(cd) / W * 100)) + "%";
      tip.style.top = "6px";
    });
    svg.addEventListener("mouseleave", function () { tip.style.display = "none"; cr.setAttribute("opacity", 0); });
  }

  /* ---------------- median + IQR archetype (secondary) ---------------- */
  function drawMain() {
    var host = document.getElementById("ct-main"); if (!host) return;
    host.innerHTML = "";
    var W = 1000, H = 470, mL = 50, mR = 118, mT = 52, mB = 58;
    var iw = W - mL - mR, ih = H - mT - mB;
    var X = function (cd) { return mL + (cd - CD0) / (CD1 - CD0) * iw; };
    var Y = function (v) { return mT + ih - (v / 100) * ih; };
    var svg = el("svg", { viewBox: "0 0 " + W + " " + H, role: "img",
      "aria-label": "1925-2026 共 26 屆美國總統任期於同一就任週期軸上的 Easy/Hard 指數比較" });

    [[70, 100, "rgba(62,207,142,.09)", "EASY ≥70", "#3ecf8e"],
     [40, 70, "rgba(230,178,61,.08)", "UNCERTAIN 40–70", "#e6b23d"],
     [0, 40, "rgba(242,107,127,.10)", "HARD ≤40", "#f26b7f"]].forEach(function (b) {
      svg.appendChild(el("rect", { x: mL, y: Y(b[1]), width: iw, height: Y(b[0]) - Y(b[1]), fill: b[2] }));
      svg.appendChild(tx(el("text", { x: mL + 7, y: Y(b[1]) + 13, fill: b[4], "font-size": "10", "font-weight": "800", opacity: .7 }), b[3]));
    });
    [70, 40].forEach(function (v) {
      svg.appendChild(el("line", { x1: mL, y1: Y(v), x2: mL + iw, y2: Y(v), stroke: "rgba(255,255,255,.2)", "stroke-width": 1, "stroke-dasharray": "4 4" }));
    });
    [0, 20, 40, 60, 80, 100].forEach(function (v) {
      svg.appendChild(tx(el("text", { x: mL - 9, y: Y(v) + 4, "text-anchor": "end", fill: "var(--muted)", "font-size": "10" }), v));
    });

    // milestones
    C.milestones.forEach(function (m, i) {
      var x = X(m.day);
      svg.appendChild(el("line", { x1: x, y1: mT, x2: x, y2: mT + ih,
        stroke: m.day === 0 ? "rgba(255,255,255,.4)" : "rgba(255,255,255,.17)",
        "stroke-width": m.day === 0 ? 1.4 : 1, "stroke-dasharray": m.day === 0 ? "" : "3 4" }));
      var y = mT - 32 + (i % 2) * 15;
      svg.appendChild(el("line", { x1: x, y1: y + 3, x2: x, y2: mT, stroke: "rgba(255,255,255,.14)", "stroke-width": .8 }));
      var anc = i === 0 ? "start" : (i === C.milestones.length - 1 ? "end" : "middle");
      svg.appendChild(tx(el("text", { x: x, y: y, "text-anchor": anc, fill: "#c3d2e8", "font-size": "10", "font-weight": "700" }),
        m.label.split(" ")[0]));
    });

    // interquartile band + median (smoothed ~13 weeks)
    var env = smoothEnv(C.envelope, 13);
    if (env.length) {
      var up = env.map(function (e, i) { return (i ? "L" : "M") + X(e.cd).toFixed(1) + " " + Y(e.p75).toFixed(1); }).join("");
      var dn = env.slice().reverse().map(function (e) { return "L" + X(e.cd).toFixed(1) + " " + Y(e.p25).toFixed(1); }).join("");
      svg.appendChild(el("path", { d: up + dn + "Z", fill: "rgba(255,255,255,.13)", stroke: "none" }));
    }

    // all 26 term lines
    ORDER.forEach(function (n) {
      var pts = S[n]; if (!pts) return;
      var d = pts.map(function (p, i) { return (i ? "L" : "M") + X(p.cd).toFixed(1) + " " + Y(p.v).toFixed(1); }).join("");
      var isF = focus === n, dim = focus && !isF;
      svg.appendChild(el("path", {
        d: d, fill: "none", stroke: isF ? "#ffffff" : colorOf(n),
        "stroke-width": isF ? 2.6 : 0.85, opacity: dim ? .1 : (isF ? 1 : .3),
        "stroke-linejoin": "round", "data-term": n, class: "ct-line"
      }));
    });

    // median on top
    if (env.length) {
      var md = env.map(function (e, i) { return (i ? "L" : "M") + X(e.cd).toFixed(1) + " " + Y(e.med).toFixed(1); }).join("");
      svg.appendChild(el("path", { d: md, fill: "none", stroke: "#ffd479", "stroke-width": 3,
        "stroke-linejoin": "round", opacity: focus ? .45 : 1 }));
      var last = env[env.length - 1];
      svg.appendChild(tx(el("text", { x: X(last.cd) + 8, y: Y(last.med) + 4, fill: "#ffd479", "font-size": "11", "font-weight": "800" }), "26屆中位數"));
    }
    if (focus) {
      var fp = S[focus][S[focus].length - 1];
      svg.appendChild(tx(el("text", { x: Math.min(X(fp.cd) + 8, mL + iw + 6), y: Y(fp.v) + 4, fill: "#fff", "font-size": "11", "font-weight": "800" }),
        M[focus].cn));
    }
    host.appendChild(svg);

    // hover
    var tip = document.createElement("div"); tip.className = "cy-tip"; tip.style.display = "none"; host.appendChild(tip);
    var cross = el("line", { x1: 0, y1: mT, x2: 0, y2: mT + ih, stroke: "rgba(255,255,255,.45)", "stroke-width": 1, opacity: 0 });
    svg.appendChild(cross);
    svg.style.cursor = "crosshair";
    svg.addEventListener("mousemove", function (e) {
      var r = svg.getBoundingClientRect();
      var cd = Math.round(CD0 + ((e.clientX - r.left) / r.width * W - mL) / iw * (CD1 - CD0));
      if (cd < CD0 || cd > CD1) return;
      cross.setAttribute("x1", X(cd)); cross.setAttribute("x2", X(cd)); cross.setAttribute("opacity", 1);
      var best = null, bd = 1e9;
      for (var i = 0; i < env.length; i++) { var dd = Math.abs(env[i].cd - cd); if (dd < bd) { bd = dd; best = env[i]; } }
      if (!best) return;
      var yy = Math.round(cd / 365.25 * 10) / 10;
      var extra = "";
      if (focus) {
        var fpts = S[focus], fb = null, fd = 1e9;
        for (var j = 0; j < fpts.length; j++) { var q = Math.abs(fpts[j].cd - cd); if (q < fd) { fd = q; fb = fpts[j]; } }
        if (fb && fd <= 14) extra = '<div class="cy-tip-r" style="border-top:1px solid var(--line);margin-top:4px;padding-top:5px">' +
          '<i style="background:#fff"></i><span class="cy-tip-n">' + M[focus].cn + '</span><b>' + fb.v.toFixed(0) +
          '</b><em class="z-' + fb.z + '">' + (fb.z === "E" ? "EASY" : fb.z === "U" ? "UNC" : "HARD") + '</em>' +
          '<span class="cy-tip-d">' + fb.t + '</span></div>';
      }
      tip.style.display = "block";
      tip.innerHTML = '<div class="cy-tip-h">週期第 ' + cd + ' 日 <span>(就職後 ' + yy + ' 年)</span></div>' +
        '<div class="cy-tip-r"><i style="background:#ffd479"></i><span class="cy-tip-n">中位數</span><b>' + best.med.toFixed(0) + '</b></div>' +
        '<div class="cy-tip-r"><i style="background:rgba(255,255,255,.35)"></i><span class="cy-tip-n">四分位</span><b>' + best.p25.toFixed(0) + '–' + best.p75.toFixed(0) + '</b></div>' +
        '<div class="cy-tip-r"><i style="background:#f26b7f"></i><span class="cy-tip-n">處 HARD</span><b>' + best.hardpct.toFixed(0) + '%</b><span class="cy-tip-d">' + best.n + ' 屆</span></div>' + extra;
      tip.style.left = Math.max(12, Math.min(88, X(cd) / W * 100)) + "%";
      tip.style.top = "8px";
    });
    svg.addEventListener("mouseleave", function () { tip.style.display = "none"; cross.setAttribute("opacity", 0); });
  }

  /* ---------------- 26 small multiples ---------------- */
  function drawSmall() {
    var host = document.getElementById("ct-small"); if (!host) return;
    host.innerHTML = "";
    ORDER.forEach(function (n) {
      var pts = S[n], m = M[n];
      var card = document.createElement("button");
      card.className = "sm-card" + (focus === n ? " on" : "");
      card.type = "button";
      var W = 260, H = 96, mT = 6, mB = 14, mL = 4, mR = 4;
      var iw = W - mL - mR, ih = H - mT - mB;
      var X = function (cd) { return mL + (cd - CD0) / (CD1 - CD0) * iw; };
      var Y = function (v) { return mT + ih - (v / 100) * ih; };
      var svg = el("svg", { viewBox: "0 0 " + W + " " + H, preserveAspectRatio: "none" });
      [[70, 100, "rgba(62,207,142,.10)"], [40, 70, "rgba(230,178,61,.08)"], [0, 40, "rgba(242,107,127,.12)"]].forEach(function (b) {
        svg.appendChild(el("rect", { x: mL, y: Y(b[1]), width: iw, height: Y(b[0]) - Y(b[1]), fill: b[2] }));
      });
      [365, 730, 1095].forEach(function (d) {
        svg.appendChild(el("line", { x1: X(d), y1: mT, x2: X(d), y2: mT + ih, stroke: "rgba(255,255,255,.13)", "stroke-width": .8 }));
      });
      svg.appendChild(el("line", { x1: X(0), y1: mT, x2: X(0), y2: mT + ih, stroke: "rgba(255,255,255,.3)", "stroke-width": 1 }));
      var d = pts.map(function (p, i) { return (i ? "L" : "M") + X(p.cd).toFixed(1) + " " + Y(p.v).toFixed(1); }).join("");
      svg.appendChild(el("path", { d: d, fill: "none", stroke: colorOf(n), "stroke-width": 1.7, "stroke-linejoin": "round" }));
      // documented trough marker
      var tr = C.troughs[n];
      if (tr && tr.cd >= CD0 && tr.cd <= CD1) {
        svg.appendChild(el("line", { x1: X(tr.cd), y1: mT, x2: X(tr.cd), y2: mT + ih,
          stroke: "#f26b7f", "stroke-width": 1.1, "stroke-dasharray": "2 2", opacity: .9 }));
        svg.appendChild(el("path", { d: "M" + (X(tr.cd) - 3.4) + " " + (mT + ih + 1) + "l3.4 4.6l3.4-4.6z", fill: "#f26b7f" }));
      }
      ["第1年", "第2年", "第3年", "第4年"].forEach(function (lb, i) {
        svg.appendChild(tx(el("text", { x: X(182 + i * 365), y: H - 3, "text-anchor": "middle",
          fill: "rgba(255,255,255,.3)", "font-size": "7.5" }), i + 1));
      });
      card.innerHTML = '<div class="sm-h"><span class="sm-n">' + m.cn + '</span>' +
        '<span class="sm-y">' + m.inaug.slice(0, 4) + '–' + m.end.slice(0, 4) + '</span>' +
        '<span class="sm-t sm-t-' + (m.tier === "混合" ? "M" : m.tier) + '">' + m.tier + '</span></div>';
      card.appendChild(svg);
      var trn = tr ? ('底 ' + tr.date + ' · ' + tr.year + (tr.midterm_low ? ' ★中期年' : '')) : '';
      var f = document.createElement("div"); f.className = "sm-f"; f.textContent = trn;
      card.appendChild(f);
      card.addEventListener("click", function () { focus = (focus === n ? null : n); render(); });
      host.appendChild(card);
    });
  }

  function render() { drawHeat(); drawMain(); drawSmall(); syncButtons(); }
  function syncButtons() {
    document.querySelectorAll("#ct-modes .cy-btn").forEach(function (b) {
      b.classList.toggle("on", b.getAttribute("data-mode") === mode);
    });
    var lg = document.getElementById("ct-legend");
    if (!lg) return;
    var items = [];
    if (mode === "era") items = ERA5.map(function (e) { return [ERACOL[e], e]; });
    else if (mode === "party") items = [[PARTYCOL.D, "民主黨"], [PARTYCOL.R, "共和黨"]];
    else if (mode === "tier") items = [[TIERCOL.A, "A 量測級（每日18指標）"], [TIERCOL["混合"], "混合"], [TIERCOL.B, "B 重建級（R1窗口+市場史）"]];
    else items = [[NEUTRAL, "全部任期"]];
    items.push(["#ffd479", "26屆中位數"]);
    items.push(["rgba(255,255,255,.35)", "四分位帶 (P25–P75)"]);
    lg.innerHTML = items.map(function (it) {
      return '<span class="ct-lg"><i style="background:' + it[0] + '"></i>' + it[1] + '</span>';
    }).join("") + (focus ? '<button class="cy-btn" id="ct-clear" type="button">✕ 取消聚焦 ' + M[focus].cn + '</button>' : '');
    var cl = document.getElementById("ct-clear");
    if (cl) cl.addEventListener("click", function () { focus = null; render(); });
  }

  document.querySelectorAll("#ct-modes .cy-btn").forEach(function (b) {
    b.addEventListener("click", function () { mode = b.getAttribute("data-mode"); render(); });
  });
  render();
})();
