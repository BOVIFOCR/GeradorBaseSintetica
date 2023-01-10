# -*- coding: latin-1 -*-

import argparse
import contextlib
import json
import math
import os
import time
import traceback as tcb
import typing
from bdb import BdbQuit
from itertools import islice

import cv2
import torch
import torch.multiprocessing as mp
from annotation_utils import load_annotations
from logging_cfg import logging

import inpainting
import paths
from find_face import NoFaceDetected, erase_face
from gan_model.models import CompletionNetwork

parser = argparse.ArgumentParser()
parser.add_argument(
    "--sample-label", default="front", type=str, choices=list(map(str,paths.SampleLabel.__members__.values()))
)
parser.add_argument("--max-num-samples", type=int, default=None)
parser.add_argument("--max-width", default=1920)
parser.add_argument("--num-max-procs", default=16)
parser.add_argument("--job-chunksize", default=5)
parser.add_argument("--keep-transcripts", action="store_true")
args = parser.parse_args()


def resize_image(img, max_width):
    width = int(img.shape[1])
    if width > max_width:
        scale = max_width / width

        height = int(img.shape[0])
        new_dim = tuple(map(int, (width * scale, height * scale)))
        img = cv2.resize(img, new_dim, interpolation=cv2.INTER_AREA)
    else:
        scale = 1.0

    return img, scale


def load_gan_model():
    gan = CompletionNetwork()
    gan.load_state_dict(torch.load("./src/gan_model/model_cn", map_location="cpu"))

    with open("./src/gan_model/config.json", "r") as f:
        config = json.load(f)
    mpv = torch.tensor(config["mpv"]).view(3, 1, 1)

    return gan, mpv


def chunk(sequence, chunksize):
    sequence = iter(sequence)
    sub_chunk = list(islice(sequence, chunksize))
    while sub_chunk:
        yield sub_chunk
        sub_chunk = list(islice(sequence, chunksize))


def process_single(img_spath, gan, mpv):
    try:
        logging.info(f"Processing {img_spath}")

        img = cv2.imread(str(img_spath))
        # Resizes image and stores it at `synth_dir.path_rot`
        # img, resize_scale = resize_image(img, args.max_width)
        resize_scale = 1.
        # Detecta e apaga a face
        with contextlib.suppress(NoFaceDetected):
            img = erase_face(img)
        # Loads and resizes annotations, storing it as .bg.json
        labels_fpath = img_spath.labels_fpath()
        json_arq = load_annotations(labels_fpath, resize_scale=resize_scale)
        with open(
            str(labels_fpath).replace(".json", ".bg.json"), mode="w", encoding="utf-8"
        ) as json_fp:
            json.dump(json_arq, json_fp)

        # Anonimize input and stores it at `synth_dir.path_back`
        logging.debug(f"Inpainting {img_spath}")
        bg_outpath = img_spath.background_fpath().as_posix()
        cv2.imwrite(
            bg_outpath,
            inpainting.inpaint_gan(
                img,
                inpainting.get_inpainting_mask(
                    img, list(inpainting.get_sensitive_roi_rectangles(json_arq))
                ),
                gan,
                mpv,
            ),
        )
        logging.info(f"Anonimization output stored at {bg_outpath}")

    except Exception as e:
        logging.error(
            f"Caught exception {e} when processing {img_spath}:\n{tcb.format_exc()}"
        )
        raise e


def process_list(img_spath_list, gan, mpv):
    for img_spath in img_spath_list:
        process_single(img_spath, gan, mpv)


def wait_for_job_completion(jobs: typing.List[mp.Process], wait_period=0.25):
    while len(jobs) > 0:
        for idx, job in enumerate(jobs):
            if not job.is_alive():
                return idx
        time.sleep(wait_period)


def process_parallel(input_list, gan, mpv):
    # sets multiprocessing via torch
    num_input_items = len(input_list)
    num_procs = min(args.num_max_procs, num_input_items)
    job_chunksize = min(args.job_chunksize, math.ceil(num_input_items / num_procs))


    mp.set_start_method("spawn")
    torch.set_num_threads(1)

    gan.share_memory()
    mpv.share_memory_()

    # launches jobs
    logging.info(
        " ".join((
                f"Distributing execution along {num_procs} threads",
                f"processing {job_chunksize} images each",
        ))
    )
    jobs: typing.List[mp.Process] = []
    for input_chunk in chunk(input_list, job_chunksize):
        # launches 1 job per given number of processes
        if len(jobs) >= num_procs:
            logging.debug("Waiting for a job to complete")
            try:
                finished_job_id = wait_for_job_completion(jobs)
                jobs[finished_job_id].close()
            except ValueError:
                raise RuntimeError()
        job = mp.Process(target=process_list, args=[input_chunk, gan, mpv])
        job.start()
        jobs.append(job)
    logging.info(f"Joining all {len(jobs)} jobs")
    for job in jobs:
        job.join()
        job.close()
        del job


def main():
    gan, mpv = load_gan_model()

    # loads input data
    synth_dir = paths.SynthesisDir(args.sample_label)
    input_list = list(synth_dir.list_input_images(for_anon=True))[:args.max_num_samples]
    logging.info(f"Finished loading {len(input_list)} images for anonimization")

    if os.environ.get("SINGLE_THREAD"):
        logging.info("Executing serially")
        process_list(input_list, gan, mpv)
    else:
        process_parallel(input_list, gan, mpv)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.debug("Caught KeyboardInterrupt\nExiting")
        exit(-1)
    except BdbQuit:
        os._exit(-2)
    except Exception as e:
        logging.error(f"Caught {type(e)} {e}\nExiting")
        logging.error(tcb.print_exc())
        exit(-3)
