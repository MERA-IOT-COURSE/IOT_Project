#!/usr/bin/python3

from sklearn.preprocessing import LabelEncoder
from sklearn.svm import SVC

import pickle
import os

# Path initialization
base_dir = os.path.dirname(os.path.realpath(__file__))
embeddings_data_file_path = os.path.join(base_dir, 'models', 'embeddings')
trained_svc_path = os.path.join(base_dir, 'models', 'svc')
label_encoder_path = os.path.join(base_dir, 'models', 'label_encoder')

# Embeddings is being loaded
print('\t- Embeddings is being loaded..')
embeddings_data = None
with open(embeddings_data_file_path, 'rb') as embeddings_data_file:
    embeddings_data = pickle.loads(embeddings_data_file.read())
print('\t\t- Embeddings loading process has been done.')

# Label encoder initialization
print('\t- Label encoder is being initialized..')
label_encoder = LabelEncoder()
labels = label_encoder.fit_transform(embeddings_data["names"])
print('\t\t- Label encoder initialization process has been done.')

# SVC has been 
print('\t- SVC is being trained..')
trained_svc = SVC(C=1.0, kernel="linear", probability=True)
trained_svc.fit(embeddings_data["embeddings"], labels)
print('\t\t- SVC training process has been done.')

# Writing data to filesystem
print('\t- Writing trained SVC to file system..')
with open(trained_svc_path, 'wb') as trained_svc_file:
    trained_svc_file.write(pickle.dumps(trained_svc))

print('\t- Writing label encoder to file system..')
with open(label_encoder_path, 'wb') as label_encoder_file:
    label_encoder_file.write(pickle.dumps(label_encoder))

print('Done.')

