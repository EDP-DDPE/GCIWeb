#!/bin/bash
cd /var/www/atlas/GCIWeb || exit 1
/usr/bin/git fetch --all
/usr/bin/git reset --hard origin/main
source /var/www/atlas/venv/bin/activate
pip install -r requirements.txt
/usr/bin/systemctl restart atlas