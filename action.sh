#!/bin/bash

# Go to home directory
cd ~

# First set up db server
echo <password> | sudo -S -u postgres /Library/PostgreSQL/12/bin/pg_ctl -D /Library/PostgreSQL/12/data start

# Activate env
source ~/anaconda3/etc/profile.d/conda.sh
conda activate quant

# Run python script
python ~/bin/download_bitcoin.py
sleep 5
python ~/bin/download_ether.py
sleep 5
python ~/bin/download_ripple.py
sleep 5
python ~/bin/download_binance.py


# Stop db server
echo facil | sudo -S -u postgres /Library/PostgreSQL/12/bin/pg_ctl -D /Library/PostgreSQL/12/data stop