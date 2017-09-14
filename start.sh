#!/bin/bash
source venv3/bin/activate

mkdir -p log
python -m http.server 80 &> ./log/web-server.log &

python -m ecosystem.wsserver.py
