import React, { useState, useMemo, useEffect } from "react";
import distanceTransform from "distance-transform";
import ndarray from "ndarray";

import defaultImg from "url:./dram.png";

const charWidth = 10; // pixel
const charHeight = 20; // pixel
const gray_charset = " .-~^*=#";
const sdf_charset = ' .\'`^_-~:+/\\|[]#';

const sleep = async (ms) => {
  await new Promise(resolve => setTimeout(resolve, ms));
}

const font2img = async (char: string) => {
  const canvas = document.createElement("CANVAS");
  canvas.height = charHeight;
  canvas.width = charWidth;
  const ctx = canvas.getContext("2d");
  ctx.fillStyle = "#FFFFFF";
  ctx.fillRect(0, 0, charWidth, charHeight);
  ctx.fillStyle = "#000000";
  ctx.font = charHeight.toString()+"px monospace";
  ctx.fillText(char, 0, charHeight-5); // left bottom corner
  // dirty -5 here, otherwise truncated; use the following appendChild to preview
  //document.body.appendChild(canvas);
  return ctx.getImageData(0, 0, charWidth, charHeight);
}

const img2sdf = async (data: ImageData) => {
  const gray = data.data.reduce((r, c, i, a) => { if (i % 4 == 0) r.push(((a[i]+a[i+1]+a[i+2])/3 < 127 ? 1 : 0)); return r; }, []); // why less than? different lib has different def
  const inv = gray.map(g => 1 - g); // invert
  const sdf_array = distanceTransform(ndarray(gray ,[charHeight, charWidth])).data;
  const sdf_inv_array = distanceTransform(ndarray(inv, [charHeight, charWidth])).data;
  var sdf_sum = sdf_array.map((c, i) => c + sdf_inv_array[i]);
  // normalize sdf_sum
  const m = Math.min(...sdf_sum);
  const n = Math.max(...sdf_sum);
  sdf_sum = sdf_sum.map((c) => c - m);
  if (n != m)
    sdf_sum = sdf_sum.map((c) => c / (n - m));
  const gray_sum = gray.reduce((r, c) => r + c, 0);
  if (gray_sum > 0)
    sdf_sum = sdf_sum.map((c) => c / (gray_sum / gray.length));
  return sdf_sum;
}

export default React.memo(() => {
  const [charSdf, setCharSdf] = useState<(string | number)[][]>([]);
  useEffect(() =>
    Array.from(sdf_charset).map(c => font2img(c).then(m => img2sdf(m).then(m => setCharSdf(sdf => [...sdf, [c, m]]) )))
  , []);

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
    };
    img.src = imgUrl;
    return ctx;
  }, [imgUrl]);
 
  const [renderNum, setRenderNum] = useState<number>(0);
  const grayRender = async (i, j) => {
    // sleep for some random time
    await sleep(100*Math.random());
    const data = ctx.getImageData(charWidth*i, charHeight*j, charWidth, charHeight).data;
    const gray = data.reduce((r, c, i, a) => { if (i % 4 == 0) r.push((a[i]+a[i+1]+a[i+2])/3); return r; }, [])
                     .reduce((r, c) => r + c, 0) / (data.length/4);
    const char = gray_charset[Math.floor((gray / 256)*gray_charset.length)];
    return char;
  };
  const sdfRender = async (i, j) =>  {
    // sleep for some random time
    await sleep(100*Math.random());
    const imageData = ctx.getImageData(charWidth*i, charHeight*j, charWidth, charHeight);
    const sdf = await img2sdf(imageData);
    return charSdf.map(([k, v]) => [k, v.map((w, i) => Math.floor(Math.abs(w - sdf[i]))).reduce((r, c) => r + c, 0)])
          .reduce((r, c) => r[0] ? (r[1] > c[1] ? c : r) : c, ['', 0])[0];
  }
 
  const [acm, setAcm] = useState<string[][]>([[]]);
  useEffect(() => {
    if (!ctx || imgHeight == 0 || imgWidth == 0)
      return
    setAcm(Array.from(Array(Math.floor(imgHeight/charHeight)),
                () => Array(Math.floor(imgWidth/charWidth)).fill('#')))
  }, [ctx, imgHeight, imgWidth]);

  useEffect(() => {
    if (charSdf.length != sdf_charset.length)
      return; // do not render when charSdf is not ready
    acm.forEach((l, j) => l.forEach((c, i) => sdfRender(i, j).then(m => { acm[j][i] = m; setRenderNum(n => n+1); })));
  }, [acm, charSdf]);

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
