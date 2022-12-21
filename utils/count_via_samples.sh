#!/bin/bash

ANNOT_CSV_PATH=via.csv

tail "${ANNOT_CSV_PATH}" -n +2 | cut -f1 -d, | sort | uniq | wc -l
