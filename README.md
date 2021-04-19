# AsCii Movie

Namely, this repo provides utils on converting normal videos to AsCii movies.

## Examples

Bad Apple

```bash
# we assume that you get the original video of bad apple by some means
#youtube-dl some-url
mkdir /tmp/badapple
mkdir /tmp/img
bash utils/ffmpeg.in.sh badapple.mp4 30 /tmp/badapple/%04d.png
export N=$((`nproc`-1))
parallel python img2ascii.py -j $N -n {} -i '/tmp/ba/{:04d}.png' -o '/tmp/img/{:04d}.png' -g ::: `seq "$N"`
bash utils/ffmpeg.out.sh /tmp/img/%04d.png 30 badapple_ascii.mp4
bash utils/ffmpeg.merge.sh badapple.mp4 badapple_ascii.mp4 badapple_final.mp4
```
