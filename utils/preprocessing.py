import os
import mysql.connector
import librosa as lb
import numpy as np
from itertools import chain

fs = 12000  # sampling rate
N_FFT = 512  # length of fft window
n_mels = 96
N_OVERLAP = 256
duration = 29.12

config = {
    'user': 'root',
    'password': '***REMOVED***',
    'host': '127.0.0.1',
    'database': 'emosic',
}

cnx = mysql.connector.connect(**config)
cursor = cnx.cursor()


def log_ceps(fn):
    y, sr = lb.load(fn, sr=fs)
    n_sample = y.shape[0]
    n_sample_fit = int(duration * fs)

    if n_sample < n_sample_fit:
        y = np.hstack((y, np.zeros((int(duration * fs) - n_sample,))))
    elif n_sample > n_sample_fit:
        y = y[(n_sample - n_sample_fit) // 2:(n_sample + n_sample_fit) // 2]

    melspect = lb.logamplitude(lb.feature.melspectrogram(
        y=y, sr=fs, hop_length=N_OVERLAP, n_fft=N_FFT, n_mels=n_mels) ** 2, ref_power=1.0)
    return melspect


def write_ceps(files, index, leng):
    rows = len(files)
    features = []
    labels = np.zeros((rows, leng), np.int)
    for i, fn in enumerate(files):
        ceps = log_ceps(os.path.join('/home/dobro/project/emosic/static', fn))
        features.append(ceps)
        labels[i, index] = 1
        print("idx {}".format(i), "label {}".format(index), fn, 'done')
    features = np.asarray(features)
    print(features.shape)
    features = features.reshape(features.shape[0], features.shape[1], features.shape[2], 1)
    return features, labels


def create_ceps(type):
    if type == 'mood':
        for i in range(1, 11): #Bright ~ Romantic
            query = "SELECT url FROM music WHERE moodid = %s and length > 30 ORDER BY rand() limit 54"
            cursor.execute(query, (i, ))
            tuples = cursor.fetchall()
            files = list(chain.from_iterable(tuples))
            X, y = write_ceps(files, i - 1, 10)
            np.savez('mood_sound_{}'.format(i), X=X, y=y)
    else:
        for i in range(1, 8):
            query = "SELECT url FROM music WHERE genreid = %s and length > 30 ORDER BY rand() limit 70"
            cursor.execute(query, (i, ))
            tuples = cursor.fetchall()
            files = list(chain.from_iterable(tuples))
            X, y = write_ceps(files, i - 1, 7)
            np.savez('genre_sound_{}'.format(i), X=X, y=y)

if __name__ == '__main__':
    os.chdir('../npz')
    print(os.path.abspath(os.path.curdir))
    #create_ceps('mood')
    create_ceps('genre')
    cnx.close()
