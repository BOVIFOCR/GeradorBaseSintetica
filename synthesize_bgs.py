# Arquivo main do projeto.
import os
import traceback as tcb

import cv2

import text_2_image

import paths

from anonimize_input import load_annotations


def main():
    repetir = 12

    fnames = os.listdir(paths.path_back)
    for img_name in fnames:
        labels_fpath = f"{paths.json_path}/{img_name.split('.')[0]}-resized.json'"
        try:
            json_arq = load_annotations(labels_fpath)

            for _ in range(repetir):
                text_2_image.control_mask_gen(
                    tipo_doc='RG',
                    json_arq=json_arq,
                    img_name=img_name,
                    angle=0)
        except Exception:
            print(f'Erro gerando a imagem {img_name}:\n{tcb.format_exc()}')
            exit(-1)
if __name__ == '__main__':
    main()
