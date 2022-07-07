#!/bin/bash

PREANNOT_SRC_PATH=/home/jpsmartinez/codes/unico/snippets/preannot-rg/
SIDE=front
OUT_DIRS="rot dpi back reboot rot crops mask"


cp_data () {
    rm via.csv input -rf ;
    cp $PREANNOT_SRC_PATH/output/$SIDE/via.csv .
    cp -r $PREANNOT_SRC_PATH/output/$SIDE/warped input
}

prep_labels() {
    rm labels/* ;
    python splitter.py via.csv ;
}

synth () {
    rm  -rf $OUT_DIRS ;
    mkdir -p $OUT_DIRS && \
    python generic_img_generator.py ;
}

cp_data &&\
prep_labels &&\
synth
