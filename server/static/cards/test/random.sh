#!/usr/bin/env bash

for i in {1..100}
do
    curl -L -o img_$i.jpg https://picsum.photos/512/512.jpg
done
