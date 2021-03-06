# -*- coding: utf-8 -*-
"""Unsupervised Learning - PML2.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1JQSq9oTLK7qcv_o3rjYdUd2RGhQXcCZC
"""

!pip install emoji

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import re
from nltk import word_tokenize
from nltk.tokenize import RegexpTokenizer
import emoji
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score

train_data = pd.read_csv("/content/emotion-labels-train.csv")
test_data = pd.read_csv("/content/emotion-labels-test.csv")
validation_data = pd.read_csv("/content/emotion-labels-val.csv")

"""# Train *Data* """

train_data

X_train=train_data['text'].values
y_train=train_data['label'].values

sns.displot(y_train,aspect=2, height=6, color='blue')
plt.show()

"""# Validation Data"""

validation_data

X_valid=validation_data['text'].values
y_valid=validation_data['label'].values

sns.displot(y_valid,aspect=2, height=6, color='blue')
plt.show()

"""# Test Data"""

test_data

X_test=test_data['text'].values
y_test=test_data['label'].values

sns.displot(y_test,aspect=2, height=6, color='blue')
plt.show()

"""# **Preproccessing data**"""

import nltk
nltk.download('punkt')

nltk.download('wordnet')

# Preproccessing training data
preproc_words=[]
for i in train_data['text']:
  # Lowercase text
  i=i.lower()
  # Removing digits
  i=re.sub(' \d+', '', i)
  # Removing more spaces between words
  i = re.sub(' +', ' ', i)
  # Removing #
  i=re.sub('#', ' ',i)
  # Removing @
  i=re.sub('@', ' ',i)
  i=emoji.get_emoji_regexp().sub(u'', i)
  
  preproc_words.append(i)
  # print(i)
  # break

# Preproccessing validation data
preproc_words_valid=[]
for i in validation_data['text']:
  # Lowercase text
  i=i.lower()
  # Removing digits
  i=re.sub(' \d+', '', i)
  # Removing more spaces between words
  i = re.sub(' +', ' ', i)
  # Removing #
  i=re.sub('#', ' ',i)
  # Removing @
  i=re.sub('@', ' ',i)
  i=emoji.get_emoji_regexp().sub(u'', i)

  preproc_words_valid.append(i)
  # print(i)
  # break

# Preproccessing test data
preproc_words_test=[]
for i in test_data['text']:
  # Lowercase text
  i=i.lower()
  # Removing digits
  i=re.sub(' \d+', '', i)
  # Removing more spaces between words
  i = re.sub(' +', ' ', i)
  # Removing #
  i=re.sub('#', ' ',i)
  # Removing @
  i=re.sub('@', ' ',i)
  i=emoji.get_emoji_regexp().sub(u'', i)

  preproc_words_test.append(i)
  # print(i)
  # break

proccessed_data_train = pd.DataFrame(preproc_words)
proccessed_data_valid = pd.DataFrame(preproc_words_valid)
proccessed_data_test = pd.DataFrame(preproc_words_test)

train_data['text'] = proccessed_data_train[0]
validation_data['text'] = proccessed_data_valid[0]
test_data['text'] = proccessed_data_test[0]

train_data

train_labels=[]
for i in train_data['label']:
  if i == "joy":
    i=0
  elif i == "fear":
    i=1
  elif i == "anger":
    i=2
  elif i =="sadness":
    i=3
  train_labels.append(i)

test_labels=[]
for i in test_data['label']:
  if i == "joy":
    i=0
  elif i == "fear":
    i=1
  elif i == "anger":
    i=2
  elif i =="sadness":
    i=3
  test_labels.append(i)

valid_labels=[]
for i in validation_data['label']:
  if i == "joy":
    i=0
  elif i == "fear":
    i=1
  elif i == "anger":
    i=2
  elif i =="sadness":
    i=3
  valid_labels.append(i)

train_labels_df=pd.DataFrame(train_labels)
train_data['label'] = train_labels_df[0]
test_labels_df=pd.DataFrame(test_labels)
test_data['label'] = test_labels_df[0]
valid_labels_df=pd.DataFrame(valid_labels)
validation_data['label'] = valid_labels_df[0]

validation_data

"""# **Model Preparation**"""

from sklearn.feature_extraction.text import CountVectorizer
vect = CountVectorizer(lowercase=True)

X_tr = vect.fit_transform(train_data['text'])
X_tr=X_tr.toarray()
X_ts = vect.transform(test_data['text'])
X_ts=X_ts.toarray()
X_val = vect.transform(validation_data['text'])
X_val=X_val.toarray()

tfidf = TfidfVectorizer(lowercase = True)
tfidf_rep = tfidf.fit(train_data['text'])

X_train = tfidf.transform(train_data['text'])
X_test = tfidf.transform(test_data['text'])
X_valid = tfidf.transform(validation_data['text'])

y_train = train_data['label']
y_test = test_data['label']
y_valid = validation_data['label']

X_valid.shape

# Supervised Comparison
from sklearn.linear_model import RidgeClassifier
from sklearn.model_selection import GridSearchCV
parameters = {'alpha':(1.0,0.8), 'fit_intercept': (True,False),
              'max_iter':(None, 2), 'class_weight':('dict','balanced',None), 
              'tol':(1e-4, 1e-3),'solver':['auto']}
