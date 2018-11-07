#!/usr/bin/python3

import os
import cv2
import sys
import magic
import pickle

mime = magic.Magic(mime = True)

base_dir = os.path.dirname(os.path.realpath(__file__))
images_dir = os.path.join(base_dir, 'users')

# Get all images from "users" dir
files = list(map(lambda x: os.path.join(images_dir, x), os.listdir(images_dir)))
images = list(filter(lambda x: mime.from_file(x).startswith('image'), files))

print("Found files: ", '\n\t- '.join([''] + files))
print("Found images: ", '\n\t- '.join([''] + images))

if not len(images):
    print("Images not found")
    sys.exit(0)

# Load models
face_cascade_path = os.path.join(base_dir, 'models', 'haarcascade_frontalface_default.xml')
face_cascade = cv2.CascadeClassifier(face_cascade_path)
print("\n")
print("* Face haarcascade has been loaded successfully")

embedding_model_path = os.path.join(base_dir, 'models', 'nn4.small2.v1.t7')
embedding_model = cv2.dnn.readNetFromTorch(embedding_model_path)
print("* Embedding model has been loaded successfully")
print("\n")


data = {
    "embeddings": [],
    "names": []
}

# Detect faces and compute embeddings with opencv dnn module
for image_path in images:
    username = os.path.splitext(os.path.basename(image_path))[0]
    # Detect faces on an image. It requires a grayscale image
    print("Image {} is being processed..".format(image_path))
    image = cv2.imread(image_path)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(
            gray_image,
            scaleFactor = 1.3,
            minNeighbors = 6,
            minSize = (150, 150)
        )

    if not len(faces):
        print("Faces not found on an image. It has been passed.")
        continue
    elif len(faces) > 1:
        print("Found more than one face. Image has been passed.")
        continue

    (xtl, ytl, width, height) = faces[0]
    face_roi = image[ytl:ytl + height, xtl:xtl + width]
    print("Face has been found with size {}x{}".format(width, height))
    
    # DNN part. Get embedding for detected face
    face_blob = cv2.dnn.blobFromImage(
            face_roi, 
            1.0 / 255, 
            (96, 96), 
            (0, 0, 0),
            swapRB=True,
            crop=False
        )

    embedding_model.setInput(face_blob)
    user_embedding = embedding_model.forward().flatten()

    data["embeddings"].append(user_embedding)
    data["names"].append(username)

    print("Image processing done.")
    print("\n")


embeddings_data_file_path = os.path.join(base_dir, 'embeddings')
with open(embeddings_data_file_path, 'wb') as embeddings_data_file:
    embeddings_data_file.write(pickle.dumps(data))

