# Arquivo que faz o data augmentation da imagem gerada.
import itertools
from PIL import Image, ImageEnhance
import numpy as np
import cv2 as cv
import random
import paths
import os

import text_2_image


# json_original = 'via_export_json.json'
json_original = './new.json'

def rotate_bound(img_name):
    outpath = (paths.path_saida / img_name).as_posix()
    img = cv.imread(outpath)
    random.seed()
    angle = random.randint(0, 360)
    # grab the dimensions of the image and then determine the
    # center
    (h, w) = img.shape[:2]
    (cX, cY) = (w // 2, h // 2)
    # grab the rotation matrix (applying the negative of the
    # angle to rotate clockwise), then grab the sine and cosine
    # (i.e., the rotation components of the matrix)
    M = cv.getRotationMatrix2D((cX, cY), -angle, 1.0)
    cos = np.abs(M[0, 0])
    sin = np.abs(M[0, 1])
    # compute the new bounding dimensions of the image
    nW = int((h * sin) + (w * cos))
    nH = int((h * cos) + (w * sin))
    # adjust the rotation matrix to take into account translation
    M[0, 2] += (nW / 2) - cX
    M[1, 2] += (nH / 2) - cY
    # perform the actual rotation and return the image
    rotated = cv.warpAffine(img, M, (nW, nH))
    cv.imwrite(outpath, rotated)
    return rotated


def motion_blur(img):
    kernel_size = 3

    # Cria um kernel vertical.
    kernel_v = np.zeros((kernel_size, kernel_size))
    kernel_v[:, int((kernel_size - 1) / 2)] = np.ones(kernel_size)

    # Normaliza.
    kernel_v /= kernel_size

    return cv.filter2D(img, -1, kernel_v)


def rand_rotation(img_name, path_img):
    img = cv.imread(path_img + r'/' + img_name)
    random.seed()
    pos_angle = [0, 90, 180, 270]
    sel_num = random.randint(0, 3)
    angle = pos_angle[sel_num]

    v_blur = random.randint(0, 9)
    if v_blur >= 8:
        img = motion_blur(img)

    if angle == 90:
        rotated = cv.rotate(img, cv.ROTATE_90_CLOCKWISE)
    elif angle == 180:
        rotated = cv.rotate(img, cv.ROTATE_180)
    elif angle == 270:
        rotated = cv.rotate(img, cv.ROTATE_90_COUNTERCLOCKWISE)
    else:
        rotated = img

    cv.imwrite(os.path.join(path_img, img_name), rotated)
    return angle


def ctr_brg(img_name, file_idx, rep_idx, area_n_text, tipo_doc):
    random.seed()
    factor = round(random.uniform(0.5, 0.9), 2)
    contrast(img_name, file_idx, rep_idx, factor, area_n_text)

    random.seed()
    factor = round(random.uniform(0.5, 0.9), 2)
    brightness(img_name, file_idx, rep_idx, factor, area_n_text)

    random.seed()
    factor = 1 + round(random.uniform(0.1, 0.3), 2)
    contrast(img_name, file_idx, rep_idx, factor, area_n_text)

    if tipo_doc != 'RG':
        random.seed()
        factor = 1 + round(random.uniform(0.1, 0.3), 2)
        brightness(img_name, file_idx, rep_idx, factor, area_n_text)
