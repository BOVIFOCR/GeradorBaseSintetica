#!/usr/bin/python
# -*- coding: latin-1 -*-

import json
import os
import traceback as tcb

import cv2
from doc_ock.mp_lock import mp_lock
import torch

import background_generator
from gan_model.models import CompletionNetwork
from find_face import erase_face

from annotation_utils import load_annotations
from logging_cfg import logging
import paths

MAX_WIDTH = 1920
MAX_NUM_PROCS = 16

gan = CompletionNetwork()
gan.load_state_dict(torch.load('./src/gan_model/model_cn', map_location='cpu'))

with open('./src/gan_model/config.json', 'r') as f:
    config = json.load(f)
mpv = torch.tensor(config['mpv']).view(3, 1, 1)


def resize_image(img, max_width=MAX_WIDTH):
    width = int(img.shape[1])
    height = int(img.shape[0])

    if width > max_width:
        scale = max_width / width
        new_dim = tuple(map(int, (width * scale, height * scale)))
        new_img = cv2.resize(img, new_dim, interpolation=cv2.INTER_AREA)
    else:
        scale = 1.0
        new_img = img

    return new_img, scale


def process_main(img_spath):
    labels_fpath = img_spath.labels_fpath()

    try:
        logging.info(f"Processing {img_spath}")

        img = cv2.imread(str(img_spath))
        # Ajusta o DPI e orientação da imagem e salva o resultado em `paths.path_rot`
        img, resize_scale = resize_image(img)

        # Detecta e apaga a face
        img = erase_face(img)

        # Carrega e ajusta anotações
        json_arq = load_annotations(labels_fpath, resize_scale=resize_scale)
        with open(
            str(labels_fpath).replace(".json", ".bg.json"), mode="w", encoding="utf-8"
        ) as json_fp:
            json.dump(json_arq, json_fp)

        # Anonimiza os dados e salva o resultadao em `paths.path_back`
        background_generator.back_gen(img, img_spath, json_arq, gan=gan, mpv=mpv)

    except Exception:
        logging.error(f"Erro gerando a imagem {img_spath}:\n{tcb.format_exc()}")
        exit(-1)


def main():
    input_list = list(paths.list_input_images(for_anon=True))
    num_input_items = len(input_list)
    logging.info(f"Finished loading {num_input_items} images for anonimization")

    if os.environ.get("SINGLE_THREAD"):
        logging.info("Iniciando processamento serial.")
        [process_main(img_spath) for img_spath in input_list]
    else:
        n = min(MAX_NUM_PROCS, len(input_list))
        logging.info(f"Iniciando processamento paralelo em {n} threads.")
        mp_lock(
            input_list, process_main, save_callback=None,
            num_procs=n, out_path=(paths.path_mpout / "anonimize_input").as_posix(),
        )


if __name__ == "__main__":
    main()
