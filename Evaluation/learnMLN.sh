#!/usr/bin/env bash

echo "save name: $1"
echo "database file: $2"
echo "info file: $3"
echo "type file: $4"
echo "lsmcode_dir: $5"
echo "data_dir: $6"
echo "MLN_dir: $7"

echo "Running random walks..."
$5/rwl/rwl $6/$3 $6/$2 $6/$4 10000 5 0.05 0.1 4.9 0.1 1 3 1 $6/$1.ldb $6/$1.uldb $6/$1.srcnclusts > $6/$1-rwl.log

echo "Extracting motifs..."
$5/getcom/getcom $6/$1.ldb $6/$1.uldb $6/$1.srcnclusts $6/$3 10 $6/$1.comb.ldb NOOP true 1 > $6/$1-getcom.log

echo "Path finding..."
$5/pfind2/pfind $6/$1.comb.ldb 5 0 5 -1.0 $6/$3 $6/$1.rules > $6/$1-findpath.log

echo "Creating MLN rules..."
$5/createrules/createrules $6/$1.rules 0 $6/$2 $6/$1.comb.ldb $6/$1.uldb $6/$3 $5/alchemy30/bin/learnwts $5/createrules/tmpdir 0.5 0.1 0.1 100 5 100 1000 1 $7/$1-rules.mln 1 - - true false 40 > $6/$1-createrules.log

echo "Computing optimal weights..."
$5/alchemy30/bin/learnwts -g -i $7/$1-rules.mln -o $7/$1-rules-out.mln -t $6/$2


