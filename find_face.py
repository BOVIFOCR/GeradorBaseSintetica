# Detecção e blur do rosto presente nos documentos solicitados.
from PIL import Image, ImageFilter
import image_slicer
import cv2 as cv
import dlib
import os
import numpy as np

dnn = dlib.cnn_face_detection_model_v1("./files/mmod_human_face_detector.dat")  # Detector pré-treinado.


def erase_face(img):
    rects = dnn(img)
    for rect in rects:
        x1 = rect.rect.left()
        y1 = rect.rect.top()
        x2 = rect.rect.right()
        y2 = rect.rect.bottom()
        x_ini = x1 - 20
        y_ini = y1 - 25
        x_fin = x2 + 20
        y_fin = y2 + 25
        img[y_ini:y_fin, x_ini:x_fin] = 255, 255, 255
    return img
