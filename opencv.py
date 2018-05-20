import os
import sys
import cv2
import numpy as np
import logging
import shutil
from peewee import *

MODEL_FILE = "model.mdl"

def detect(img, cascade):
  gray = to_grayscale(img)
  rects = cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=4, minSize=(30, 30), flags = cv2.CASCADE_SCALE_IMAGE)

  if len(rects) == 0:
    return []
  return rects

def detect_faces(img):
  cascade = cv2.CascadeClassifier("data/haarcascade_frontalface_alt.xml")
  return detect(img, cascade)

def to_grayscale(img):
  gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
  gray = cv2.equalizeHist(gray)
  return gray

def contains_face(img):
  return len(detect_faces(img)) > 0

def save(path, img):
  cv2.imwrite(path, img)

def crop_faces(img, faces):
  for face in faces:
    x, y, h, w = [result for result in face]
    return img[y:y+h,x:x+w]

def load_images(path):
  images, labels = [], []
  c = 0
  print ("test " + path)
  for dirname, dirnames, filenames in os.walk(path):
    print ("test")
    for subdirname in dirnames:
      subjectPath = os.path.join(dirname, subdirname)
      for filename in os.listdir(subjectPath):
        try:
          img = cv2.imread(os.path.join(subjectPath, filename), cv2.IMREAD_GRAYSCALE)
          images.append(np.asarray(img, dtype=np.uint8))
          labels.append(c)
        except IOError as err:
          errno, strerror = e.args
          print (errno, strerror)
        #except IOError, (errno, strerror):
          #print "IOError({0}): {1}".format(errno, strerror)
        except:
          print ("Unexpected error:" , sys.exc_info()[0])
          raise
      c += 1
    return images, labels

def load_images_to_db(path):
  for dirname, dirnames, filenames in os.walk(path):
    for subdirname in dirnames:
      subject_path = os.path.join(dirname, subdirname)
      label , iscreated = Label.get_or_create(name=subdirname)
      label.save()
      for filename in os.listdir(subject_path):
        path = os.path.abspath(os.path.join(subject_path, filename))
        logging.info('saving path %s' % path)
        image , iscreated = Image.get_or_create(path=path, label=label)
        image.save()

def load_images_from_db():
  images, labels = [],[]
  for label in Label.select():
    for image in label.image_set:
      try:
        cv_image = cv2.imread(image.path, cv2.IMREAD_GRAYSCALE)
        cv_image = cv2.resize(cv_image, (100,100))
        images.append(np.asarray(cv_image, dtype=np.uint8))
        labels.append(label.id)
      except IOError as err:
        errno, strerror = e.args
        print (errno, strerror)
      #except IOError, (errno, strerror):
       #print "IOError({0}): {1}".format(errno, strerror)
  return images, np.asarray(labels)

def train():
  images, labels = load_images_from_db()
  #model = cv2.createFisherFaceRecognizer() #old
  model = cv2.face.FisherFaceRecognizer_create()
  model.train(images,labels)
  model.save(MODEL_FILE)

def predict(cv_image):
  faces = detect_faces(cv_image)
  result = None
  if len(faces) > 0:
    cropped = to_grayscale(crop_faces(cv_image, faces))
    resized = cv2.resize(cropped, (100,100))
    model = cv2.face.FisherFaceRecognizer_create()
    #model = cv2.createFisherFaceRecognizer()
    #model = cv2.createEigenFaceRecognizer()
    #model.load(MODEL_FILE)
    model.read(MODEL_FILE)
    prediction = model.predict(resized)
    result = {
      'face': {
        'id': prediction[0],
        'name': Label.get(Label.id == prediction[0]).name,
        'distance': prediction[1],
        'coords': {
          'x': str(faces[0][0]),
          'y': str(faces[0][1]),
          'width': str(faces[0][2]),
          'height': str(faces[0][3])
          }
       }
    }
  return result

db = SqliteDatabase("data/images.db")
class BaseModel(Model):
  class Meta:
    database = db

class Label(BaseModel):
  IMAGE_DIR = "data/images"

  name = CharField()

  def persist(self):
    path = os.path.join(self.IMAGE_DIR, self.name)
    #if directory exists with 10 images
    #delete it and recreate
    if os.path.exists(path) and len(os.listdir(path)) >= 10:
      shutil.rmtree(path)

    if not os.path.exists(path):
      logging.info("Created directory: %s" % self.name)
      os.makedirs(path)

    Label.get_or_create(name=self.name)

class Image(BaseModel):
  IMAGE_DIR = "data/images"
  path = CharField()
  label = ForeignKeyField(Label)

  def persist(self, cv_image):
    path = os.path.join(self.IMAGE_DIR, self.label.name)
    nr_of_images = len(os.listdir(path))
    if nr_of_images >= 10:
      return 'Done'
    faces = detect_faces(cv_image)
    if len(faces) > 0 and nr_of_images < 10:
      path += "/%s.jpg" % nr_of_images
      path = os.path.abspath(path)
      logging.info("Saving %s" % path)
      cropped = to_grayscale(crop_faces(cv_image, faces))
      cv2.imwrite(path, cropped)
      self.path = path
      self.save()
#Todo @add_face to specific dirs and record to table
class Attendance(BaseModel):
  IMAGE_DIR = "data/images"
  label = ForeignKeyField(Label)

  def persist(self):
    Attendance.create(label_id=self.label.id)


if __name__ == "__main__":
  load_images_to_db("data/images")
  #train()

  print ('done')
  #predict()
  #train()
