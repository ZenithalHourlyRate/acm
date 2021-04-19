#!/usr/bin/bash

if [ $# -lt 3 ]
then
  echo "Usage: $0 origin_video ascii_video output_video"
  echo "Example: $0 badapple.mp4 badapple_ascii.mp4 badapple_final.mp4"
  exit -1
fi

TMPDIR=$(mktemp -d) || exit 1

ffmpeg -i $2 $TMPDIR/audio.aac
ffmpeg -i $1 -i $TMPDIR/audio.aac $3

rm -r $TMPDIR
