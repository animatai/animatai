#!/bin/bash
mkdir -p log
python -m http.server 80 &> ./log/web-server.log &

python -m animatai.wsserver
