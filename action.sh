#!/bin/bash

# Run script to all pairs
for pair in $(cat tickers.txt) 
do 
	python3 todb_binance.py "$pair"
	sleep 1
done

exit 0