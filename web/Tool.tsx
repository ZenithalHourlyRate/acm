import React, { useState, useMemo, useEffect } from "react";
import defaultImg from "url:./dram.png";

const charWidth=10; // pixel
const charHeight=20; // pixel
const charset = " .-~^*=#";

export default React.memo(() => {
  const [imgUrl, setImgUrl] = useState<string>(defaultImg);
  const handleUpload = e => setImgUrl(URL.createObjectURL(e.target.files[0]));

  const [imgHeight, setImgHeight] = useState<number>(0);
  const [imgWidth, setImgWidth] = useState<number>(0);

  const ctx = useMemo<any>(() => {
    if (!imgUrl)
      return null;
    const canvas = document.createElement("CANVAS");
    const ctx = canvas.getContext("2d");
    const img = new Image;
    img.onload = () => {
      canvas.height = img.height;
      canvas.width = img.width;
      ctx.drawImage(img, 0, 0);
      setImgHeight(img.height);
      setImgWidth(img.width);
      //document.body.appendChild(canvas);
      console.log("Img info", imgWidth, imgHeight);
    };
    img.src = imgUrl;
    console.log(imgUrl);
    return ctx;
  }, [imgUrl]);
 
  const render = async (i, j) => {
    // sleep for some random time
    await new Promise(resolve => setTimeout(resolve, Math.random()*500));
    const data = ctx.getImageData(charWidth*i, charHeight*j, charWidth, charHeight).data;
    const gray = data.reduce((r, c, i, a) => { if (i % 4 == 0) r.push((a[i]+a[i+1]+a[i+2])/3); return r; }, [])
                     .reduce((r, c) => r + c, 0) / (data.length/4);
    const char = charset[Math.floor((gray / 256)*charset.length)];
    return char;
  };
  const [renderNum, setRenderNum] = useState<number>(0);
 
  const [acm, setAcm] = useState<string[][]>([[]]); // place holder

  useEffect(() => {
    if (!ctx || imgHeight == 0 || imgWidth == 0) // placeholder
      return
    setAcm(Array.from(Array(Math.floor(imgHeight/charHeight)),
                () => Array(Math.floor(imgWidth/charWidth)).fill('#')))
  }, [ctx, imgHeight, imgWidth]);

  useEffect(() => {
    acm.forEach((l, j) => l.forEach((c, i) => render(i, j).then(m => { acm[j][i] = m; setRenderNum(n => n+1); })));
  }, [acm]);

  return (
    <div className="tool">
      <input type="file" accept="image/*" onChange={handleUpload} />
      <div>Rendered: {renderNum}</div>
      <div className="display">
        <div className="src-img">
          <img src={imgUrl} />
        </div>
        <div className="dst-acm">
          <pre>{ acm.map(l => l.join('')).join('\n') }</pre>
        </div>
      </div>
    </div>
  );
});
