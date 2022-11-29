python3 generic_img_generator.py

python3 spl.py ./reboot

python3 make_train_test cross reboot

mv train.csv valid.csv test.csv nbid/

mv reboot/!(*mask*).jpg nbid/images/

mv reboot/*.tsv nbid/boxes_and_transcripts/
