#! /bin/bash

curl -H "Content-type: application/json" \
-X POST http://127.0.0.1:50000/exesyscmds -d '{"from":"testclient","to":"end_job","cmd":"test_cmd","data":["test0","test1"],"job_id":"00fd2706-8baf-433b-82eb-8c7fada847da"}'

curl -H "Content-type: application/json" \
-X POST http://127.0.0.1:50000/exesyscmds -d '{"from":"testclient","to":"end_job","cmd":"test_cmd","data":["test0","test1"],"job_id":"01fd2706-8baf-433b-82eb-8c7fada847da"}'
