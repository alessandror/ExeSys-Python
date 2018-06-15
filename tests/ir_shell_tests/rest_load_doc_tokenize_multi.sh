#! /bin/bash

curl -H "Content-type: application/json" \
-X POST http://127.0.0.1:5000/exesyscmds -d '{"from":"testclient","to":"tokenize","cmd":"tika_read_document","data":["filesys-single","/Users/alexr/test_docs/test0.pdf","redis"],"job_id":"00fd2706-8baf-433b-82eb-8c7fada847da"}'

curl -H "Content-type: application/json" \
-H "Operation: workflow" \
-X POST http://127.0.0.1:5000/exesyscmds -d '{"from":"tokenize","to":"end_job","cmd":"regex_tokenizer","data":["redis","filetext:test0:pdf","redis","tokens:test0:pdf"],"job_id":"00fd2706-8baf-433b-82eb-8c7fada847da"}'



curl -H "Content-type: application/json" \
-X POST http://127.0.0.1:5000/exesyscmds -d '{"from":"testclient","to":"tokenize","cmd":"tika_read_document","data":["filesys-single","/Users/alexr/test_docs/criton_p.pdf","redis"],"job_id":"00fd2706-8baf-433b-82eb-8c7fada847db"}'

curl -H "Content-type: application/json" \
-H "Operation: workflow" \
-X POST http://127.0.0.1:5000/exesyscmds -d '{"from":"tokenize","to":"end_job","cmd":"regex_tokenizer","data":["redis","filetext:criton_p:pdf","redis","tokens:criton_p:pdf"],"job_id":"00fd2706-8baf-433b-82eb-8c7fada847db"}'



curl -H "Content-type: application/json" \
-X POST http://127.0.0.1:5000/exesyscmds -d '{"from":"testclient","to":"tokenize","cmd":"tika_read_document","data":["filesys-single","/Users/alexr/test_docs/il_fed_p.pdf","redis"],"job_id":"00fd2706-8baf-433b-82eb-8c7fada847dc"}'

curl -H "Content-type: application/json" \
-H "Operation: workflow" \
-X POST http://127.0.0.1:5000/exesyscmds -d '{"from":"tokenize","to":"end_job","cmd":"regex_tokenizer","data":["redis","filetext:il_fed_p:pdf","redis","tokens:il_fed_p:pdf"],"job_id":"00fd2706-8baf-433b-82eb-8c7fada847dc"}'
