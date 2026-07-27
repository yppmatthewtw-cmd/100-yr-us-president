(function(){
  var SVGNS="http://www.w3.org/2000/svg";
  var ZCOL={E:"var(--easy)",U:"var(--unc)",H:"var(--hard)"};
  var ZBAND={E:"rgba(62,207,142,.13)",U:"rgba(230,178,61,.13)",H:"rgba(242,107,127,.14)"};
  var ZNAME={E:"EASY 寬鬆",U:"UNCERTAIN 震盪",H:"HARD 緊縮"};
  function dnum(s){var p=s.split("-");return Date.UTC(+p[0],+p[1]-1,+p[2])/86400000;}
  function el(tag,attrs){var e=document.createElementNS(SVGNS,tag);for(var k in attrs)e.setAttribute(k,attrs[k]);return e;}
  function fmtNum(n){return Math.round(n).toLocaleString();}

  function render(container){
    var name=container.getAttribute("data-pres");
    var pts=DATA.chart[name]; if(!pts||!pts.length)return;
    var segs=DATA.segments[name]||[];
    var keys=(DATA.keydates[name]||[]).filter(function(k){return k.inwin;});
    var W=1000,H=340,mL=54,mR=14,mT=14,mB=52;
    var iw=W-mL-mR, ih=H-mT-mB;
    var t0=dnum(pts[0].t), t1=dnum(pts[pts.length-1].t), tr=Math.max(1,t1-t0);
    var lo=Infinity,hi=-Infinity;
    for(var i=0;i<pts.length;i++){if(pts[i].n<lo)lo=pts[i].n;if(pts[i].n>hi)hi=pts[i].n;}
    var pad=(hi-lo)*0.08||1; lo-=pad; hi+=pad; var vr=hi-lo;
    function X(t){return mL+((t-t0)/tr)*iw;}
    function Y(v){return mT+ih-((v-lo)/vr)*ih;}
    var svg=el("svg",{viewBox:"0 0 "+W+" "+H,preserveAspectRatio:"none",role:"img",
      "aria-label":name+" NDX 走勢與資金三區分段"});

    // zone bands
    for(var s=0;s<segs.length;s++){
      var g=segs[s]; var z=g.zone[0];
      var x1=X(dnum(g.start)), x2=X(dnum(g.end));
      svg.appendChild(el("rect",{x:x1.toFixed(1),y:mT,width:Math.max(0.5,x2-x1).toFixed(1),height:ih,
        fill:ZBAND[z]}));
      // top zone tick line
      svg.appendChild(el("rect",{x:x1.toFixed(1),y:mT,width:Math.max(0.5,x2-x1).toFixed(1),height:3,fill:ZCOL[z],opacity:.85}));
      // label if wide enough
      if(x2-x1>46){
        var tx=el("text",{x:((x1+x2)/2).toFixed(1),y:mT+15,"text-anchor":"middle",
          fill:ZCOL[z],"font-size":"10.5","font-weight":"700"});
        tx.textContent=g.zone[0]==="E"?"EASY":(g.zone[0]==="U"?"UNC":"HARD");
        svg.appendChild(tx);
      }
    }
    // y gridlines + labels
    var ticks=5;
    for(var gi=0;gi<=ticks;gi++){
      var v=lo+vr*gi/ticks; var yy=Y(v);
      svg.appendChild(el("line",{x1:mL,y1:yy.toFixed(1),x2:W-mR,y2:yy.toFixed(1),
        stroke:"var(--line)","stroke-width":gi===0?0:.7,opacity:.5}));
      var lb=el("text",{x:mL-8,y:(yy+3).toFixed(1),"text-anchor":"end",fill:"var(--muted)","font-size":"10"});
      lb.textContent=fmtNum(v); svg.appendChild(lb);
    }
    // year x-axis labels
    var y0=new Date(pts[0].t).getUTCFullYear(), y1=new Date(pts[pts.length-1].t).getUTCFullYear();
    for(var yr=y0;yr<=y1+1;yr++){
      var xd=dnum(yr+"-01-01"); if(xd<t0||xd>t1)continue;
      var xx=X(xd);
      svg.appendChild(el("line",{x1:xx.toFixed(1),y1:mT,x2:xx.toFixed(1),y2:mT+ih,stroke:"var(--line)","stroke-width":.6,opacity:.35}));
      var xl=el("text",{x:xx.toFixed(1),y:mT+ih+16,"text-anchor":"middle",fill:"var(--muted)","font-size":"10.5"});
      xl.textContent=yr; svg.appendChild(xl);
    }
    // NDX line
    var d="";
    for(var p=0;p<pts.length;p++){d+=(p?"L":"M")+X(dnum(pts[p].t)).toFixed(1)+" "+Y(pts[p].n).toFixed(1);}
    svg.appendChild(el("path",{d:d,fill:"none",stroke:"var(--ndx)","stroke-width":1.6,"stroke-linejoin":"round"}));

    // key-date markers
    for(var kx=0;kx<keys.length;kx++){
      var k=keys[kx]; var xk=X(dnum(k.date));
      svg.appendChild(el("line",{x1:xk.toFixed(1),y1:mT+3,x2:xk.toFixed(1),y2:mT+ih,
        stroke:"var(--key)","stroke-width":1.2,"stroke-dasharray":"3 3",opacity:.9}));
      svg.appendChild(el("circle",{cx:xk.toFixed(1),cy:(mT+3).toFixed(1),r:3.2,fill:"var(--key)"}));
      var kl=el("text",{x:xk.toFixed(1),y:(mT+ih+34).toFixed(1),"text-anchor":"middle",fill:"var(--key)","font-size":"9.5","font-weight":"600"});
      kl.textContent=k.label.split(" ")[0]; svg.appendChild(kl);
    }
    container.appendChild(svg);

    // hover layer
    var tip=document.createElement("div"); tip.className="ct-tip"; tip.style.display="none";
    container.appendChild(tip);
    var cross=el("line",{x1:0,y1:mT,x2:0,y2:mT+ih,stroke:"var(--accent)","stroke-width":1,opacity:0});
    var dot=el("circle",{r:3.6,fill:"var(--accent)",opacity:0});
    svg.appendChild(cross); svg.appendChild(dot);
    svg.style.cursor="crosshair";
    svg.addEventListener("mousemove",function(ev){
      var rect=svg.getBoundingClientRect();
      var px=(ev.clientX-rect.left)/rect.width*W;
      var tt=t0+((px-mL)/iw)*tr;
      // nearest point
      var best=0,bd=1e9;
      for(var i=0;i<pts.length;i++){var dd=Math.abs(dnum(pts[i].t)-tt);if(dd<bd){bd=dd;best=i;}}
      var pt=pts[best]; var cxx=X(dnum(pt.t)), cyy=Y(pt.n);
      cross.setAttribute("x1",cxx);cross.setAttribute("x2",cxx);cross.setAttribute("opacity",.6);
      dot.setAttribute("cx",cxx);dot.setAttribute("cy",cyy);dot.setAttribute("opacity",1);
      dot.setAttribute("fill",ZCOL[pt.z]);
      tip.style.display="block";
      tip.style.left=(cxx/W*100)+"%";
      tip.style.top=(cyy/H*100)+"%";
      tip.innerHTML='<div class="mono">'+pt.t+'</div><div class="mono">NDX '+fmtNum(pt.n)+
        '</div><div class="zt" style="color:'+ZCOL[pt.z]+'">'+ZNAME[pt.z]+'</div>';
    });
    svg.addEventListener("mouseleave",function(){tip.style.display="none";cross.setAttribute("opacity",0);dot.setAttribute("opacity",0);});
  }
  document.querySelectorAll(".chart").forEach(render);
})();
