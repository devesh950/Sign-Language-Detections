import numpy as np
import pandas as pd
import keras
from keras import layers
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from keras.utils import to_categorical
import pickle

df = pd.read_csv('landmarks_dataset.csv')
labels = df['label'].values
X = df.drop(columns=['label']).values.astype('float32')

def normalize_sample(s):
    pts = s.reshape(-1,3)
    wrist = pts[0]
    pts -= wrist
    scale = np.max(np.linalg.norm(pts, axis=1))
    if scale > 0:
        pts /= scale
    return pts.flatten()

X = np.array([normalize_sample(x) for x in X])

le = LabelEncoder()
y = le.fit_transform(labels)
y = to_categorical(y)

X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, stratify=y)

inp = layers.Input(shape=(X.shape[1],))
x = layers.Dense(256, activation='relu')(inp)
x = layers.Dropout(0.3)(x)
x = layers.Dense(128, activation='relu')(x)
out = layers.Dense(y.shape[1], activation='softmax')(x)

model = keras.Model(inp, out)
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

model.fit(X_train, y_train, validation_data=(X_val, y_val), epochs=100, batch_size=32)

model.save('sign_model.h5')
with open('labels.pkl','wb') as f:
    pickle.dump(le, f)

print("✅ Model trained and saved!")
