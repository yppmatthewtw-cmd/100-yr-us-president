/* R2 現任錨定版 — X axis = the CURRENT president's real calendar (YEAR 0 election →
   YEAR 5 end of term). Every predecessor projected onto the same axis by cycle-day.
   Each president is an independently expandable/collapsible card; every zone
   transition carries its reason + major event. */
(function () {
  var NS = "http://www.w3.org/2000/svg";
  var A = DATA.anchor, TERMS = A.terms, AN = A.anchor;
  var CD0 = -90, CD1 = 1461;
  var ZC = { E: "#2e9b6f", U: "#c99a2e", H: "#d2566c" };
  var ZBG = { E: "rgba(62,207,142,.16)", U: "rgba(230,178,61,.15)", H: "rgba(242,107,127,.17)" };
  var ZN = { E: "EASY", U: "UNCERTAIN", H: "HARD" };

  function el(t, a) { var e = document.createElementNS(NS, t); for (var k in a) e.setAttribute(k, a[k]); return e; }
  function tx(e, s) { e.textContent = s; return e; }
  function X(cd, mL, iw) { return mL + (cd - CD0) / (CD1 - CD0) * iw; }
  function fmtA(iso) { return iso.slice(0, 7).replace("-", "."); }

  /* ---- shared axis furniture: year bands + milestones + now ---- */
  function axisFurniture(svg, mL, iw, top, h, opts) {
    opts = opts || {};
    A.yearbands.forEach(function (b, i) {
      var x1 = X(Math.max(b.cd0, CD0), mL, iw), x2 = X(b.cd1, mL, iw);
      if (i % 2 === 0) svg.appendChild(el("rect", { x: x1, y: top, width: x2 - x1, height: h, fill: "rgba(255,255,255,.028)" }));
      if (opts.bandLabels && x2 - x1 > 40)
        svg.appendChild(tx(el("text", { x: (x1 + x2) / 2, y: top + h + 14, "text-anchor": "middle",
          fill: "var(--muted)", "font-size": "9.5", "font-weight": "700" }), b.lab));
    });
    A.milestones.forEach(function (m, i) {
      var x = X(m.cd, mL, iw);
      svg.appendChild(el("line", { x1: x, y1: top, x2: x, y2: top + h,
        stroke: m.cd === 0 ? "rgba(255,255,255,.45)" : "rgba(255,255,255,.2)",
        "stroke-width": m.cd === 0 ? 1.3 : 1, "stroke-dasharray": m.cd === 0 ? "" : "3 4" }));
      if (opts.msLabels) {
        var y = top - 24 + (i % 2) * 12;
        var anc = i === 0 ? "start" : (i === A.milestones.length - 1 ? "end" : "middle");
        var lb = el("text", { x: x, y: y, "text-anchor": anc, fill: "#c3d2e8", "font-size": "9.5", "font-weight": "700" });
        tx(lb, m.label);
        var ttl = el("title"); ttl.textContent = m.date + " " + m.note; lb.appendChild(ttl);
        svg.appendChild(lb);
      }
    });
    // now
    var xn = X(A.anchor.cd_now, mL, iw);
    svg.appendChild(el("line", { x1: xn, y1: top - (opts.msLabels ? 2 : 0), x2: xn, y2: top + h,
      stroke: "#7fd4ff", "stroke-width": 1.4 }));
    if (opts.nowLabel) {
      svg.appendChild(tx(el("text", { x: xn + 5, y: top + 11, fill: "#7fd4ff", "font-size": "9.5", "font-weight": "800" }),
        "現在 " + AN.now));
    }
  }

  /* ---- zone strip + numbered transition flags for one term ---- */
  function drawStrip(host, T, big) {
    host.innerHTML = "";
    var W = 1000, RH = big ? 34 : 16;
    var mL = 8, mR = 8, mT = big ? 34 : 4, mB = big ? 24 : 6;
    var H = mT + RH + mB, iw = W - mL - mR;
    var svg = el("svg", { viewBox: "0 0 " + W + " " + H, preserveAspectRatio: "none", role: "img",
      "aria-label": T.cn + " 資金區分段（對標現任時間軸）" });
    axisFurniture(svg, mL, iw, mT, RH, { msLabels: big, bandLabels: big, nowLabel: false });
    T.zones.forEach(function (z) {
      var x1 = X(Math.max(z.cd0, CD0), mL, iw), x2 = X(Math.min(z.cd1, CD1), mL, iw);
      var r = el("rect", { x: x1, y: mT, width: Math.max(1, x2 - x1), height: RH,
        fill: ZC[z.z], opacity: T.tier === "B" ? .8 : 1, rx: 2 });
      var ttl = el("title");
      ttl.textContent = ZN[z.z] + "  " + z.own0 + " → " + z.own1 + "\n" + (z.note || "");
      r.appendChild(ttl);
      svg.appendChild(r);
    });
    // now line above the zones
    var xn = X(A.anchor.cd_now, mL, iw);
    svg.appendChild(el("line", { x1: xn, y1: mT - 2, x2: xn, y2: mT + RH + 2, stroke: "#7fd4ff", "stroke-width": 1.4 }));
    // trough marker
    if (T.trough && T.trough.cd >= CD0 && T.trough.cd <= CD1) {
      var xt = X(T.trough.cd, mL, iw);
      svg.appendChild(el("path", { d: "M" + (xt - 4) + " " + (mT + RH + 2) + "l4 5.4l4-5.4z",
        fill: T.trough.midterm_low ? "#ffd479" : "#fff" }));
    }
    // numbered transition flags
    if (big) T.transitions.forEach(function (t, i) {
      var x = X(t.cd, mL, iw);
      svg.appendChild(el("line", { x1: x, y1: mT - 8, x2: x, y2: mT + RH, stroke: "#fff", "stroke-width": 1, opacity: .65 }));
      var c = el("circle", { cx: x, cy: mT - 14, r: 8, fill: ZC[t.to], stroke: "#0b111b", "stroke-width": 1.4 });
      var ttl = el("title");
      ttl.textContent = "#" + (i + 1) + "  " + t.own + "  " + ZN[t.frm] + "→" + ZN[t.to] + "\n" + (t.reason || "") + (t.event ? "\n事件: " + t.event : "");
      c.appendChild(ttl); svg.appendChild(c);
      svg.appendChild(tx(el("text", { x: x, y: mT - 10.6, "text-anchor": "middle", fill: "#0b111b",
        "font-size": "9", "font-weight": "800" }), i + 1));
    });
    host.appendChild(svg);
  }

  /* ---- transitions table ---- */
  function transTable(T) {
    if (!T.transitions.length)
      return '<p class="muted" style="margin:8px 0 0">任內無制度級轉區（全程 ' + ZN[T.zones[0].z] + '）。</p>';
    var rows = T.transitions.map(function (t, i) {
      return '<tr><td class="am-num"><span class="am-flag" style="background:' + ZC[t.to] + '">' + (i + 1) + '</span></td>' +
        '<td class="mono">' + t.own + '</td>' +
        '<td class="mono am-anchor-d">' + fmtA(t.anchor) + '</td>' +
        '<td><span class="zbadge ' + (t.frm === "E" ? "easy" : t.frm === "U" ? "unc" : "hard") + '">' + ZN[t.frm] + '</span>' +
        '<span class="am-arrow">→</span>' +
        '<span class="zbadge ' + (t.to === "E" ? "easy" : t.to === "U" ? "unc" : "hard") + '">' + ZN[t.to] + '</span></td>' +
        '<td class="am-reason">' + (t.reason || "—") + (t.event ? '<div class="am-ev">⚡ ' + t.event + '</div>' : "") + '</td></tr>';
    }).join("");
    return '<div class="pm-wrap"><table class="am-tt"><thead><tr><th>#</th><th>自家日期</th><th>對標現任</th><th>轉區</th><th>主因與大事件</th></tr></thead><tbody>' + rows + '</tbody></table></div>';
  }

  /* ---- at-now chip ---- */
  function nowChip(T) {
    if (!T.at_now) return '<span class="am-chip am-chip-na">同位無數據</span>';
    var z = T.at_now.z;
    return '<span class="am-chip" style="background:' + ZBG[z] + ';color:' + ZC[z] + ';border-color:' + ZC[z] + '">' +
      '同位 ' + T.at_now.own.slice(0, 7).replace("-", ".") + ' · ' + ZN[z] + ' ' + Math.round(T.at_now.v) + '</span>';
  }

  /* ---- master: the anchor president on his real calendar ---- */
  function drawMaster() {
    var host = document.getElementById("am-master"); if (!host) return;
    host.innerHTML = "";
    var T = TERMS.filter(function (t) { return t.name === AN.name; })[0];
    var W = 1000, H = 330, mL = 44, mR = 10, mT = 46, mB = 40;
    var iw = W - mL - mR, ih = H - mT - mB - 26, stripY = mT + ih + 8;
    var Y = function (v) { return mT + ih - (v / 100) * ih; };
    var svg = el("svg", { viewBox: "0 0 " + W + " " + H, role: "img",
      "aria-label": "現任總統的真實時間軸與 Easy/Hard 指數" });
    axisFurniture(svg, mL, iw, mT, ih + 34, { msLabels: true, bandLabels: true, nowLabel: true });
    // zone reference bands behind the line
    [[70, 100, "E"], [40, 70, "U"], [0, 40, "H"]].forEach(function (b) {
      svg.appendChild(el("rect", { x: mL, y: Y(b[1]), width: iw, height: Y(b[0]) - Y(b[1]), fill: ZBG[b[2]], opacity: .5 }));
    });
    [0, 40, 70, 100].forEach(function (v) {
      svg.appendChild(tx(el("text", { x: mL - 7, y: Y(v) + 4, "text-anchor": "end", fill: "var(--muted)", "font-size": "9.5" }), v));
      svg.appendChild(el("line", { x1: mL, y1: Y(v), x2: mL + iw, y2: Y(v), stroke: "rgba(255,255,255,.14)", "stroke-width": .8, "stroke-dasharray": "4 4" }));
    });
    // daily smoothed index line
    var pts = A.master;
    if (pts.length) {
      var d = pts.map(function (p, i) { return (i ? "L" : "M") + X(p.cd, mL, iw).toFixed(1) + " " + Y(p.sm).toFixed(1); }).join("");
      svg.appendChild(el("path", { d: d, fill: "none", stroke: "#eaf1fb", "stroke-width": 2, "stroke-linejoin": "round" }));
      var last = pts[pts.length - 1];
      svg.appendChild(el("circle", { cx: X(last.cd, mL, iw), cy: Y(last.sm), r: 3.6, fill: "#7fd4ff", stroke: "#0b111b", "stroke-width": 1.4 }));
      svg.appendChild(tx(el("text", { x: X(last.cd, mL, iw) + 7, y: Y(last.sm) + 4, fill: "#7fd4ff", "font-size": "10.5", "font-weight": "800" }),
        Math.round(last.sm) + " " + ZN[last.z]));
    }
    // zone strip under the line
    T.zones.forEach(function (z) {
      var x1 = X(Math.max(z.cd0, CD0), mL, iw), x2 = X(Math.min(z.cd1, CD1), mL, iw);
      var r = el("rect", { x: x1, y: stripY, width: Math.max(1, x2 - x1), height: 14, fill: ZC[z.z], rx: 2 });
      var ttl = el("title"); ttl.textContent = ZN[z.z] + "  " + z.own0 + " → " + z.own1 + "\n" + (z.note || "");
      r.appendChild(ttl); svg.appendChild(r);
    });
    // remaining-term hatch (future)
    var xn = X(A.anchor.cd_now, mL, iw);
    svg.appendChild(el("rect", { x: xn, y: stripY, width: X(CD1, mL, iw) - xn, height: 14, fill: "rgba(255,255,255,.05)", rx: 2 }));
    svg.appendChild(tx(el("text", { x: (xn + X(CD1, mL, iw)) / 2, y: stripY + 11, "text-anchor": "middle",
      fill: "var(--muted)", "font-size": "9" }), "未來（未有數據）"));
    // numbered flags on master
    T.transitions.forEach(function (t, i) {
      var x = X(t.cd, mL, iw);
      var c = el("circle", { cx: x, cy: stripY - 8, r: 8, fill: ZC[t.to], stroke: "#0b111b", "stroke-width": 1.4 });
      var ttl = el("title");
      ttl.textContent = "#" + (i + 1) + "  " + t.own + "  " + ZN[t.frm] + "→" + ZN[t.to] + "\n" + (t.reason || "") + (t.event ? "\n事件: " + t.event : "");
      c.appendChild(ttl); svg.appendChild(c);
      svg.appendChild(tx(el("text", { x: x, y: stripY - 4.6, "text-anchor": "middle", fill: "#0b111b", "font-size": "9", "font-weight": "800" }), i + 1));
      svg.appendChild(el("line", { x1: x, y1: stripY, x2: x, y2: stripY + 14, stroke: "#fff", "stroke-width": 1, opacity: .7 }));
    });
    host.appendChild(svg);
    var tt = document.getElementById("am-master-tt");
    if (tt) tt.innerHTML = transTable(T);
  }

  /* ---- predecessor cards (newest first), expandable ---- */
  function buildCards() {
    var host = document.getElementById("am-cards"); if (!host) return;
    host.innerHTML = "";
    TERMS.slice().reverse().forEach(function (T) {
      if (T.name === AN.name) return;
      var det = document.createElement("details");
      det.className = "am-card";
      var tierCls = T.tier === "A" ? "A" : (T.tier === "B" ? "B" : "M");
      det.innerHTML =
        '<summary class="am-sum">' +
        '<span class="am-chev">▸</span>' +
        '<span class="am-name">' + T.cn + '<small>' + T.inaug.slice(0, 4) + '–' + T.end.slice(0, 4) + ' · ' + T.era + '</small></span>' +
        '<span class="sm-t sm-t-' + tierCls + '">' + T.tier + '</span>' +
        '<span class="am-ministrip"></span>' +
        nowChip(T) +
        '<span class="am-ntr">' + T.transitions.length + ' 次轉區</span>' +
        '</summary>' +
        '<div class="am-body">' +
        '<div class="am-bigstrip"></div>' +
        '<div class="am-tt-wrap"></div>' +
        (T.trough ? '<p class="am-trough">▾ 任內大底 <b class="mono">' + T.trough.date + '</b>（' + T.trough.year + '，對標現任時間 <b class="mono">' + fmtA(T.trough.anchor) + '</b>）' + (T.trough.midterm_low ? ' <span class="cov-b">★中期年樣本</span>' : '') + ' — ' + T.trough.note + '</p>' : '') +
        '</div>';
      host.appendChild(det);
      drawStrip(det.querySelector(".am-ministrip"), T, false);
      det.addEventListener("toggle", function () {
        if (det.open && !det.dataset.drawn) {
          drawStrip(det.querySelector(".am-bigstrip"), T, true);
          det.querySelector(".am-tt-wrap").innerHTML = transTable(T);
          det.dataset.drawn = "1";
        }
      });
    });
  }

  var ea = document.getElementById("am-expand-all"), ca = document.getElementById("am-collapse-all");
  if (ea) ea.addEventListener("click", function () {
    document.querySelectorAll(".am-card").forEach(function (d) { d.open = true; });
  });
  if (ca) ca.addEventListener("click", function () {
    document.querySelectorAll(".am-card").forEach(function (d) { d.open = false; });
  });

  drawMaster();
  buildCards();
})();
