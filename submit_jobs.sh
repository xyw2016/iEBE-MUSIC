#!/bin/bash

if [ -z "$1" ]; then
    echo "Usage: $0 "
    exit 1
fi

path0="$1"

cd ${path0}
pwd
#NT=$(ls event_* 2> /dev/null | wc -l)
NT=$(find . -maxdepth 1 -name 'event_*' -type d | wc -l)

echo ${NT}

for i in $(seq 0 $((NT-1)) )  
do
    cd "$path0/event_${i}"
    #pwd 
#    # Submit the job using sbatch
#    #sbatch submit_job.pbs
     sbatch submit_job.script
#    # Go back to the home directory
    cd ../..
done

