#!/bin/sh
cd $3
code=2
count=0
while [ $code -eq 2 ] && [ $count -lt 10 ]
do
    echo "TRYING POWER" $2 $1
    ./bin/powerControl $1 $2
    code=$?
    count=$(($count+1))
    sleep 0.5
done
