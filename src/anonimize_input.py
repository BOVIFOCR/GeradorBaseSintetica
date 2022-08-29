# Arquivo main do projeto.
import cv2
import glob
import json
from pathlib import Path

import os

import traceback as tcb

import background_generator
from find_face import erase_face
import text_2_image

import paths
from paths import SamplePath

from doc_ock.mp_lock import mp_lock


def resize_image(img, max_width=1920):  # sourcery skip: move-assign
    width = int(img.shape[1])
    height = int(img.shape[0])

    if width > max_width:
        scale = max_width / width
        new_dim = tuple(map(int, (width * scale, height * scale)))

        new_img = cv2.resize(
            img, new_dim,
            interpolation=cv2.INTER_AREA
        )
    else:
        scale = 1.
        new_img = img

    return new_img, scale


def load_annotations(labels_fpath, resize_scale=1.):
    with open(labels_fpath, encoding='utf-8') as json_file:
        json_arq = json.load(json_file)
    for idx in range(len(json_arq)):
        json_arq[idx]['region_shape_attributes']['all_points_x'] = list(map(
            lambda c: c * resize_scale,
            json_arq[idx]['region_shape_attributes']['all_points_x']))
        json_arq[idx]['region_shape_attributes']['all_points_y'] = list(map(
            lambda c: c * resize_scale,
            json_arq[idx]['region_shape_attributes']['all_points_y']))
    return json_arq


def process_main(img_spath):
    labels_fpath = img_spath.labels_fpath()

    try:
        print(f'Processando: {img_spath}')
        img = cv2.imread(str(img_spath))

        # Ajusta o DPI e orientação da imagem e salva o resultado em `paths.path_rot`
        print('Ajustando orientação e resolução da imagem')
        print(img.shape)
        img, resize_scale = resize_image(img)
        print(img.shape)
        print(resize_scale)

        # Detecta e apaga a face
        print('Apagando face')
        img = erase_face(img)

        # Carrega e ajusta anotações
        print('Ajustando anotações')
        json_arq = load_annotations(labels_fpath, resize_scale=resize_scale)
        with open(str(labels_fpath).replace('.json', '.bg.json'), mode='w', encoding='utf-8') as json_fp:
            json.dump(json_arq, json_fp)

        # Anonimiza os dados e salva o resultadao em `paths.path_back`
        background_generator.back_gen(img, img_spath, json_arq, tipo_doc='RG', angle=0)
        print('Background gerado!')

    except Exception as e:
        print(f'Erro gerando a imagem {img_spath}:\n{tcb.format_exc()}')
        exit(-1)


def main():
    input_list = list(paths.list_input_images(for_anon=True))
    input_list = [SamplePath('synthesis_input/input/1bc288dc-718c-4c81-9365-48377215880f.jpg')]
    print(f'Loaded {len(input_list)} for anonimization.')

    mp_lock(
        input_list, process_main, save_callback=None, num_procs=16, out_path='mplock_out')

if __name__ == '__main__':
    main()