clf = RidgeClassifier()
clf = GridSearchCV(clf, parameters)
clf.fit(X_train, y_train)
sorted(clf.cv_results_.keys())
print('Train Score', clf.score(X_train, y_train))
print('Test Score', clf.score(X_test, y_test))
print('Validation Score', clf.score(X_valid, y_valid))

# Supervised Comparison
from sklearn.linear_model import RidgeClassifier
from sklearn.model_selection import GridSearchCV
parameters = {'alpha':(1.0,0.8), 'fit_intercept': (True,False),  'max_iter':(None, 2), 'class_weight':('dict','balanced',None), 'tol':(1e-4, 1e-3),'solver':['auto']}
clf = RidgeClassifier()
clf = GridSearchCV(clf, parameters)
clf.fit(X_tr, y_train)
sorted(clf.cv_results_.keys())
print('Train Score', clf.score(X_tr, y_train))
print('Test Score', clf.score(X_ts, y_test))
print('Validation Score', clf.score(X_val, y_valid))

"""Spectral on Tfidf features"""

from sklearn.cluster import SpectralClustering
import numpy as np
import matplotlib.pyplot as plt

clustering = SpectralClustering(n_clusters=4,
assign_labels='discretize',
eigen_solver='arpack',
random_state=0, affinity='rbf').fit_predict(X_train)

clustering1 = SpectralClustering(n_clusters=4,
assign_labels='discretize',
eigen_solver='arpack',
random_state=0, affinity='rbf').fit_predict(X_test)

clustering2 = SpectralClustering(n_clusters=4,
assign_labels='discretize',
eigen_solver='arpack',
random_state=0, affinity='rbf').fit_predict(X_valid)
print(accuracy_score(y_train, clustering))
print(accuracy_score(y_test, clustering1))
print(accuracy_score(y_valid, clustering2))

from sklearn.decomposition import TruncatedSVD
import numpy as np


svd = TruncatedSVD(n_components=2, random_state=42)
svd.fit(X_train)

X_train_pca = svd.transform(X_train)

X_train_pca.shape

y_train.values

colormap[y_train.values]

color = np.array(['r', 'g', 'b','y'])
plt.scatter(X_train_pca[:,0],X_train_pca[:,1], c=color[y_train.values])

plt.scatter(X_train_pca[:,0],X_train_pca[:,1], c=colormap[clustering])

clustering1 = SpectralClustering(n_clusters=4,
assign_labels='discretize',
eigen_solver='arpack',
random_state=0, affinity='rbf').fit(X_test)

clustering1.get_params

"""Spectral on CountVectorizer"""

from sklearn.cluster import SpectralClustering
import numpy as np
import matplotlib.pyplot as plt


clustering = SpectralClustering(n_clusters=4,
        assign_labels='discretize',
        random_state=0).fit(X_tr)
y=clustering.fit_predict(X_ts)
accuracy_score(y_test, y)

y[:200]

"""GMM on Tfidf features"""

from sklearn.mixture import GaussianMixture
from sklearn.metrics import accuracy_score
gm = GaussianMixture(n_components = 4, random_state = 0,covariance_type = 'diag',tol=1e-4,init_params='random',warm_start=True).fit(X_train.toarray())
gmm_lab_test = gm.predict(X_test.toarray())
gmm_lab_valid = gm.predict(X_valid.toarray())
accuracy_score(y_test, gmm_lab_test)
# accuracy_score(y_test, gmm_lab_valid)
# X_train['GMM'] = gmm_lab
# gmm_lab

colormap = np.array(['r', 'g', 'b','y'])
plt.scatter(X_train_pca[:,0],X_train_pca[:,1], c=colormap[gm.predict(X_train.toarray())])

"""Gmm on CountVectorizer"""

from sklearn.mixture import GaussianMixture
from sklearn.metrics import accuracy_score
gm = GaussianMixture(n_components = 4, 
random_state = 0,
covariance_type = 'diag',
tol=1e-4,
init_params='random').fit(X_tr)
gmm_lab = gm.predict(X_ts)
accuracy_score(y_test, gmm_lab)

"""Kmeans Tfidf"""

from sklearn.cluster import KMeans
import numpy as np
kmeans = KMeans(n_clusters=4, random_state=0, init='k-means++',tol=1e-3,algorithm='auto').fit(X_train)
kmeans.labels_

kmeans_pred=kmeans.predict(X_test)
accuracy_score(y_test, kmeans_pred)

# kmeans.cluster_centers_

"""Kmeans CountVect"""

from sklearn.cluster import KMeans
import numpy as np
kmeans = KMeans(n_clusters=4, random_state=0, init='k-means++',tol=1e-3,algorithm='auto').fit(X_tr)
kmeans.labels_

kmeans_pred=kmeans.predict(X_ts)
accuracy_score(y_test, kmeans_pred)

y_test

gmm_lab[:200]

"""Random Chance"""

random_chance = np.random.randint(0,4,len(test_labels))

accuracy_score(y_test, random_chance)

random_chance[:100]

1 2 3
3 2 1

len(test_labels)

arr = np.zeros(3142)

arr

kmeans_pred[:15]

from sklearn.metrics import confusion_matrix

confusion_matrix(y_test, y)

arr[kmeans_pred==0] =1
arr[kmeans_pred==1] =0
arr[kmeans_pred==2] =2
arr[kmeans_pred==3] =3

accuracy_score(y_test, arr)

accuracy_score(y_test, kmeans_pred)