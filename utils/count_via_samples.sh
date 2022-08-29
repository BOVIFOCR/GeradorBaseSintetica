#!/bin/bash

ANNOT_CSV_PATH=via.csv

cat $ANNOT_CSV_PATH | tail -n +2 | cut -f1 -d, | sort | uniq | wc -l
