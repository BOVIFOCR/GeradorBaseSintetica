# Arquivo main do projeto.
import argparse
import os
from pathlib import Path
import traceback as tcb

import cv2

import text_2_image

import paths

from anonimize_input import load_annotations
from doc_ock.mp_lock import mp_lock
from paths import SamplePath


parser = argparse.ArgumentParser()
parser.add_argument('--num-iters', default=1)
args = parser.parse_args()


def process_main(input_fpath):
    img_id = input_fpath.sample_id()
    anon_labels_fpath = input_fpath.labels_fpath()
    json_arq = load_annotations(str(anon_labels_fpath).replace('.json', '.bg.json'))
    try:
        for it_idx in range(args.num_iters):
            text_2_image.control_mask_gen(
                tipo_doc='RG',
                json_arq=json_arq,
                img_id=img_id,
                angle=0)
    except Exception:
        print(
            f'Erro na iteração de síntese {it_idx}',
            f'da imagem {img_id} a partir de ',
            f'anotações em {anon_labels_fpath}.')
        print(f'Traceback capturado:\n{tcb.format_exc()}')

        exit(-1)


# fnames = list(paths.list_input_images())
fnames = [SamplePath('synthesis_input/input/1bc288dc-718c-4c81-9365-48377215880f.jpg')]
print(f'Loaded {len(fnames)} files for {args.num_iters} iterations each.')

mp_lock(
    fnames, process_main, save_callback=None, num_procs=16, out_path='mplock_out_synth')
