import json
import os
import traceback as tcb

import cv2
from doc_ock.mp_lock import mp_lock

import background_generator
import paths
from find_face import erase_face

from annotation_utils import load_annotations
from logging_cfg import logging

MAX_WIDTH = 1920
MAX_NUM_PROCS = 16


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
        logging.info(f"Processando {img_spath}")
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
        background_generator.back_gen(img, img_spath, json_arq, angle=0)

    except Exception:
        logging.error(f"Erro gerando a imagem {img_spath}:\n{tcb.format_exc()}")
        exit(-1)


def main():
    env = dict(os.environ)

    input_list = list(paths.list_input_images(for_anon=True))
    if env.get("DEBUGGING"):
        input_list = [
            paths.SamplePath("synthesis_input/input/1bc288dc-718c-4c81-9365-48377215880f.jpg")
        ]
    logging.info(f"Foram carregadas {len(input_list)} imagens para anonimização.")

    if env.get("SINGLE_THREAD"):
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
