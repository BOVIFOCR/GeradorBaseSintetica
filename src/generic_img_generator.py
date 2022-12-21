#!/usr/bin/python
# -*- coding: latin-1 -*-

# Arquivo main do projeto.
import cv2
import itertools
import json
import torch

import background_generator
from gan_model.models import CompletionNetwork
from find_face import erase_face, FaceDetectionError
from logging_cfg import logging
import paths
import text_2_image


use_gan = True
saved_model = './src/gan_model/model_cn'
gan_config = './src/gan_model/config.json'

path_entrada = './synthesis_input/input/'
json_path = './synthesis_input/labels/'

synth_repeat = 3


def main():
    gan = CompletionNetwork()
    gan.load_state_dict(torch.load(saved_model, map_location='cpu'))

    with open(gan_config, 'r') as f:
        config = json.load(f)
    mpv = torch.tensor(config['mpv']).view(3, 1, 1)

    # for img_spath in list(paths.list_input_images(for_anon=True)):
    for img_spath in itertools.chain(
        paths.list_input_images(for_anon=True)
        # (paths.SamplePath(p) for p in (
        #     "synthesis_input/input/6bf05161-99a8-4200-b98c-dabab0bd5e04.jpg",
        #     "synthesis_input/input/5ba95c7f-cff1-4efb-90ad-a34646dee2ba.jpg",
        #     "synthesis_input/input/1bc288dc-718c-4c81-9365-48377215880f.jpg",
        #     "synthesis_input/input/590697a6-ccfb-4cef-8515-c7cc2919556c.jpg"
        # )),
    ):

        with open(img_spath.labels_fpath(), 'r', encoding='utf-8') as json_file:
            json_arq = json.load(json_file)

        img = cv2.imread(str(img_spath))
        logging.info('Processando: ' + str(img_spath))

        try:
            img = erase_face(img)
        except FaceDetectionError as e:
            logging.warning(f"Skipping image {str(img_spath)} because of {e}")
            continue

        background_generator.back_gen(img, img_spath, json_arq, gan=gan, mpv=mpv)

        for i in range(synth_repeat):
            text_2_image.control_mask_gen(json_arq, img_spath.sample_id())


if __name__ == '__main__':
    import pdb

    try:
        main()
        exit(0)
    except pdb.Restart:
        import importlib
        import generic_img_generator
        importlib.reload(generic_img_generator)
        pdb.run('generic_img_generator.main()')
