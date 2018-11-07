#!/usr/bin/python3

import os
import cv2
import sys
import magic

mime = magic.Magic(mime = True)
base_dir = os.path.dirname(os.path.realpath(__file__))
images_dir = os.path.join(base_dir, 'users')
files = list(map(lambda x: os.path.join(images_dir, x), os.listdir(images_dir)))
images = list(filter(lambda x: mime.from_file(x).startswith('image'), files))

print("Found files: ", '\n\t- '.join([''] + files))
print("Found images: ", '\n\t- '.join([''] + images))

if not len(images):
    print("Images not found")
    sys.exit(0)

face_cascade_path = os.path.join(base_dir, models, 'haarcascade_frontalface_default.xml')
face_cascade = cv2.CascadeClassifier(face_cascade_path)

for image_path in images:
    image = cv2.imread(image_path)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(
            gray_image,
            scaleFactor = 1.3,
            minNeighbors = 6,
            minSize = (150, 150),
            flags = cv2.cv.CV_HAAR_SCALE_IMAGE
        )

    if not len(faces):
        print("Faces not found on the image {}. It has been passed".format(image_path))
        continue
    elif len(faces) > 1:
        print("Found more than one face on the image {}. It has been passed.".format(image_path))
        continue
    (xtl, ytl, width, height) = faces[0]
    face_roi = image[ytl:ytl + height, xtl:xtl + width]


