# Arquivo main do projeto.
import argparse
import traceback as tcb

from doc_ock.mp_lock import mp_lock

import paths
import text_2_image

from annotation_utils import load_annotations
from logging_cfg import logging

parser = argparse.ArgumentParser()
parser.add_argument("--num-iters", default=1)
args = parser.parse_args()


def process_main(input_fpath):
    img_id = input_fpath.sample_id()
    anon_labels_fpath = input_fpath.labels_fpath()
    json_arq = load_annotations(str(anon_labels_fpath).replace(".json", ".bg.json"))
    try:
        for it_idx in range(args.num_iters):
            text_2_image.control_mask_gen(json_arq=json_arq, img_id=img_id)
    except Exception:
        logging.error(
            f"Erro na iteração de síntese {it_idx}",
            f"da imagem {img_id} a partir de ",
            f"anotações em {anon_labels_fpath}.",
        )
        logging.error(f"Traceback capturado:\n{tcb.format_exc()}")
        exit(-1)


fnames = list(paths.list_input_images())
mp_lock(
    fnames, process_main, save_callback=None, num_procs=16,
    out_path=(paths.path_mpout / "synthesize_bgs").as_posix()
)
