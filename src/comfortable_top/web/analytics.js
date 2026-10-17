"use strict";
const query=new URLSearchParams(location.search), canvas=document.querySelector("canvas"), ctx=canvas.getContext("2d");
const processMode=query.get("mode")==="process", pid=Number(query.get("pid")), created=Number(query.get("created"));
let payload=null, range=90;
let language=query.get("lang")==="zh"?"zh":"en";
const copy={
  en:{title:"Resource history",waiting:"Waiting for first sample",samples:"samples",memory:"Memory",warmup:"warmup",
    exited:"exited",empty:"No sample",chart:"CPU and memory history",page:"Comfortable Top · local analytics",
    eyebrow:"COMFORTABLE / TELEMETRY",overview:"Click a process to focus its TUI row. Browser range is independent for each page.",
    process:"Process CPU: 100% = one core; graph clips above 100%. Values remain exact in TUI.",processCPU:"Process CPU"},
  zh:{title:"资源历史",waiting:"等待首次采样",samples:"个采样点",memory:"内存",warmup:"预热中",
    exited:"已退出",empty:"暂无采样",chart:"CPU 与内存历史",page:"Comfortable Top · 本机分析",
    eyebrow:"COMFORTABLE / 系统指标",overview:"点击进程可定位终端中的对应行。每个页面的显示范围独立。",
    process:"进程 CPU 100% = 一个核心；曲线裁剪到 100%，终端表格保留精确值。",processCPU:"进程 CPU"}
};
const t=key=>copy[language][key];
function setLanguage(value){
  if(value!=="zh"&&value!=="en")return;
  language=value;
  document.documentElement.lang=value==="zh"?"zh-CN":"en";
  document.title=t("page");
  document.querySelector(".eyebrow").textContent=t("eyebrow");
  document.querySelector("#memory-label").textContent=t("memory");
  document.querySelectorAll("[data-range]").forEach(button=>button.textContent=`${button.dataset.range} ${t("samples")}`);
  canvas.setAttribute("aria-label",t("chart"));canvas.title="";
  document.querySelector("#title").textContent=t("title");
  document.querySelector("#badge").textContent=t("waiting");
  document.querySelector("#detail").textContent=t(processMode?"process":"overview");
  draw();
}
document.querySelectorAll("[data-range]").forEach(button=>button.onclick=()=>{range=Number(button.dataset.range);draw();});
function historyRows(){
  const watched=(payload?.watched||[]).find(p=>p.pid===pid&&p.created===created);
  return processMode?(watched?.history||[]).slice(-range).map(v=>[0,v,null]):(payload?.history||[]).slice(-range);
}
function draw(){
  if(!payload)return;
  const watched=(payload.watched||[]).find(p=>p.pid===pid&&p.created===created);
  const rows=historyRows(), size=canvas.getBoundingClientRect(), ratio=window.devicePixelRatio||1;
  if(size.width<=0||size.height<=0)return;
  const pixelWidth=Math.max(1,Math.round(size.width*ratio)),pixelHeight=Math.max(1,Math.round(size.height*ratio));
  if(canvas.width!==pixelWidth||canvas.height!==pixelHeight){canvas.width=pixelWidth;canvas.height=pixelHeight;}
  ctx.setTransform(ratio,0,0,ratio,0,0);
  ctx.clearRect(0,0,size.width,size.height);
  const left=26,right=Math.max(left+1,size.width-2),bottom=Math.max(9,size.height-7),plotHeight=Math.max(1,bottom-6);
  ctx.font="10px monospace";
  [0,50,100].forEach(v=>{const y=bottom-v*plotHeight/100;ctx.strokeStyle="#29354b";ctx.beginPath();ctx.moveTo(left,y);ctx.lineTo(right,y);ctx.stroke();ctx.fillStyle="#8292ac";ctx.fillText(String(v),0,Math.max(10,y));});
  [1,2].forEach((index)=>{
    ctx.strokeStyle=index===1?"#77e0c2":"#ff79bc";ctx.lineWidth=2;ctx.beginPath();let pen=false;
    rows.forEach((r,i)=>{if(r[index]===null){pen=false;return;}const x=left+i*(right-left)/Math.max(1,rows.length-1),y=bottom-Math.min(100,Math.max(0,r[index]))*plotHeight/100;
      if(pen)ctx.lineTo(x,y);else ctx.moveTo(x,y);pen=true;});ctx.stroke();});
  document.querySelector("#badge").textContent=new Date(payload.timestamp*1000).toLocaleTimeString(language==="zh"?"zh-CN":"en")+" · "+rows.length+" "+t("samples");
  const p=processMode?watched?.process:payload.selected;
  document.querySelector("#title").textContent=processMode?(p?`${p.name} · PID ${p.pid}`:`PID ${pid} · ${t("exited")}`):t("title");
  document.querySelector("#detail").textContent=t(processMode?"process":"overview");
  const holder=document.querySelector("#processes");holder.replaceChildren();
  (processMode?(p?[p]:[]):payload.processes.slice(0,12)).forEach(p=>{
    const button=document.createElement("button");button.textContent=`${p.pid} ${p.name} · ${p.cpu===null?t("warmup"):p.cpu.toFixed(1)+"%"}`;
    button.onclick=()=>comfortable.publish("monitor.select",{pid:p.pid,created:p.created});holder.append(button);});
}
document.addEventListener("DOMContentLoaded",()=>{
  setLanguage(language);
  comfortable.subscribe("monitor.locale",event=>setLanguage(event.payload?.language));
  comfortable.subscribe("monitor.sample",event=>{
    payload=event.payload;
    if(payload.language===language)draw();else setLanguage(payload.language);
  });
  comfortable.subscribe("monitor.probe",event=>{
    const p=event.payload;
    const bounds=canvas.getBoundingClientRect();
    comfortable.publish("monitor.proof",{token:p.token,received:payload!==null&&payload.processes.length>0,mode:processMode?"process":"overview",
      language,range,title:document.querySelector("#title").textContent,
      viewport:{width:innerWidth,height:innerHeight,documentWidth:document.documentElement.scrollWidth,
        chartWidth:bounds.width,chartHeight:bounds.height,titleSize:parseFloat(getComputedStyle(document.querySelector("h1")).fontSize)}});
    if(!processMode&&payload?.processes.some(row=>row.pid===p.pid&&row.created===p.created))
      comfortable.publish("monitor.select",{pid:p.pid,created:p.created});
  });
});
new ResizeObserver(draw).observe(canvas);
canvas.addEventListener("mousemove",e=>{
  if(!payload)return;const rows=historyRows(),r=rows[Math.round((e.offsetX/canvas.clientWidth)*(rows.length-1))];
  const value=r?.[1]===null?t("warmup"):`${r?.[1]}%`;
  canvas.title=r?(processMode?`${t("processCPU")} ${value}`:new Date(r[0]*1000).toLocaleTimeString(language==="zh"?"zh-CN":"en")+` CPU ${value} · ${t("memory")} ${r[2]}%`):t("empty");
});
