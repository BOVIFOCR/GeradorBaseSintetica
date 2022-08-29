""" make_funsd_data.py """
import io
import os
import re
import sys
import cv2
import glob
import gzip
import json
import codecs
import logging
import argparse
import csv

__dir__ = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(os.path.join(__dir__, '../')))
sys.path.append(os.path.abspath(os.path.join(__dir__, '../../')))

from collections import namedtuple
from model.ernie.tokenizing_ernie import ErnieTokenizer

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

whit_space_pat = re.compile(r'\S+')
pat = re.compile(r'([a-zA-Z0-9]+|\S)')
cls_dict = {'other': 0, 'header': 1, 'question': 2, 'answer': 3}
cls_dict_full = {"unknown":0 , "meta": 1, "info-nome": 2, "nome": 3, "info-filiacao": 4, "filiacao": 5, "info-datanasc": 6,
        "data-nascimento": 7, "info-org": 8, "org": 9, "info-rh": 10, "fator-rh": 11, "info-naturalidade":12,
        "naturalidade": 13, "info-obs": 14, "info-asstitular": 15, "ass-titular": 16, "5-code": 17, "info-rg": 18,
        "rg": 19, "info-cpf": 20, "cpf": 21, "info-doc": 22, "doc-origem": 23, "comarca": 24, "obs": 25, "info-dataexp":26,
        "data-expedicao":27, "info-assdiretor": 28, "ass-diretor": 29}
cls_dict_full = {'header-nome': 0, 'nomeMae': 1, 'naturalidade': 2, 'header-obs': 3, 'serial?': 4, 'header-datanasc': 5, 'header-orgaoexp': 6, 'assin': 7, 'tag': 8, 'header-rh': 9, 'nomePai': 10, 'orgaoEmissor': 11, 'cod-sec': 12, 'header-naturalidade': 13, 'header-filiacao': 14, 'dataNascimento': 15, 'nome': 16, 'header-assin': 17}

def merge_subword(tokens):
    """
    :param tokens:
    :return: merged_tokens
    """
    ret = []
    for token in tokens:
        if token.startswith("##"):
            real_token = token[2:]
            if len(ret):
                ret[-1] += real_token
            else:
                ret.append(real_token)
        else:
            ret.append(token)
    return ret

def parse_txt(line, tokenizer):
    """
    char tokenizer (wordpiece english)
    normed txt(space seperated or not) => list of word-piece
    """
    ret_line = []
    line = line.lower()
    if len(line) == 0:
        return ret_line
    for sub in pat.finditer(line):
        s, e = sub.span()
        sen = line[s:e]
        for ll in tokenizer.tokenize(sen):
            ret_line.append(ll)

    #ret_line = tokenizer.convert_tokens_to_ids(ret_line)
    return ret_line

def get_word_bboxes(bbox, n_words):
    ret = []
    for i in range(1, n_words + 1):
        offset_up = int(round((bbox[2] - bbox[0])*i/n_words, 1))
        offset_down = int(round((bbox[2] - bbox[0])*(i-1)/n_words, 1))
        ret.append((bbox[0] + offset_down, bbox[1], bbox[0] + offset_up, bbox[3]))

    return ret

def read_example_from_file(label, image_name, tokenizer):
    """
    convert label_file to pickle example
    """

    ids = []
    tokens = []
    line_bboxes = []
    token_bboxes = []
    cls_label = []
    linkings = []
    for idx, line in enumerate(label):
        id = int(line[0])
        line_bbox = (int(line[1]), int(line[2]), int(line[5]), int(line[6]))
        cls = cls_dict_full.get(line[-1].strip('\n'))
        linking = [] # ???
        words = ",".join(line[9:-1]).split(' ')
        for w in words:
            if len(w.strip()) == 0:
                w = '[UNK]'
        text = [x for x in words]
        token_bbox = get_word_bboxes(line_bbox, len(words)) # Word coors not available in BID.
        token = [parse_txt(word, tokenizer) for word in text]

        ids.append(id)
        tokens.append(token)
        token_bboxes.append(token_bbox)
        line_bboxes.append(line_bbox)
        linkings.append(linking)
        cls_label.append(cls)
    example = {'ids': ids,
               'cls': cls_label,
               'tokens': tokens,
               'line_bboxes': line_bboxes,
               'token_bboxes': token_bboxes,
               'linkings': linkings,
               'image_name': image_name}
    return example


def build_dataset(label_dir, out_dir, config):
    """
    extract & parse doc_label
    """
    os.makedirs(out_dir, exist_ok=True)
    dict_params = config['dict_params']
    tokenizer = ErnieTokenizer.init(config['dict_path'], **dict_params)
    label_files = glob.glob(os.path.join(label_dir, '*.tsv'))
    for label_file in label_files:
        image_name = os.path.basename(label_file).replace('tsv', 'jpg')
        with codecs.open(label_file, 'r', 'utf-8') as f:
        #    label = json.load(f)['form']
             csr = csv.reader(f)
             label = [x for x in csr]
        example = read_example_from_file(label, image_name, tokenizer)
        #print(example)
        if example is None:
            raise ValueError('Failed to parse label of (%s)', image_path)
        save_path = os.path.join(out_dir, image_name + '.label')
        with gzip.open(save_path, 'wb') as w:
            w.write(json.dumps(example).encode('utf-8'))
        logging.info('Parsing %s', image_name)


if __name__ == '__main__':
    parser = argparse.ArgumentParser('FUNSD Data Maker')
    parser.add_argument('--config_file', type=str, required=True)
    parser.add_argument('--label_dir', type=str, required=True)
    parser.add_argument('--out_dir', type=str, required=True)

    args = parser.parse_args()
    assert os.path.exists(args.config_file)
    config = json.loads(open(args.config_file).read())

    build_dataset(args.label_dir, args.out_dir, config['eval']['dataset'])
    logging.info('done: %s' % args.out_dir)
