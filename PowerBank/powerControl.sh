#!/bin/sh
export LD_LIBRARY_PATH=/home/wcs-server/powerBank/lib:$LD_LIBRARY_PATH
~/powerBank/powerControl $1 $2 &

