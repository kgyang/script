#!/usr/bin/env bash


function usage() {
    echo "$0 <mp4file>" >&2
    exit 1
}

[[ $# -eq 1 && -f $1 ]] || usage
srcfile=$1
dstfile=$(dirname $srcfile)/wm_$(basename $srcfile)

set -x

ffmpeg -y -i $srcfile -filter_complex "
[0:v]
drawtext='
font=Times:
fontsize=20:x=20:y=20:
fontcolor=red@0.8:
text=Èý(2)°à ÑîÀÖÐÐ'
" $dstfile
