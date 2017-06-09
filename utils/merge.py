import os
import glob

import numpy as np

NPZ_DIR = "../npz"

print(os.path.abspath(NPZ_DIR))
X = np.empty((0, 96, 1366, 1))
y = np.empty((0, 7))
npz_files = glob.glob(os.path.join(NPZ_DIR, 'genre*'))
print(npz_files)
for fn in npz_files:
    print(fn)
    data = np.load(fn)
    X = np.append(X, data['X'], axis=0)
    y = np.append(y, data['y'], axis=0)

print(X.shape, y.shape)
for r in y:
    if np.sum(r) > 1.5:
        print(r)
np.savez('genre', X=X, y=y)
