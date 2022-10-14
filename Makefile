PREANNOT_SRC_PATH=/home/jpsmartinez/codes/unico/snippets/preannot-rg/
SIDE=front

REMOTE_HOST=ufpr-duo
REMOTE_URL=/home/jpmartinez/rg_novo/nbid/


export PYTHONPATH := ${PYTHONPATH}:${PWD}/src/
export PYTHONPATH := ${PYTHONPATH}:${PWD}/lib/multiprocessing_lib/src/
export PYTHONPATH := ${PYTHONPATH}:${PWD}/utils/


cp_data:
	rm via.csv input -rf ;\
	cp $(PREANNOT_SRC_PATH)/output/$(SIDE)/via.csv . ;\
	cp -r $(PREANNOT_SRC_PATH)/output/$(SIDE)/warped input

prep_labels:
	rm synthesis_input/labels/* ;\
	.venv/bin/python utils/data_formatters/splitter.py via.csv


anonimize: src/anonimize_input.py
	.venv/bin/python -u src/anonimize_input.py

clean_anonimize:
	rm -rf synthesis_output/back

synth: src/synthesize_bgs.py
	.venv/bin/python -u src/synthesize_bgs.py

clean_synth:
	rm -rf synthesis_output/mask synthesis_output/reboot


upload:
	rsync -avzh synthesis_output/reboot \
		output/
		$(REMOTE_HOST):$(REMOTE_URL)
	ssh $(REMOTE_HOST) "echo 'feitoo' > $(REMOTE_URL)/.upload_status


clean_all: clean_anonimize clean_synth

run: anonimize synth
rerun: reset prep_labels run
