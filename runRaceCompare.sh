#!/bin/bash

SOURCE_PATH=$1
TEMP_OUT="tempFromRunRaceCompare.exe"
LOG="runCompareLog.txt"

if [ -z $SOURCE_PATH ]; then
   echo Usage: runRaceCompare path/to/cSource.c
   exit 0
fi

gcc -o $TEMP_OUT $SOURCE_PATH -g -fopenmp
valgrind --tool=helgrind --error-exitcode=1 ./$TEMP_OUT 2>$LOG
if [ $? -eq 0 ]; then
   echo Helgrind: NO
else
   echo Helgrind: YES
fi
gcc -o $TEMP_OUT $SOURCE_PATH -fsanitize=thread -g -fopenmp
./$TEMP_OUT 2>> $LOG

if [ $? -eq 0 ]; then
   echo Thread Sanitizer: NO
else
   echo Thread Sanitizer: YES
fi
