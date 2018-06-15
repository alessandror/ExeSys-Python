#! /bin/bash

CURRENT=`pwd`

echo -e '\033[32m >>>> running exe sys...'

echo -e '\033[37m'

echo 'current dir: '${CURRENT}

cd ${CURRENT}/ExeSysMain

CMD=${CURRENT}/ExeSysMain/startexesys.py

echo 'command: python '$CMD

#PYTHONPATH=${CURRENT}:${CURRENT}/ExeSys:${CURRENT}/ExeSysFunctionalModules python ${CMD}

PYTHONPATH=${CURRENT}:${CURRENT}/ExeSysMain:${CURRENT}/ExeSysMain/ExeSysFunctionalModules python ${CMD}

echo -e '\033[32m >>>> exe sys ended'
