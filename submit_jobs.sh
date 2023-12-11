#!/bin/bash

if [ -z "$1" ]; then
    echo "Usage: $0 "
    exit 1
fi

path0="$1"

NT=100
for i in $(seq 0 $((NT-1)) )  
do
    cd "$path0/event_${i}"
    
    # Submit the job using sbatch
    #sbatch submit_job.pbs
    sbatch submit_job.pbs
    # Go back to the home directory
    cd ../..
done

