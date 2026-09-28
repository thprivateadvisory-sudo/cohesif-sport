const {chromium}=require('playwright');
const fs=require('fs'),{spawn}=require('child_process');
(async()=>{
  const mode=process.argv[2]||'preview';
  const tl=fs.readFileSync('timeline.json','utf8');
  fs.writeFileSync('ad_built.html',fs.readFileSync('ad.html','utf8').replace('__TIMELINE__',tl));
  const b=await chromium.launch({args:['--font-render-hinting=none']});
  const p=await b.newPage({viewport:{width:1080,height:1920}});
  p.on('pageerror',e=>console.error('ERR',e.message));
  await p.goto('file://'+process.cwd()+'/ad_built.html');await p.evaluate(()=>document.fonts.ready);
  await p.waitForTimeout(300);
  if(mode==='preview'){
    for(const t of process.argv.slice(3).map(Number)){await p.evaluate(t=>render(t),t);await p.screenshot({path:`prev_${t}.jpg`,type:'jpeg',quality:80});}
  }else{
    const dur=await p.evaluate(()=>DUR);const fps=30,n=Math.ceil(dur*fps);
    const ff=spawn('ffmpeg',['-y','-loglevel','error','-f','image2pipe','-framerate','30','-c:v','mjpeg','-i','-','-c:v','libx264','-preset','medium','-crf','17','-pix_fmt','yuv420p','video.mp4'],{stdio:['pipe','inherit','inherit']});
    for(let i=0;i<n;i++){await p.evaluate(t=>render(t),i/fps);const buf=await p.screenshot({type:'jpeg',quality:95});
      if(!ff.stdin.write(buf))await new Promise(r=>ff.stdin.once('drain',r));if(i%150==0)console.log(i,'/',n);}
    ff.stdin.end();await new Promise(r=>ff.on('close',r));
  }
  await b.close();
})();
