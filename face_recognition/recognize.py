#!/usr/bin/python3

import numpy as np
import pickle 
import cv2
import os


base_dir = os.path.dirname(os.path.realpath(__file__))

# Loading models
face_cascade_path = os.path.join(base_dir, 'models', 'haarcascade_frontalface_default.xml')
face_cascade = cv2.CascadeClassifier(face_cascade_path)

embedding_model_path = os.path.join(base_dir, 'models', 'nn4.small2.v1.t7')
embedding_model = cv2.dnn.readNetFromTorch(embedding_model_path)

trained_svc_path = os.path.join(base_dir, 'models', 'svc')
trained_svc = pickle.loads(open(trained_svc_path, "rb").read())

label_encoder_path = os.path.join(base_dir, 'models', 'label_encoder')
label_encoder = pickle.loads(open(label_encoder_path, "rb").read())


def recognize(image):
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(
        gray_image,
        scaleFactor = 1.3,
        minNeighbors = 6,
        minSize = (150,150)
    )

    if not len(faces) or len(faces) > 1:
        return None

    (xtl, ytl, width, height) = faces[0]
    face_roi = image[ytl:ytl + height, xtl:xtl + width]
    face_blob = cv2.dnn.blobFromImage(
        face_roi,
        1.0 / 255,
        (96, 96),
        (0, 0, 0),
        swapRB = True, 
        crop = False
    )

    embedding_model.setInput(face_blob)
    user_embedding = embedding_model.forward()

    predictions = trained_svc.predict_proba(user_embedding)[0]
    j = np.argmax(predictions)
    probability = predictions[j]
    name = label_encoder.classes_[j]

    return (name, probability)


print(recognize(cv2.imread('/home/pi/IOT_Project/face_recognition/test/boris.jpg')))
