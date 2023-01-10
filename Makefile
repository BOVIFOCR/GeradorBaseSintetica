ANNOTATIONS_ROOT_PATH?=${PWD}/../preannot-rg
IMAGES_SOURCE_ROOT_PATH?=${PWD}/../preannot-rg/data
SIDE?=front

REMOTE_HOST=duo
REMOTE_URL=/home/jpmartinez/rg_novo/synthesis_output/nbid

PY_VENV_PATH=${PWD}/.venv

PY_VERSION = ${PY_VENV_PATH}/bin/python --version

export PYTHONPATH := ${PYTHONPATH}:${PWD}/src/
export PYTHONPATH := ${PYTHONPATH}:${PWD}/lib/multiprocessing_lib/src/
export PYTHONPATH := ${PYTHONPATH}:${PWD}/utils/

ANNOTATIONS_PATH := ${ANNOTATIONS_ROOT_PATH}/output/${SIDE}
IMAGES_SOURCE_PATH := ${IMAGES_SOURCE_ROOT_PATH}/data/${SIDE}

SYNTH_INPUT_PATH := synthesis_input/${SIDE}
SYNTH_OUTPUT_PATH := synthesis_output/${SIDE}

SIDE_ARG = `echo "$${SIDE:+--sample-label ${SIDE}}"`
NUM_SAMPLES_ARG := `echo "$${NUM_SAMPLES:+--max-num-samples ${NUM_SAMPLES}}"`
MAIN_SCRIPT_ARGS = ${SIDE_ARG} ${NUM_SAMPLES_ARG}

prep_dirs:
	mkdir -p ${SYNTH_INPUT_PATH} ${SYNTH_OUTPUT_PATH}

cp_data:
	rm via.csv ${SYNTH_INPUT_PATH}/input -rf ;\
	cp ${ANNOTATIONS_PATH}/via.csv . ;\
	cp -r ${ANNOTATIONS_PATH}/warped ${SYNTH_INPUT_PATH}/input

prep_labels: via.csv
	rm ${SYNTH_INPUT_PATH}/labels/* ;\
	${PY_VENV_PATH}/bin/python utils/data_formatters/splitter.py via.csv


run_anonimize: src/anonimize_input.py
	echo "main script args: ${MAIN_SCRIPT_ARGS}"
	${PY_VENV_PATH}/bin/python -u src/anonimize_input.py ${MAIN_SCRIPT_ARGS} 2> /dev/null

debug_anonimize: src/anonimize_input.py
	${PY_VENV_PATH}/bin/python -u src/anonimize_input.py ${MAIN_SCRIPT_ARGS}

clean_anonimize:
	rm -rf ${SYNTH_OUTPUT_PATH}/back


run_synth: src/synthesize_bgs.py
	${PY_VENV_PATH}/bin/python -u src/synthesize_bgs.py ${MAIN_SCRIPT_ARGS} 2> /dev/null

debug_synth: src/synthesize_bgs.py
	${PY_VENV_PATH}/bin/python -u src/synthesize_bgs.py ${MAIN_SCRIPT_ARGS}


run_partition: src/partition_dataset.py
	${PY_VENV_PATH}/bin/python -u src/partition_dataset.py cross reboot
	mkdir -p ${SYNTH_OUTPUT_PATH}/nbid/images ${SYNTH_OUTPUT_PATH}/nbid/boxes_and_transcripts
	mv train.csv valid.csv test.csv ${SYNTH_OUTPUT_PATH}/nbid/
	find ${SYNTH_OUTPUT_PATH}/reboot -type f -name "*.jpg" | grep -v "mask_GT" | xargs -I@ cp @ ${SYNTH_OUTPUT_PATH}/nbid/images/
	find ${SYNTH_OUTPUT_PATH}/reboot -type f -name "*.tsv" | xargs -I@ cp @ ${SYNTH_OUTPUT_PATH}/nbid/boxes_and_transcripts/

clean_synth:
	rm -rf ${SYNTH_OUTPUT_PATH}/mask ${SYNTH_OUTPUT_PATH}/reboot

clean_debug:
	rm -rf ${SYNTH_OUTPUT_PATH}/debug

clean_partition:
	rm -rf ${SYNTH_OUTPUT_PATH}/nbid

upload:
	rsync -avzh ${SYNTH_OUTPUT_PATH}/reboot \
		output/
		$(REMOTE_HOST):$(REMOTE_URL)
	ssh $(REMOTE_HOST) "echo 'feitoo' > $(REMOTE_URL)/.upload_status


clean clean_all: clean_anonimize clean_debug clean_synth clean_partition
	rm -f via.csv

run run_all: run_anonimize run_synth run_partition
rerun: cp_data prep_labels run

.PHONY: clean%
