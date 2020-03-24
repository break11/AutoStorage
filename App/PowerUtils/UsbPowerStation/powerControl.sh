#!/bin/sh
cd $3
code=2
count=0
max_retries=10
while [ $code -eq 2 ] && [ $count -lt $max_retries ]
do
    echo "TRYING POWER" $2 $1
    ./bin/powerControl $1 $2
    code=$?
    count=$(($count+1))
    sleep 0.5
done

if [ $count -eq $max_retries ]
then
    echo "\e[31mMax retries exceeded to power" $2 "port:" $1 "\e[39m"
fi