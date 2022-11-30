import math

import cv2 as cv
import doxapy as doxa
import numpy as np

from logging_cfg import logging


# Checa se os pixels estão dentro do intervalo para pegar os 3 mais próximos.
def check_pixels(borders, correction_window_size=3):
    return borders[0] - correction_window_size > 0


# Garante que os intervalos fiquem  do range da imagem.
def fill_black_area(
    min_x, min_y, max_x, max_y, correction_window_size, limit_x, limit_y
):
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


def create_sweep_area(x_inicial, y_inicial, x_final, y_final):
    """Implementa um gerador que representa a área retangular indicada pelos parâmetros.
    O gerador varre o retângulo priorizando o eixo apontado pelos parâmetros `x_inicial` e `x_final`.

    Parameters
    ----------
    x_inicial : int
    y_inicial : int
    x_final : int
    y_final : int

    Yields
    ------
    Tuple[int, int]
        Coordenada 2D dentro da área retangular
    """
    for y_var in range(y_inicial, y_final):
        for x_var in range(x_inicial, x_final):
            yield y_var, x_var


def correct_color_v(img, coord, correction_window_size):
    if all(
        (
            coord[0] > correction_window_size,
            coord[1] < img.shape[1],
            coord[0] < img.shape[0],
        )
    ):
        window = np.array(
            [img[(coord[0] - i)][coord[1]] for i in range(correction_window_size)]
        )
        mean_pixel = np.median(window)
        img[coord[0]][coord[1]] = mean_pixel


def correct_color_h(img, coord, correction_window_size):
    if all(
        (
            coord[1] > correction_window_size,
            coord[1] < img.shape[1],
            coord[0] < img.shape[0],
        )
    ):
        window = np.array(
            [img[coord[0]][coord[1] - i] for i in range(correction_window_size)]
        )
        mean_pixel = np.median(window)
        img[coord[0]][coord[1]] = mean_pixel


def erase_text(img, area, num_iters=5, correction_window_size=5):
    monos = cv.split(img)
    area_v, area_h = area
    for _ in range(num_iters):
        # vertical
        for coord in area_v:
            if check_pixels(coord):
                for c in range(3):
                    correct_color_v(
                        monos[c], coord, correction_window_size=correction_window_size
                    )
        # then horizontal
        for coord in area_h:
            if check_pixels(coord):
                for c in range(3):
                    correct_color_h(
                        monos[c], coord, correction_window_size=correction_window_size
                    )
    return cv.merge(monos)


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


def get_sensitive_roi_rectangles(regions):
    if regions is not None:
        for aux in range(len(regions)):
            if regions[aux]["region_attributes"]["info_type"] == "p":
                if regions[aux]["region_shape_attributes"]["name"] == "rect":
                    rect_x = regions[aux]["region_shape_attributes"]["x"]
                    rect_x_final = (
                        rect_x + regions[aux]["region_shape_attributes"]["width"]
                    )
                    rect_y = regions[aux]["region_shape_attributes"]["y"]
                    rect_y_final = (
                        rect_y + regions[aux]["region_shape_attributes"]["height"]
                    )
                else:
                    all_points_x = regions[aux]["region_shape_attributes"][
                        "all_points_x"
                    ]
                    all_points_y = regions[aux]["region_shape_attributes"][
                        "all_points_y"
                    ]
                    rect_x = min(all_points_x)
                    rect_y = min(all_points_y)
                    rect_y_final = max(all_points_y)
                    rect_x_final = max(all_points_x)
                yield tuple(map(int, (rect_x, rect_y, rect_x_final, rect_y_final)))


# Gera as imagens do background.
def back_gen(img, img_spath, arq, angle):
    rects = list(get_sensitive_roi_rectangles(arq))

    # computes inpaint mask
    inpaint_mask = np.zeros((img.shape[0], img.shape[1], 1), like=img, dtype=np.uint8)
    for rect_x, rect_y, rect_x_final, rect_y_final in rects:
        roi = img[rect_y:rect_y_final, rect_x:rect_x_final]
        roi_bin = cv.cvtColor(roi, cv.COLOR_RGB2GRAY)
        doxa.Binarization.update_to_binary(doxa.Binarization.Algorithms.NICK, roi_bin)
        roi_bin = cv.bitwise_not(roi_bin)

        roi = np.array(roi_bin, dtype=np.uint8)
        roi = cv.blur(roi, (7, 3))
        roi = np.atleast_3d(roi)

        inpaint_mask[rect_y:rect_y_final, rect_x:rect_x_final] = roi

    # defines erasing functions
    def inpaint(img_arg):
        for rect_x, rect_y, rect_x_final, rect_y_final in rects:
            inp_radius = max(2, (rect_y_final - rect_y) // 8)  # that's an heuristic
            # computational cost of cv.inpaint is proportional (maybe quadratic) to inpaintRadius
            img_arg = cv.inpaint(
                img_arg, inpaint_mask, flags=cv.INPAINT_TELEA, inpaintRadius=inp_radius
            )
        return img_arg

    def sweep_erase(img_arg):
        # TODO: try areas on character segmentation rather than full bbox
        for rect_x, rect_y, rect_x_final, rect_y_final in rects:
            width = rect_x_final - rect_x
            min_area_x = 20
            num_areas_x = math.floor(width / min_area_x)
            dx = (rect_x_final - rect_x) / num_areas_x
            for idx in range(num_areas_x):
                rect_x_i = int(rect_x + dx * idx)
                rect_x_final_i = int(rect_x_i + dx)

                area_text_v = create_sweep_area(
                    rect_x_i, rect_y, rect_x_final_i, rect_y_final
                )
                area_text_h = map(
                    lambda coord: (coord[1], coord[0]),
                    create_sweep_area(rect_y, rect_x_i, rect_y_final, rect_x_final_i),
                )
                img_arg = erase_text(img_arg, (area_text_v, area_text_h))
        return img_arg

    # erasing process
    logging.debug("Aplicando inpaint")
    img = inpaint(img)

    # saves and returns
    bg_outpath = img_spath.background_fpath().as_posix()
    cv.imwrite(bg_outpath, img)
    logging.info(f"Imagem anonimizada salva em {bg_outpath}")
