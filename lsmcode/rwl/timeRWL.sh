#!/usr/bin/env bash

#echo "save name: $1"
#echo "database file: $2"
#echo "info file: $3"
#echo "type file: $4"
#echo "data_dir: $5"

#echo "Running random walks..."
./rwl $5/$3 $5/$2 $5/$4 10000 5 0.05 0.1 4.9 0.1 1 3 1 $5/$1.ldb $5/$1.uldb $5/$1.srcnclusts > $5/$1-rwl.log


