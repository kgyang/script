#!/usr/bin/bash

function usage() {
    echo "$0 <rawvideo> <croppedvideo>" >&2
    exit 1
}


[[ $# -eq 2 ]] || usage

rawvideo=$1
croppedvideo=$2

[[ -f "$rawvideo" ]] || usage


# crop out top 3.8cm and bottom 3.8 cm, keep central 9.8cm, keep width
#3.8cm
#9.8cm
#3.8cm
set -x
ffmpeg -i $rawvideo -vf crop=in_w:0.5632*in_h:0:0.2183*in_h $croppedvideo

function cropman() {
   echo '
Crop the input video to given dimensions.

It accepts the following parameters:

w, out_w

    The width of the output video. It defaults to iw. This expression is evaluated only once during the filter configuration, or when the ¡®w¡¯ or ¡®out_w¡¯ command is sent.
h, out_h

    The height of the output video. It defaults to ih. This expression is evaluated only once during the filter configuration, or when the ¡®h¡¯ or ¡®out_h¡¯ command is sent.
x

    The horizontal position, in the input video, of the left edge of the output video. It defaults to (in_w-out_w)/2. This expression is evaluated per-frame.
y

    The vertical position, in the input video, of the top edge of the output video. It defaults to (in_h-out_h)/2. This expression is evaluated per-frame.
keep_aspect

    If set to 1 will force the output display aspect ratio to be the same of the input, by changing the output sample aspect ratio. It defaults to 0.
exact

    Enable exact cropping. If enabled, subsampled videos will be cropped at exact width/height/x/y as specified and will not be rounded to nearest smaller value. It defaults to 0. 

The out_w, out_h, x, y parameters are expressions containing the following constants:

x
y

    The computed values for x and y. They are evaluated for each new frame.
in_w
in_h

    The input width and height.
iw
ih

    These are the same as in_w and in_h.
out_w
out_h

    The output (cropped) width and height.
ow
oh

    These are the same as out_w and out_h.
a

    same as iw / ih
sar

    input sample aspect ratio
dar

    input display aspect ratio, it is the same as (iw / ih) * sar
hsub
vsub

    horizontal and vertical chroma subsample values. For example for the pixel format "yuv422p" hsub is 2 and vsub is 1.
n

    The number of the input frame, starting from 0.
pos

    the position in the file of the input frame, NAN if unknown
t

    The timestamp expressed in seconds. It¡¯s NAN if the input timestamp is unknown.

The expression for out_w may depend on the value of out_h, and the expression for out_h may depend on out_w, but they cannot depend on x and y, as x and y are evaluated after out_w and out_h.

The x and y parameters specify the expressions for the position of the top-left corner of the output (non-cropped) area. They are evaluated for each frame. If the evaluated value is not valid, it is approximated to the nearest valid value.

The expression for x may depend on y, and the expression for y may depend on x.
39.40.1 Examples

    Crop area with size 100x100 at position (12,34).

    crop=100:100:12:34

    Using named options, the example above becomes:

    crop=w=100:h=100:x=12:y=34

' >&2
   exit 1
}

