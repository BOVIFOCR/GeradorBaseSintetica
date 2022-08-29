PREANNOT_SRC_PATH=/home/jpsmartinez/codes/unico/snippets/preannot-rg/
SIDE=front

REMOTE_HOST=ufpr-duo
REMOTE_URL=/home/jpmartinez/rg_novo/nbid/


export PYTHONPATH := ${PYTHONPATH}:${PWD}/src/:${PWD}/lib/multiprocessing_lib/src/


cp_data:
	rm via.csv input -rf ;\
    cp $(PREANNOT_SRC_PATH)/output/$(SIDE)/via.csv . ;\
    cp -r $(PREANNOT_SRC_PATH)/output/$(SIDE)/warped input

reset:
	cp_data &&\
    rm -rf back tile crop mask reboot


prep_labels:
	rm synthesis_output/labels/* ;\
    .venv/bin/python utils/splitter.py via.csv

anonimize: src/anonimize_input.py
	echo $(PYTHONPATH)
	.venv/bin/python -u src/anonimize_input.py

synth: src/synthesize_bgs.py
	.venv/bin/python -u src/synthesize_bgs.py


upload:
	rsync -avzh synthesis_output/reboot \
		output/
		$(REMOTE_HOST):$(REMOTE_URL)
	ssh $(REMOTE_HOST) "echo 'feitoo' > $(REMOTE_URL)/.upload_status


run: anonimize synth
rerun: reset prep_labels run
