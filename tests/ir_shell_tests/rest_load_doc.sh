#! /bin/bash

curl -H "Content-type: application/json" \
-X POST http://127.0.0.1:5000/exesyscmds -d '{"from":"testclient","to":"end_job","cmd":"tika_read_document","data":["filesys-single","/Users/alexr/test_docs/il_fed_p.pdf","redis"],"job_id":"00fd2706-8baf-433b-82eb-8c7fada847da"}'

