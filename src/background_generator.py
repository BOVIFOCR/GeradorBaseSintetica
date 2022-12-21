#!/usr/bin/python
# -*- coding: latin-1 -*-

import numpy as np
import cv2

import paths

from logging_cfg import logging

from inpainting import (
    get_sensitive_roi_rectangles, get_inpainting_masks,
    inpaint_sweep, inpaint_telea, inpaint_gan)


def overlay_mask(img, mask, color):
    bg = np.zeros_like(img)
    for i, c in enumerate(color):
        bg[:, :, i] = c
    # TODO: do not darken out-of-mask pixels
    return cv2.addWeighted(img, .8, cv2.bitwise_and(bg, cv2.cvtColor(mask, cv2.COLOR_GRAY2RGB)), .2, 0)


# Gera as imagens do background.
def back_gen(img, img_spath, arq, gan, mpv):
    rects = list(get_sensitive_roi_rectangles(arq))

    # erasing process
    img_id = img_spath.sample_id()
    logging.debug("Aplicando inpaint")

    inpaint_mask_fine, inpaint_mask_coarse = get_inpainting_masks(img, rects)

    # DEV: draw boxes for debugging
    debug_dirpath = paths.path_output_base / 'debug' / img_id
    debug_dirpath.mkdir(exist_ok=True, parents=True)

    # cv2.imwrite(str(debug_dirpath / "mask-fine.jpg"), inpaint_mask_fine)
    # cv2.imwrite(str(debug_dirpath / "mask-coarse.jpg"), inpaint_mask_coarse)

    # inp_with_overlay = overlay_mask(
    #     overlay_mask(img, inpaint_mask_fine, color=(0, 0, 255)),
    #     inpaint_mask_coarse, color=(122, 122, 0))
    # cv2.imwrite(str(debug_dirpath / "overlay.jpg"), inp_with_overlay)

    img_gan_fine = inpaint_gan(img, inpaint_mask_fine, gan, mpv)
    # cv2.imwrite(str(debug_dirpath / "gan-fine.jpg"), img_gan_fine)
    img_gan_coarse = inpaint_gan(img, inpaint_mask_coarse, gan, mpv)
    # cv2.imwrite(str(debug_dirpath / "gan-coarse.jpg"), img_gan_coarse)

    img_sweep = inpaint_sweep(img, rects)
    # cv2.imwrite(str(debug_dirpath / "sweep.jpg"), img_sweep)

    img_classic_fine = inpaint_telea(img, inpaint_mask_fine)
    cv2.imwrite(str(debug_dirpath / "classic-fine.jpg"), img_classic_fine)
    # img_classic_coarse = inpaint_telea(img, inpaint_mask_coarse)
    # cv2.imwrite(str(debug_dirpath / "classic-coarse.jpg"), img_classic_coarse)

    # prepares debug images for plots
    debug_shape = [3000]
    debug_shape.append(int((debug_shape[0] / img.shape[1]) * img.shape[0]))
    debug_shape = tuple(debug_shape)
    font_type = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 6
    font_color = (0, 0, 0)
    font_thickness = 15
    (font_width, font_height), font_base = cv2.getTextSize("==", font_type, font_scale, font_thickness)
    font_anchor = (font_width, font_height + font_base)

    img_sweep_plot = cv2.putText(
        cv2.resize(img_sweep, debug_shape), "BID (orth. + reduced prop.)", font_anchor,
        font_type, font_scale, font_color, font_thickness)

    # img_classic_coarse_plot = cv2.putText(
    #     img_classic_coarse, "Telea with coarse mask", font_anchor,
    #     font_type, font_scale, font_color, font_thickness)
    img_classic_fine_plot = cv2.putText(
        cv2.resize(img_classic_fine, debug_shape), "Telea (fine)", font_anchor,
        font_type, font_scale, font_color, font_thickness)

    img_gan_coarse_plot, img_gan_fine_plot = tuple(map(
        lambda ima: cv2.resize(ima, debug_shape),
        (img_gan_coarse, img_gan_fine)))
    img_gan_coarse_plot = cv2.putText(
        img_gan_coarse_plot, "GAN (coarse)", font_anchor,
        font_type, font_scale, font_color, font_thickness)
    img_gan_fine_plot = cv2.putText(
        img_gan_fine_plot, "GAN (fine)", font_anchor,
        font_type, font_scale, font_color, font_thickness)

    # img_debug = cv2.vconcat([
    #     cv2.hconcat([img, cv2.cvtColor(inpaint_mask_fine, cv2.COLOR_GRAY2RGB), inp_with_overlay, img_sweep_plot]),
    #     cv2.hconcat([
    #         img_classic_coarse_plot, img_classic_fine_plot,
    #         img_gan_coarse_plot, img_gan_fine_plot])
    # ])
    # cv2.imwrite(str(debug_dirpath / "gridplot.jpg"), img_debug)

    # TODO: safe gridplot (no sensitive data)
    safe_img_debug = cv2.vconcat([
        cv2.hconcat([img_sweep_plot, img_classic_fine_plot]),
        cv2.hconcat([img_gan_coarse_plot, img_gan_fine_plot])
    ])
    cv2.imwrite(str(debug_dirpath / "safegridplot.jpg"), safe_img_debug)

    img_output = img_gan_fine

    # saves and returns
    bg_outpath = img_spath.background_fpath().as_posix()
    cv2.imwrite(bg_outpath, img_output)
    logging.info(f"Imagem anonimizada salva em {bg_outpath}")
