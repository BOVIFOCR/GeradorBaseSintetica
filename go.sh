#!/bin/bash

PREANNOT_SRC_PATH=/home/jpsmartinez/codes/unico/snippets/preannot-rg/
SIDE=front
ANOM_OUT_DIRS="back tile crop"
SYNTH_OUT_DIRS="mask reboot"


cp_data () {
    rm via.csv input -rf ;
    cp $PREANNOT_SRC_PATH/output/$SIDE/via.csv .
    cp -r $PREANNOT_SRC_PATH/output/$SIDE/warped input
}

prep_labels () {
    rm labels/* ;
    python splitter.py via.csv ;
}

anonimize () {
    rm  -rf $ANOM_OUT_DIRS ;
    mkdir -p $ANOM_OUT_DIRS && \
    python -u anonimize_input.py ;
}

synth () {
    rm -rf $SYNTH_OUT_DIRS ;
    mkdir -p $SYNTH_OUT_DIRS && \
    python -u synthesize_bgs.py ;
}

source .venv/bin/activate

# cp_data &&\
# prep_labels &&\
anonimize &&\
synth &&\
echo "Done!"