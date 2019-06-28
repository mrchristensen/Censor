#!/bin/bash

cat example.c
read
echo analyzing
python3 main.py --tool cesk demo/example.c
read
cat example-safe.c
read
echo analyzing
python3 main.py --tool cesk demo/example-safe.c
