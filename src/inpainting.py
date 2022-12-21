import math

import cv2
import doxapy as doxa
import numpy as np
import torch

from gan_model.utils import poisson_blend
from torchvision import transforms


def check_pixels(borders, correction_window_size=3):
    """Checa se os pixels estão dentro do intervalo para pegar os 3 mais próximos."""
    return borders[0] - correction_window_size > 0


# Area creation
def create_rect_area(x_inicial, y_inicial, x_final, y_final):
    area = []
    x_var = x_inicial
    y_var = y_inicial

    while y_var < y_final:
        while x_var < x_final:
            area.append([y_var, x_var])
            x_var = x_var + 1
        x_var = x_inicial
        y_var = y_var + 1

    return area


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


def fill_black_area(
    min_x, min_y, max_x, max_y, correction_window_size, limit_x, limit_y
):
    """Garante que os intervalos fiquem  do range da imagem."""
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


# Mask creation
def get_inpainting_masks(img, rects):
    """Computes coarser and finer inpaint masks"""
    inpaint_mask = np.zeros((img.shape[0], img.shape[1], 1), like=img, dtype=np.uint8)
    inpaint_mask_coarse = np.zeros((img.shape[0], img.shape[1], 1), like=img, dtype=np.uint8)
    binarization_method = doxa.Binarization.Algorithms.ISAUVOLA
    for rect_x, rect_y, rect_x_final, rect_y_final in rects:
        inpaint_mask_coarse[rect_y:rect_y_final, rect_x:rect_x_final] = 255

        # ROI binarization via doxapy
        roi = cv2.cvtColor(img[rect_y:rect_y_final, rect_x:rect_x_final], cv2.COLOR_RGB2GRAY)
        doxa.Binarization.update_to_binary(binarization_method, roi, parameters={'k': 0.05})
        roi = np.array(cv2.bitwise_not(roi), dtype=np.uint8)

        # blur + dilate iterations (otherwise, character borders are not covered)
        blur_shape = (3, 3)
        dilation_shape = cv2.MORPH_ELLIPSE
        dilatation_size = 2
        blur_dilate_iters = 3
        for _ in range(blur_dilate_iters):
            roi = cv2.blur(roi, blur_shape)
            roi = cv2.dilate(
                roi, cv2.getStructuringElement(
                    dilation_shape,
                    (2 * dilatation_size + 1, 2 * dilatation_size + 1), (dilatation_size, dilatation_size)))

        inpaint_mask[rect_y:rect_y_final, rect_x:rect_x_final] = np.atleast_3d(roi)
    return inpaint_mask, inpaint_mask_coarse


# Color correction
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


def correct_color(img, tp, dom_color, tipo_doc):
    """Cobre os pixels listados dentro da área de texto."""
    if check_pixels(tp):
        window = np.array([img[tp[0] - 3, tp[1]], img[tp[0] - 2, tp[1]], img[tp[0] - 1, tp[1]]])
        mean_pixel = np.mean(window)

        if tipo_doc == 'CPF':
            img[tp[0]][tp[1]] = mean_pixel

        else:
            if mean_pixel > dom_color:
                img[tp[0]][tp[1]] = mean_pixel
            else:
                img[tp[0]][tp[1]] = dom_color


# Sweep erase
def erase_text_orthogonally(img, area, num_iters=5, correction_window_size=5):
    monos = cv2.split(img)
    area_v, area_h = area
    for _ in range(num_iters):
        # vertical
        for coord in area_v:
            if check_pixels(coord):
                for c in range(3):
                    correct_color_v(monos[c], coord, correction_window_size=correction_window_size)
        # horizontal
        for coord in area_h:
            if check_pixels(coord):
                for c in range(3):
                    correct_color_h(monos[c], coord, correction_window_size=correction_window_size)
    return cv2.merge(monos)


# Inpaint techniques
## Orthogonal Sweep
def inpaint_sweep(img, rects):
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
            img = erase_text_orthogonally(img, (area_text_v, area_text_h))
    return img


## Classic / Telea
def inpaint_telea(img, inpaint_mask, inpaintRadius=3):
    """Applies Telea's inpainting method (TODO: link OpenCV doc.)

    Computational cost of cv2.inpaint is proportional (maybe quadratic) to inpaintRadius.
    """
    return cv2.inpaint(
        img, inpaint_mask,
        flags=cv2.INPAINT_TELEA, inpaintRadius=inpaintRadius)


## GAN
def inpaint_gan(img, mask, model, mpv):
    x = torch.unsqueeze(transforms.ToTensor()(img), 0)
    mask = torch.unsqueeze(transforms.ToTensor()(mask), 0)
    x_mask = x - x * mask + mpv * mask

    input = torch.cat((x_mask, mask), dim=1)
    output = model(input)
    inpainted = poisson_blend(x_mask, output, mask)

    ret = inpainted.squeeze()
    ret = ret.mul(255).add_(0.5).clamp_(0, 255).permute(1, 2, 0).to("cpu", torch.uint8).numpy()
    return ret
