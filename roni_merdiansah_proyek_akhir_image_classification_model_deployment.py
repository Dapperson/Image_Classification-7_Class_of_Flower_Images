# -*- coding: utf-8 -*-
"""Roni Merdiansah - Proyek Akhir : Image Classification Model Deployment.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1UlgBx-ABkkLAfCWm5wasGXIKT2JbkaF3

Nama : Roni Merdiansah

Untuk dataset yang digunakan sudah melalui proses `train_test_split` sehingga sudah terdapat folder untuk training dan validation, hanya tinggal melanjutkan proses augmentation, melatih dan evaluasi data, serta melabeli data secara otomatis

Data juga sudah memenuhi kriteria kurang lebih 80% train set dan 20% test set

---

Link dataset :
https://www.kaggle.com/datasets/junkal/flowerdatasets
"""

! pip install -q kaggle

from google.colab import files

files.upload()

!mkdir -p ~/.kaggle
!cp kaggle.json ~/.kaggle/
!chmod 600 ~/.kaggle/kaggle.json
!ls ~/.kaggle

!kaggle datasets download -d junkal/flowerdatasets

!mkdir flowerdatasets
!unzip flowerdatasets.zip -d flowerdatasets
!ls flowerdatasets

import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Input
from sklearn.model_selection import train_test_split
import numpy as np
import matplotlib.pyplot as plt
import pathlib
import zipfile,os,shutil

train_dir = os.path.join('/content/flowerdatasets/flowers/train')
valid_dir = os.path.join('/content/flowerdatasets/flowers/val')

os.listdir(train_dir)

train_datagen = ImageDataGenerator(
    rescale = 1./255,
    rotation_range = 20,
    horizontal_flip = True,
    shear_range = 0.2,
    validation_split = 0.2,
    fill_mode = 'nearest',
)
test_datagen = ImageDataGenerator(
    rescale = 1./225
    # rotation_range = 20,
    # horizontal_flip = True,
    # vertical_flip = True,
    # shear_range = 0.2,
    # validation_split = 0.2,
    # fill_mode = 'nearest'
)

train_generator = train_datagen.flow_from_directory(
    train_dir,
    target_size=(150,150),
    batch_size= 32,
    class_mode='categorical'
)

validation_generator = test_datagen.flow_from_directory(
    valid_dir,
    target_size = (150,150),
    batch_size = 32,
    class_mode = 'categorical'
)

"""Saat dijumlah total data image adalah 10.375

---

Bila dikalikan 80% maka hasilnya adalah 8300

Bila dikalikan 20% maka hasilnya adalah 2075

---
Hasil yang didapatkan tidak terlalu jauh perbedaannya, sehingga dapat disimpulkan bahwa data train dan validation sudah sesuai ketetuan 80% dan 20%

*(saya sudah melakukan survei sebelumnya bahwa jumlah persentase data saat melakukan `train_test_split` hasilnya tidak sama persis dengan kalkulator)*



"""

#Menggunakan model CNN & Layer Max Pooling
model = tf.keras.models.Sequential([
  tf.keras.layers.Conv2D(32, (3,3), activation = 'relu', input_shape= (150,150,3)),
  tf.keras.layers.MaxPooling2D(2,2),
  tf.keras.layers.Conv2D(64,(3,3), activation= 'relu'),
  tf.keras.layers.MaxPooling2D(2,2),
  tf.keras.layers.Flatten(),
  tf.keras.layers.Dropout(0.5),
  tf.keras.layers.Dense(128, activation= 'relu'),
  tf.keras.layers.Dense(7, activation= 'softmax')
])

model.summary()
model.compile(loss='categorical_crossentropy',
              optimizer=tf.optimizers.Adam(),
              metrics=['accuracy'])

class myCallback(tf.keras.callbacks.Callback):
  def on_epoch_end(self, epoch, logs={}):
    if(logs.get('accuracy') > 0.92 and logs.get('val_accuracy') > 0.92): #artinya berhenti bila nilai lebih dari 92%
      print("\nAkurasi di atas 92%, hentikan training!")
      self.model.stop_training = True

callbacks = myCallback()

history = model.fit(
    train_generator,
    steps_per_epoch = 252, # 8069 images = batch_size(32) * steps(252)
    epochs = 50,
    validation_data = validation_generator,
    validation_steps = 72, # 2306 images = batch_size(32) * steps(72)
    verbose =2,
    callbacks=[callbacks]
)

import matplotlib.pyplot as plt
plt.figure(figsize=(15,5))
plt.plot(history.history['accuracy'])
plt.plot(history.history['val_accuracy'])
plt.title('Model Accuracy')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()

plt.figure(figsize=(15,5))
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('Model Loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()

# Menyimpan model dalam format SavedModel
export_dir = 'saved_model/'
tf.saved_model.save(model, export_dir)
 
# Convert SavedModel menjadi vegs.tflite
converter = tf.lite.TFLiteConverter.from_saved_model(export_dir)
tflite_model = converter.convert()
 
tflite_model_file = pathlib.Path('flowers.tflite')
tflite_model_file.write_bytes(tflite_model)

# #main driver
# import numpy as np
# from google.colab import files
# from keras.preprocessing import image
# import matplotlib.pyplot as plt
# import matplotlib.image as mpimg
# import matplotlib.pyplot as plt
# import matplotlib.image as mpimg
# %matplotlib inline

# uploaded = files.upload()

# for fn in uploaded.keys():

#   path = fn 
#   img = image.load_img(path, target_size =(150,150))
#   imgplot = plt.imshow(img)
#   x = image.img_to_array(img)
#   x = np.expand_dims(x, axis=0)

#   images = np.vstack([x])
#   classes = model.predict(images, batch_size=10)

#   print(fn)
#   if classes[0,1]!=0:
#     print('daisy')
#   elif classes[0,2]!=0:
#     print('rose')
#   elif classes[0,3]!=0:
#     print('lily')
#   elif classes[0,4]!=0:
#     print('orchid')
#   elif classes[0,5]!=0:
#     print('dandelion')
#   elif classes[0,6]!=0:
#     print('tulip')
#   elif classes[0,7]!=0:
#     print('sunflower')

  
# # ['daisy', 'rose', 'lily', 'orchid', 'dandelion', 'tulip', 'sunflower']