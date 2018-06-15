#! /bin/bash

#start jobs
declare -i start=$1
declare -i stop=$2
let "start += $stop"
eval "stop=$start"

for ((i=$1;i<$stop;i++))
do
   echo "Test-> $i"
   curl -H "Content-type: application/json" \
-X POST http://127.0.0.1:50000/sys_cmd -d "{\"from\":\"testclient\",\"to\":\"testjob\",\"cmd\":\"test_cmd\",\"data\":[\"$i\",\"test1\"],\"job_id\":\"00fd2706-8baf-433b-82eb-8c7fada847d$i\"}"
 
done

