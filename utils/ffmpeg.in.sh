#!/usr/bin/bash

if [ $# -lt 3 ]
then
  echo "Usage: $0 video_file frame_rate output_format"
  echo "Example: $0 badapple.mp4 30 /tmp/badapple/%04d.png"
  exit -1
fi

ffmpeg -i $1 -vf fps=$2 $3
