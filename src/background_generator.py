# Arquivo que apaga as informações pessoais das imagens.

from colorthief import ColorThief
import cv2 as cv
import math
import numpy as np
import os

import paths


# Checa se os pixels estão dentro do intervalo para pegar os 3 mais próximos.
def check_pixels(borders, correction_window_size=3):
    return borders[0] - correction_window_size > 0:


# Garante que os intervalos fiquem  do range da imagem.
def fill_black_area(min_x, min_y, max_x, max_y, correction_window_size, limit_x, limit_y):
    if max_x + correction_window_size >= limit_x:
        max_x = limit_x - 1
    else:
        max_x = max_x + correction_window_size
    if max_y + correction_window_size >= limit_y:
        max_y = limit_y - 1
    else:
        max_y = max_y + correction_window_size
    min_x = max(min_x - correction_window_size, 1)
    min_y = max(min_y - correction_window_size, 1)
    return [min_x, min_y, max_x, max_y]


# Cria uma área retangular na área do texto para apagá-lo.
def create_rect_area(x_inicial, y_inicial, x_final, y_final):
    for y_var in range(y_inicial, y_final):
        for x_var in range(x_inicial, x_final):
            yield y_var, x_var


# Cobre os pixels listados dentro da área de texto.
def correct_color_v(img, tp, tipo_doc, correction_window_size):
    if (tp[0] > correction_window_size) and (tp[1] < img.shape[1]) and (tp[0] < img.shape[0]):
        window = np.array([img[(tp[0]-i)][tp[1]] for i in range(correction_window_size)])
        mean_pixel = np.median(window)
        img[tp[0]][tp[1]] = mean_pixel


def correct_color_h(img, tp, tipo_doc, correction_window_size):
    if (tp[1] > correction_window_size) and (tp[1] < img.shape[1]) and (tp[0] < img.shape[0]):
        window = np.array([img[tp[0]][tp[1]-i] for i in range(correction_window_size)])
        mean_pixel = np.median(window)
        img[tp[0]][tp[1]] = mean_pixel


# Apaga o texto.
def erase_text(img, area, tipo_doc):
    monos = cv.split(img)
    for _ in range(5):
        # vertical
        for tp in area[0]:
            if check_pixels(tp):
                for c in range(3):
                    correct_color_v(monos[c], tp, tipo_doc)
        # then horizontal
        for tp in area[1]:
            tp = tp[1], tp[0]
            if check_pixels(tp):
                for c in range(3):
                    correct_color_h(monos[c], tp, tipo_doc)
    return cv.merge(monos)


# O elemento em mat[row][col] deve rodar com mat[col][11 - row - 1], mat[11 - row - 1][11 - col - 1],
# e mat[11 - col - 1][row].
def rotate_points(shape_x, shape_y, x_ini, y_ini, x_fin, y_fin, angle):
    if angle == 91:
        x_inicial = x_ini
        y_inicial = y_fin

        x_final = x_fin
        y_final = y_ini

        x_inicial_rot = shape_x - 1 - y_inicial
        y_inicial_rot = x_inicial

        x_final_rot = shape_x - 1 - y_final
        y_final_rot = x_final

    elif angle == 181:
        x_inicial = x_fin
        y_inicial = y_fin

        x_final = x_ini
        y_final = y_ini

        x_inicial_rot = shape_x - 1 - x_inicial
        y_inicial_rot = shape_y - 1 - y_inicial

        x_final_rot = shape_x - 1 - x_final
        y_final_rot = shape_y - 1 - y_final

    elif angle == 271:
        x_inicial = x_fin
        y_inicial = y_ini

        x_final = x_ini
        y_final = y_fin

        x_inicial_rot = y_inicial
        y_inicial_rot = shape_y - 1 - x_inicial

        x_final_rot = y_final
        y_final_rot = shape_y - 1 - x_final

    else:
        x_inicial_rot = x_ini
        y_inicial_rot = y_ini
        x_final_rot = x_fin
        y_final_rot = y_fin

    return x_inicial_rot, y_inicial_rot, x_final_rot, y_final_rot


