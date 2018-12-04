#!/usr/bin/python3

import argparse
import cv2
import os

parser = argparse.ArgumentParser()
parser.add_argument('name')
name = parser.parse_args().name

base_dir = os.path.dirname(os.path.realpath(__file__))
face_cascade_path = os.path.join(base_dir, 'models', 'haarcascade_frontalface_default.xml')

capture = cv2.VideoCapture(0)
capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)
classifier = cv2.CascadeClassifier(face_cascade_path)
idx = 0

while True:
    ret, frame = capture.read()
    if not ret:
        print('Bad frame was received')
    else:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = classifier.detectMultiScale(
            gray,
            scaleFactor = 1.3,
            minNeighbors = 6,
            minSize = (150, 150)
        )

        if not len(faces):
            print('Faces not found')
            continue
        elif len(faces) > 1:
            print('More than one face were found')
            continue

    input('Press enter to continue..')
    fname = os.path.join(base_dir, 'users', '{}_{}.jpg'.format(name, idx))
    cv2.imwrite(fname, frame)
    print('Saved: {}'.format(fname))
    idx += 1

    # Pass single frame in the buffer
    ret, frame = capture.read()

cap.release()

