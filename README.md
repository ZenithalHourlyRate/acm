# AsCii Movie

Namely, this repo provides utils on converting normal videos to AsCii movies.

## Examples

Bad Apple

```bash
# we assume that you get the original video of bad apple by some means
#youtube-dl some-url
export VID=badapple.mp4
export N=$((`nproc`-1))
export TMPDIR=$(mktemp -d)
export RAW=$TMPDIR/raw
export ASC=$TMPDIR/asc
mkdir $RAW
mkdir $ASC
bash utils/ffmpeg.in.sh $VID 30 $RAW/%05d.png
parallel python img2ascii.py -j $N -n {} -i "$RAW/{:05d}.png" -o "$ASC/{:05d}.png" -s 40x12 -g ::: `seq "$N"`
bash utils/ffmpeg.out.sh $ASC/%05d.png 30 asc.$VID
bash utils/ffmpeg.merge.sh $VID asc.$VID final.$VID
rm -r $TMPDIR
```
