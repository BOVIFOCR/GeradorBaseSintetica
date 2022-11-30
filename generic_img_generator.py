#!/usr/bin/python
# -*- coding: latin-1 -*-

# Arquivo main do projeto.
import cv2 as cv
import json
import os
import torch

import background_generator
import rotate_images
import text_2_image
from find_face import erase_face
from gan_model.models import CompletionNetwork

import paths
path_base = '' #paths.path

use_gan = True
saved_model = './gan_model/model_cn_step90000'
gan_config = './gan_model/config.json'

# Path com a imagem.
# path_entrada = path_base + r'/original/BASE_UTIL/BETA'
path_entrada = './input/'

# Nome do json de saída do VIA ANNOTATOR com as informações de todas as imagens rotuladas.
# json_name = 'new.json'
json_path = './labels/'

def main():
    # Escolher o tipo de imagem que será gerada CNH, RG ou CPF, isso definirá a melhor fonte para a imagem criada.
    tipo_doc = 'RG'

    # Número de vezes que o processo irá se repetir para criar mais de uma imagem com informações diferentes a
    # partir de uma mesma imagem.
    repetir = 1
    # with open(path_entrada + r'/' + json_name, 'r', encoding='utf-8') \
    if use_gan == True:
        gan = CompletionNetwork()
        gan.load_state_dict(torch.load(saved_model, map_location='cpu'))

        with open(gan_config, 'r') as f:
            config = json.load(f)
        mpv = torch.tensor(config['mpv']).view(3, 1, 1)


    for idx, file_img in enumerate(os.listdir(path_entrada)):

        if file_img.endswith('.jpg') or file_img.endswith('.JPG') or file_img.endswith('.jpeg') \
                or file_img.endswith('.png'):

            with open(json_path + file_img.split('.')[0] + '.json', 'r', encoding='utf-8') \
                    as json_file:
                json_arq = json.load(json_file)

            img_name = str(file_img)

            img = cv.imread(path_entrada + r'/' + img_name)
            print('***************************')
            print('Processando: ' + img_name)

            print('***************************')
            print('Apagando face')
            # img = erase_face(img)

            angle_img, check_img = rotate_images.rotate_img(img, img_name)

            if check_img == 1:
                if use_gan:
                    background_generator.back_gen(img_name, json_arq, tipo_doc, angle=angle_img, gan=gan, mpv=mpv)

                # print('Background gerado!')
                # print('-----------------------------')

                for i in range(repetir):
                    text_2_image.control_mask_gen(tipo_doc, json_arq, img_name, str(idx), str(i), angle=angle_img)


if __name__ == '__main__':
    main()