def rotate_poly(shape_x, shape_y, point_x, point_y, angle):
    x_inicial = point_x
    y_inicial = point_y

    if angle == 91:
        x_inicial_rot = shape_x - 1 - y_inicial
        y_inicial_rot = x_inicial

    elif angle == 181:
        x_inicial_rot = shape_x - 1 - x_inicial
        y_inicial_rot = shape_y - 1 - y_inicial

    elif angle == 271:
        x_inicial_rot = y_inicial
        y_inicial_rot = shape_y - 1 - x_inicial

    else:
        x_inicial_rot = x_inicial
        y_inicial_rot = y_inicial

    return x_inicial_rot, y_inicial_rot


# Gera as imagens do background.
def back_gen(img, img_spath, arq, tipo_doc, angle):
    def get_crop_dom_color(crop_path, crop_img):
        cv.imwrite(crop_path, crop_img)
        color_thief = ColorThief(crop_path)
        palette = color_thief.get_palette(color_count=2)
        dominant_color = palette[1]
        os.remove(crop_path)

        return dominant_color


    bg_outpath = img_spath.background_fpath().as_posix()

    color_thief = ColorThief(img_spath.as_posix())
    palette = color_thief.get_palette(color_count=2)
    dominant_color = palette[1]

    shape_y = img.shape[1]
    shape_x = img.shape[1]

    color_ref_window = tuple(map(int, (.85 * shape_x, .21 * shape_y))), tuple(map(int, (.91 * shape_x, .51 * shape_y)))
    dominant_color = tuple(map(np.median, cv.split(img)))

    regions = arq
    if regions is not None:
        qtd_regions = len(regions)
        crop_name = f'crop-{img_spath.sample_id()}.jpg'
        crop_path = paths.path_crop / crop_name
        for aux in range(qtd_regions):
            if regions[aux]['region_attributes']['info_type'] == 'p':
                if regions[aux]['region_shape_attributes']['name'] == 'rect':
                    rect_x = regions[aux]['region_shape_attributes']['x']
                    rect_x_final = rect_x + regions[aux]['region_shape_attributes']['width']
                    rect_y = regions[aux]['region_shape_attributes']['y']
                    rect_y_final = rect_y + regions[aux]['region_shape_attributes']['height']
                    rect_x, rect_y, rect_x_final, rect_y_final = rotate_points(shape_x, shape_y, rect_x, rect_y, rect_x_final, rect_y_final, angle)
                else:
                    all_points_x = regions[aux]['region_shape_attributes']['all_points_x']
                    all_points_y = regions[aux]['region_shape_attributes']['all_points_y']
                    qtd_points = len(all_points_x)
                    points = [rotate_poly(shape_x, shape_y, all_points_x[i], all_points_y[i], angle) for i in range(qtd_points)]

                    # pts = np.asarray(points, dtype=int)
                    # pts = pts.reshape((-1, 1, 2))
                    # cv.polylines(img, pts, isClosed=True, color=(1, 1, 1))
                    # cv.fillPoly(img, [pts], (1, 1, 1))

                    min_x = min(all_points_x)
                    min_y = min(all_points_y)
                    max_y = max(all_points_y)
                    max_x = max(all_points_x)
                    rect_x, rect_y, rect_x_final, rect_y_final = tuple(map(int, rotate_points(shape_x, shape_y, min_x, min_y, max_x, max_y, angle)))
                # TODO: multiple text areas for grained filtering
                width = rect_x_final - rect_x
                min_area_x = 20
                num_areas_x = math.floor(width / min_area_x)
                for idx in range(num_areas_x):
                area_text = (
                    create_rect_area(rect_x, rect_y, rect_x_final, rect_y_final),
                    create_rect_area(rect_y, rect_x, rect_y_final, rect_x_final))
                img = erase_text(img, area_text, tipo_doc)
        cv.imwrite(bg_outpath, img)
        print(f'Wrote background at {bg_outpath}')
