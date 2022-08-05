# Arquivo main do projeto.
import cv2
import glob
import json
import os
import random
import traceback as tcb

import background_generator
from find_face import erase_face
import text_2_image

import paths


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


def list_input_images():
    fnames = os.listdir(paths.path_entrada)
    print(f'Found {len(fnames) = } in input directory')
    random.shuffle(fnames)
    for file_img in fnames:
        labels_file = paths.json_path + file_img.split('.')[0] + '.json'

        valid_fname_extension = file_img.endswith('.jpg') or file_img.endswith('.JPG') or \
            file_img.endswith('.jpeg') or file_img.endswith('.png')
        labels_file_exists = os.path.isfile(labels_file)
        back_file_exists = os.path.isfile(f'{paths.path_back}/{file_img}')
        if not back_file_exists and labels_file_exists and valid_fname_extension:
            yield str(file_img)


def load_annotations(labels_fpath, resize_scale=1.):
    with open(labels_fpath, encoding='utf-8') as json_file:
        json_arq = json.load(json_file)
    for idx in range(len(json_arq)):
        json_arq[idx]['region_shape_attributes']['all_points_x'] = list(map(
            lambda c: int(c * resize_scale),
            json_arq[idx]['region_shape_attributes']['all_points_x']))
        json_arq[idx]['region_shape_attributes']['all_points_y'] = list(map(
            lambda c: int(c * resize_scale),
            json_arq[idx]['region_shape_attributes']['all_points_y']))
    return json_arq


def main():
    for img_name in list_input_images():
        img_fpath = f'{paths.path_entrada}/{img_name}'
        labels_fpath = f"{paths.json_path}/{img_name.split('.')[0] + '.json'}"

        img = cv2.imread(img_fpath)
        # if (img.shape[1] < 1920):
        #     continue
        try:
            print(f'Processando: {img_fpath}')
            img = cv2.imread(f'{paths.path_entrada}/{img_name}')

            # Ajusta o DPI e orientação da imagem e salva o resultado em `paths.path_rot`
            print('Ajustando orientação e resolução da imagem')
            img, resize_scale = resize_image(img)

            # Detecta e apaga a face
            print('Apagando face')
            img = erase_face(img)

            # Carrega e ajusta anotações
            json_arq = load_annotations(labels_fpath, resize_scale=resize_scale)
            new_labels_fpath = f"{paths.json_path}/{img_name.split('.')[0]}-resized.json'"
            with open(new_labels_fpath, mode='w', encoding='utf-8') as json_fp:
                json_arq = json.dump(json_arq, json_fp)
            json_arq = load_annotations(new_labels_fpath)

            # Anonimiza os dados e salva o resultadao em `paths.path_back`
            background_generator.back_gen(img, img_name, json_arq, tipo_doc='RG', angle=0)
            print('Background gerado!')

        except Exception as e:
            print(f'Erro gerando a imagem {img_fpath}:\n{tcb.format_exc()}')
            exit(-1)



if __name__ == '__main__':
    main()
