ANNOTATIONS_ROOT_PATH ?= ${PWD}/../preannot-rg
IMAGES_SOURCE_ROOT_PATH ?= /home/jpsmartinez/data/acessorh_rg_novo/images

REMOTE_HOST = duo
REMOTE_URL = /home/jpmartinez/rg_novo/synthesis_output/nbid

PY_VENV_PATH = ${PWD}/.venv
PY_VERSION = ${PY_VENV_PATH}/bin/python --version
PY_EXEC = ${PY_VENV_PATH}/bin/python -u

export PYTHONPATH := ${PYTHONPATH}:${PWD}/src/:${PWD}/utils/
export PYTHONPATH := ${PYTHONPATH}:${PWD}/lib/multiprocessing_lib/src/

DEBUG_NUM_SAMPLES := 4


check_data_source_%: synthesis_input/%/entities.json
	[ -d ${IMAGES_SOURCE_ROOT_PATH}/$* ]

*_front: check_data_source_front
*_back: check_data_source_back

cp_data_% : check_data_source_%
	mkdir -p syntehesis_input/$*
	rm -f syntehesis_input/$*/input syntehesis_input/$*/*.via.csv
	ln -s ${IMAGES_SOURCE_ROOT_PATH}/$* syntehesis_input/$*/input
	cp ${ANNOTATIONS_ROOT_PATH}/output/$*/*.via.csv syntehesis_input/$*

prep_labels_%: cp_data syntehesis_input/%/entities.via.csv syntehesis_input/%/sample.via.csv
	mkdir -p syntehesis_input/$*/labels
	find syntehesis_input/$*/labels -type f | xargs -I@ rm @
	${PY_EXEC} utils/data_formatters/splitter.py $*

anonimize_run_%: src/anonimize_input.py
	${PY_EXEC} src/anonimize_input.py --sample-label $*
anonimize_debug_%: src/anonimize_input.py
	SINGLE_THREAD=yes DEBUGGING=yes ${PY_EXEC} src/anonimize_input.py --max-num-samples ${DEBUG_NUM_SAMPLES} --sample-label $*
anonimize_clean_%:
	rm -rf synthesis_output/$*/anom synthesis_output/$*/warped
	find syntehesis_input/$*/labels/ -name *.bg.json | xargs -I@ rm @
anonimize: anonimize_run_front anonimize_run_back
anonimize_debug: anonimize_debug_front anonimize_debug_back

synth_run_%: src/synthesize_bgs.py
	${PY_EXEC} src/synthesize_bgs.py --sample-label $*
synth_debug_%: src/synthesize_bgs.py
	SINGLE_THREAD=yes DEBUGGING=yes ${PY_EXEC} src/synthesize_bgs.py --sample-label --max-num-samples ${DEBUG_NUM_SAMPLES} $*
synth_clean_%:
	rm -rf synthesis_output/$*/mask synthesis_output/$*/reboot
synth: synth_run_front synth_run_back
synth_debug: synth_debug_front synth_debug_back

partition_%: src/partition_dataset.py
	${PY_EXEC} src/partition_dataset.py cross reboot
	mkdir -p synthesis_output/$*/nbid/images synthesis_output/$*/nbid/boxes_and_transcripts
	mv train.csv valid.csv test.csv synthesis_output/$*/nbid/
	find synthesis_output/$*/reboot -type f -name "*.jpg" | grep -v "mask_GT" | xargs -I@ cp @ synthesis_output/$*/nbid/images/
	find synthesis_output/$*/reboot -type f -name "*.tsv" | xargs -I@ cp @ synthesis_output/$*/nbid/boxes_and_transcripts/
partition_clean_%:
	rm -rf synthesis_output/$*/nbid

debug_clean_%:
	rm -rf synthesis_output/$*/debug

clean_%: anonimize_clean_% debug_clean_% synth_clean_% partition_clean_%
	rm -f via.csv
clean: clean_front clean_back

run_all_% run_%: anonimize_run_% synth_run_% partition_%
run: run_front run_back

rerun_%: cp_data_% prep_labels_% run_%
rerun: rerun_front rerun_back

.PHONY: check_args check_data_source clean%
