#!/usr/bin/bash

if [ $# -lt 3 ]
then
  echo "Usage: $0 input_format frame_rate output_video"
  echo "Example: $0 /tmp/img/%04d.png 30 badapple_ascii.mp4"
  exit -1
fi

ffmpeg -r $2 -i $1 $3
