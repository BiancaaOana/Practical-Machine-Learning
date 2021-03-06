# -*- coding: utf-8 -*-
"""Word Complexity Challange.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1cb_c69VNMsLnpKXBjkUPC1TvMAsjNzdX
"""

# Imported libraries
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
import numpy
from sklearn.metrics import mean_absolute_error

# Mounting the google drive where I saved the data from competition
from google.colab import drive
drive.mount("/content/gdrive")

!unzip "/content/gdrive/MyDrive/pml-unibuc-2021.zip" -d "/content/gdrive/MyDrive/pml-unibuc-2021"

"""# **Train Data Visualization**

Saving the training file into a variable so I can use it to show the table of the training data. I also renamed the columns with more suggestive names.
"""

train_file = "/content/gdrive/MyDrive/pml-unibuc-2021/train_full.txt"

df=pd.read_table(train_file,header=None)

train_table = df.rename(columns = {0: 'ID', 1: 'Sentence', 2:'Start_Offset', 3:'End_Offset', 4:'Target Word',5:'NatAnnot', 6:'NonNatAnnot',7:'NrNat',8:'NrNonNat', 9:'Prob'}, inplace = False)

"""complexity = (NrNat+NrNonNat)/(NatAnnot+NonNatAnnot)"""

train_table

# Dropped 2 of the columns because they had a constant value of 10 and I thought it won't help me that much
train_table.drop(['NrNat', 'NrNonNat'],
  axis='columns', inplace=True)

train_table

# Showing the first 100 datas that have the highest probability
train_table.nlargest(100,['Prob'])

# Plotting the frequency based on probability
plt.hist(train_table['Prob'], bins=5)
plt.show()

# Creating a feature that shows the length of the target word
train_table["LenWord"]= train_table["Target Word"].apply( lambda x: len(x))

lenvsprob = train_table.groupby(['LenWord'])['Prob'].value_counts()

# Using wordnet for extracting features
import nltk 
from nltk.corpus import wordnet as wn
nltk.download('wordnet')

# The length of the definition of the word
def len_synset(sysnet):
  if len(sysnet) == 0:
    return 0
  else:
    return len(sysnet[0].definition().split())

# Type of word
def len_hyp(sysnet):
  if len(sysnet) == 0:
    return 0
  else:
    return sysnet[0].pos()

#semantic field of the word
def len_hyo(sysnet):
  if len(sysnet) == 0:
    return 0
  else:
    return len(sysnet[0].member_holonyms())
def len_lem(sysnet):
  if len(sysnet) == 0:
    return 0
  else:
    return len(sysnet[0].lemmas())

# Function for calculating the number of vowels and cons
def calcul_voc(word):
  v=0
  c=0
  vocale = ['a','e','i','o','u']
  for i in word:
    if(i in vocale):
      v+=1
    else:
      c+=1
  return v,c


vowels =[]
cons =[]
for j in train_table['Target Word'].values:
  returned = calcul_voc(j)
  vowels.append(returned[0])
  cons.append(returned[1])
  # creating dictionary for types of words
pos_dict = {0 : 0 ,"n" : 1, "v" : 2, "a" : 3, "s" : 4, "r" : 5}
# creating columns in my table with all the features I extracted
train_table["Vowels"] = vowels
train_table["Cons"] = cons
train_table["LenWord"]= train_table["Target Word"].apply( lambda x: len(x))
train_table["NumSyns"]= train_table["Target Word"].apply( lambda x: len(wn.synsets(x)))
train_table["LenDef"]= train_table["Target Word"].apply( lambda x: len_synset(wn.synsets(x)))
train_table["Capital"]= train_table["Target Word"].apply( lambda x: int(x==x.lower()))
train_table["Type"]= train_table["Target Word"].apply( lambda x: pos_dict[len_hyp(wn.synsets(x))])
# train_table["NumHyo"]= train_table["Target Word"].apply( lambda x: len_hyo(wn.synsets(x)))
# train_table["NumLem"]= train_table["Target Word"].apply( lambda x: len_lem(wn.synsets(x)))

train_table

# Plot showing the connection between the length of the word and their complexity
plt.hist(lenvsprob)
plt.show()

train_table.corr()

# def calcul_voc(word):
#   v=0
#   c=0
#   vocale = ['a','e','i','o','u']
#   for i in word:
#     if(i in vocale):
#       v+=1
#     else:
#       c+=1
#   return v,c


# vowels =[]
# cons =[]
# for j in train_table['Target Word'].values:
#   returned = calcul_voc(j)
#   vowels.append(returned[0])
#   cons.append(returned[1])

# Creating columns in the table for no of vowels and cons
# train_table["Vowels"] = vowels
# train_table["Cons"] = cons

train_datas = train_table[["LenWord","Vowels","Cons"]]
labels = train_table["Prob"]

X_train, X_test, y_train, y_test = train_test_split(train_datas.values, labels.values, test_size=0.33, random_state=42)

y_train

"""Some tryings"""

# First try Linear Regressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error
reg = LinearRegression().fit(X_train, y_train)
mean_absolute_error(reg.predict(X_test),y_test)

# Second try with SGD and Standard Scaler, changed the parameters in order to obtain better results
from sklearn.linear_model import SGDRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
regr = make_pipeline(StandardScaler(),
                    SGDRegressor(loss= 'huber',penalty = 'l2',max_iter=1000, 
                    tol=1e-3, random_state=1,epsilon=0.01,
                    learning_rate='invscaling',
                    average=15))
regr.fit(X_train, y_train)
mean_absolute_error(regr.predict(X_test),y_test)

# Decision Tree Regressor with Standard Scaler
from sklearn.svm import SVC
from sklearn import tree
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.metrics import mean_absolute_error
clf = make_pipeline(StandardScaler(),tree.DecisionTreeRegressor(max_depth=2,
                                  criterion='absolute_error')) 
clf = clf.fit(X_train, y_train)
mean_absolute_error(clf.predict(X_test),y_test)

# MLP Regressor, again, tried various values for parameters in order to obtai better results
from sklearn.neural_network import MLPRegressor
regr = MLPRegressor(random_state=1,activation='logistic', max_iter=500,
                    solver='adam',batch_size=10, learning_rate='adaptive',
                    learning_rate_init=0.001,shuffle=False,tol=1e-5,
                    epsilon=1e-9).fit(X_train, y_train)
mean_absolute_error(regr.predict(X_test),y_test)

# hyperparameter boosting
params = {'bootstrap': [True, False],
 'max_depth': [5, 50, None],
 'max_features': ['auto', 'sqrt'],
 'min_samples_leaf': [1, 4],
 'min_samples_split': [2, 6],
 'n_estimators': [100, 1600, 4000]}

from sklearn.feature_extraction.text import TfidfVectorizer
vect = TfidfVectorizer(max_features=200)
vect.fit([" ".join(word for word in sentence)for sentence in data])

target_words_train = vect.transform(train_table['Target Word']).todense()

target_words_train[:,vect.vocabulary_[train_table['Target Word'][0]]].shape

"""# Test File

Saving the test file into a variable so I can use it to show the table of the test data. I also renamed the columns with more suggestive names.
"""

test_file ="/content/gdrive/MyDrive/pml-unibuc-2021/test.txt"

df=pd.read_table(test_file,header=None)

test_table = df.rename(columns = {0: 'ID', 1: 'Sentence', 2:'Start_Offset', 3:'End_Offset', 4:'Target Word',5:'NatAnnot', 6:'NonNatAnnot'}, inplace = False)

test_table

vowels =[]
cons =[]
for j in test_table['Target Word'].values:
  returned = calcul_voc(j)
  vowels.append(returned[0])
  cons.append(returned[1])
  
  # print(j)
  # print(calcul_voc(j))

  # Adding the extracted features on my test table
test_table["Vowels"] = vowels
test_table["Cons"] = cons
test_table["LenWord"]= test_table["Target Word"].apply( lambda x: len(x))
test_table["NumSyns"]= test_table["Target Word"].apply( lambda x: len(wn.synsets(x)))
test_table["LenDef"]= test_table["Target Word"].apply( lambda x: len_synset(wn.synsets(x)))
test_table["Capital"]= test_table["Target Word"].apply( lambda x: int(x==x.lower()))
test_table["Type"]= test_table["Target Word"].apply( lambda x: pos_dict[len_hyp(wn.synsets(x))])
# test_table["NumHyo"]= test_table["Target Word"].apply( lambda x: len_hyo(wn.synsets(x)))
# test_table["NumLem"]= test_table["Target Word"].apply( lambda x: len_lem(wn.synsets(x)))

test_table

len(word_vectors_test[0])

"""# **Word2Vec Model**"""

from gensim.models import Word2Vec
import gensim.downloader

from nltk.tokenize import sent_tokenize, word_tokenize
import nltk
nltk.download('punkt')

# Checking the existence of some words which were problematic at some point
train_table[train_table['Target Word'] == 'Hayaleen']['Sentence']

train_table.iloc[400:404]

corpus_text = list(train_table['Sentence'].values)
corpus_text.extend(test_table['Sentence'].values)
# corpus_text.extend(data)
data = []
import string
# Excluding the punctuation and special characters found
exclude = set(string.punctuation)
exclude.add("???")
exclude.add("???")
exclude.add("???")
# iterate through each sentence in the file
for i in corpus_text:
    temp = []
    i = ''.join(ch if ch not in exclude else ' ' for ch in i) 
    # tokenizing the sentence into words
    for j in word_tokenize(i):
      if j == "5bn":
        temp.append("5")
        temp.append("bn")
      elif j=="45pc":
        temp.append("45")
        temp.append("pc")
      else:
        temp.append(j.lower())
    data.append(temp)

import re
def has_numbers(inputString):
  return bool(re.search(r'\d', inputString))

match = re.match(r"([a-z]+)([0-9]+)", '???37.5bn', re.I)
match

for i in train_table['Target Word']:
 
  if(has_numbers(i)):
    match = re.match(r"([a-z]+)([0-9]+)", i, re.I)
    print(i)
    print(match)

data[4440]

# Again, some checking
for i in data:
  if "hayaleen" in i:
    print(i)

# First try of the model
my_model=gensim.models.Word2Vec(data, min_count = 1, size = 100, window = 5, sg = 1)

my_model['bn']

import string
word_vectors=[]  
exclude = set(string.punctuation)
exclude.add("???")
exclude.add("???")
exclude.add("???")
for word in train_table['Target Word'].values:
  word = word.lower()
  #print(word)
  word = ''.join(ch if ch not in exclude else ' ' for ch in word) 
  
  if(len(word.split())<2):
    word = word.strip()
    word_vectors.append(my_model[word])
  else:
    word = word.split()
    value = None
    for w in word:
      if(value is None):
        value = my_model[w]
      else:
        value = value + my_model[w]
    value = value/len(word)
    word_vectors.append(value)

len(word_vectors)

# Trying Decision Tree Regressor on word embeddings from word2vec
X_train, X_test, y_train, y_test = train_test_split(word_vectors, labels.values, test_size=0.33, random_state=42)
from sklearn.svm import SVC
from sklearn import tree
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.metrics import mean_absolute_error
clf = tree.DecisionTreeRegressor(max_depth=50,criterion='absolute_error')
clf = clf.fit(X_train, y_train)
mean_absolute_error(clf.predict(X_test),y_test)

from sklearn.neural_network import MLPRegressor
regr = MLPRegressor(random_state=1,activation='logistic', 
                    max_iter=500,solver='adam',batch_size=48, 
                    learning_rate='adaptive',learning_rate_init=0.001,
                    shuffle=False,tol=1e-5,epsilon=1e-9).fit(X_train, y_train)
mean_absolute_error(regr.predict(X_test),y_test)

"""Also calculating the cross validation scores for Random Forest Regressor and Linear Regressor"""

from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import cross_val_score
regr = RandomForestRegressor(bootstrap=False, max_features= 'log2',
                             n_estimators=1600)
# .fit(X_train, y_train)
                             
# mean_absolute_error(regr.predict(X_test),y_test)
scores = cross_val_score(regr,word_vectors, labels.values, cv=5, scoring="neg_mean_absolute_error")

regr = LinearRegression()
# .fit(X_train, y_train)
                             
# mean_absolute_error(regr.predict(X_test),y_test)
scores_lin = cross_val_score(regr,word_vectors, labels.values, cv=5, scoring="neg_mean_absolute_error")

scores_lin

scores

pred = regr.predict(word_vectors_test)

"""Making submission"""

subm = pd.read_csv("/content/gdrive/MyDrive/pml-unibuc-2021/sample_submission.txt")

subm = pd.read_csv("/content/gdrive/MyDrive/pml-unibuc-2021/sample_submission.txt")
subm["label"] = pred
subm.to_csv("submission1.csv", index=None)

"""# **Neural Networks**"""

import torch
from torch import nn
from torch.utils.data import DataLoader

# Defining the class
class my_class(torch.utils.data.Dataset):
  
  def __init__(self, X, y):
    self.X = torch.from_numpy(X)
    self.y = torch.from_numpy(y)

  def __len__(self):
      return len(self.X)

  def __getitem__(self, i):
      return self.X[i], self.y[i]

# Creating the model class with 4 layers of Linears, ReLU as activation function and 2 layers of Dropout
class MLP(nn.Module):

  def __init__(self):
    super().__init__()
    self.layers = nn.Sequential(
      nn.Linear(207, 600),
      nn.ReLU(),
      nn.Dropout(p=0.2),
      nn.Linear(600, 800),
      nn.ReLU(),
      nn.Dropout(p=0.2),
      nn.Linear(800, 1000),
      nn.ReLU(),
      nn.Linear(1000, 1)    )


  def forward(self, x):
    return self.layers(x)

train_table

my_model=gensim.models.Word2Vec(data, min_count = 1, size = 200, window = 2, sg =1,seed=1,hs=1,cbow_mean=0, negative=5)
# Applying the changes on my model too
import string
import numpy as np
word_vectors=[]  
exclude = set(string.punctuation)
exclude.add("???")
exclude.add("???")
exclude.add("???")
for item in train_table.values:
  #print(item)
  word = item[4]
  word = word.lower()
  #print(item[8:])
  #print(word)
  #break
  word = ''.join(ch if ch not in exclude else ' ' for ch in word) 
  
  if(len(word.split())<2):
    word = word.strip()
    value = np.append(np.float32(item[8:]),my_model[word])
    word_vectors.append(value)
  else:
    word = word.split()
    value = None
    for w in word:
      if(value is None):
        value = my_model[w]
      else:
        value = value + my_model[w]
    value = value/len(word)
    #print(item[8:11])
    value = np.append(np.float32(item[8:]),value)
    word_vectors.append(np.array(value))




X = numpy.array(word_vectors)
y = train_table['Prob'].values

import string
# Applying changes on test word vectors as well
word_vectors_test=[]  
exclude = set(string.punctuation)
exclude.add("???")
exclude.add("???")
exclude.add("???")
for item in test_table.values:
  word = item[4].lower()
  word = ''.join(ch if ch not in exclude else ' ' for ch in word) 
  if(len(word.split())<2):
    word = word.strip()
    word_vectors_test.append(np.append(np.float32(item[7:]),my_model[word]))
  else:
    word = word.split()
    value = None
    for w in word:
      if(value is None):
        value = my_model[w]
      else:
        value = value + my_model[w]
    value = value/len(word)
    value = np.append(np.float32(item[7:]),value)
    word_vectors_test.append(value)

len(X[0])

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Creating train dataloader
dataset = my_class(np.array(X_train),np.array(y_train))
train_loader = DataLoader(dataset, batch_size=1, shuffle=True)

# Creating validation dataloader
dataset_valid = my_class(np.array(X_test),np.array(y_test))
valid_loader = DataLoader(dataset_valid, batch_size=1, shuffle=False)

# Creating test dataloader
dataset_test = my_class(numpy.array(word_vectors_test),numpy.ones(len(word_vectors_test)))
test_loader = DataLoader(dataset_test, batch_size=1, shuffle=False)

# Initialize the MLP
mlp = MLP().cuda()

# Define the loss function and optimizer
loss_function = nn.L1Loss()
optimizer = torch.optim.Adam(mlp.parameters(), lr=1e-4)
lr_scheduler = torch.optim.lr_scheduler.MultiStepLR(optimizer,[4,11],0.6,verbose=True)

# Defining the training function which saves the best score for the future submission
def train_function(epochs: int, train_loader: DataLoader, valid_loader: DataLoader):
  best_error = 1
  best_sub = []
  for e in range(epochs):
    mlp.train()
    for value, label in train_loader:
      value = value.cuda()
      label = label.cuda()

      optimizer.zero_grad()
      out = mlp(value)
      loss = loss_function(out.squeeze(1),label.float())
      loss.backward()
      optimizer.step()
      
    print("Loss-ul la finalul epocii {} are valoarea {}".format(e, loss.item()))
    lista=[]
    listat=[]
    lkista=[]
    lkistat=[]
    # for vt,lt in train_loader:
    #   vt=vt.cuda()
    #   # l=l.cuda()
    #   hmm = mlp(vt)
    #   listat.append(hmm.detach().cpu().numpy())
      
    #   lkistat.append(lt.numpy())
    mlp.eval()
    with torch.no_grad():

      for v,l in valid_loader:
        v=v.cuda()
        # l=l.cuda()
        hm = mlp(v)
        lista.append(hm.detach().cpu().numpy())
      
        lkista.append(l.numpy())
    # print(lista)
    # print(lkista)
    # print("train err: ", mean_absolute_error(numpy.vstack(listat),numpy.vstack(lkistat)))
    print("valid err: ", mean_absolute_error(numpy.vstack(lista),numpy.vstack(lkista)))
    error = mean_absolute_error(numpy.vstack(lista),numpy.vstack(lkista))
    # Creating plots for validation and test distribution
    plt.title("validation distribution")
    plt.hist(numpy.vstack(lista), bins=5)
    plt.show()
    listaaa=[]
    mlp.eval()
    with torch.no_grad():
      for val,lab in test_loader:
        val = val.cuda()
        #print(val[0][:8])
        out=mlp(val)
        #print(out)
        listaaa.append(out.detach().cpu().numpy())
    plt.title("test distribution")
    plt.hist(numpy.vstack(listaaa), bins=5)
    plt.show()
    if best_error > error:
      best_sub=numpy.vstack(listaaa)
      best_error=error
    lr_scheduler.step()
  print(best_error)
  return best_sub

# for a,b in valid_loader:
#   hh=mlp(a.cuda())
#   print(hh)
#   break

best_sub = train_function(15,train_loader,valid_loader)

subm = pd.read_csv("/content/gdrive/MyDrive/pml-unibuc-2021/sample_submission.txt")
# subm["label"] = pred
# subm.to_csv("submission1.csv", index=None)

best_sub

listaaa=[]
mlp.eval()
with torch.no_grad():
  for val,lab in test_loader:
    val = val.cuda()
    #print(val[0][:8])
    out=mlp(val)
    print(out)
    listaaa.append(out.detach().cpu().numpy())

listaaa

listaaa=numpy.vstack(listaaa)

plt.hist(best_sub, bins=5)
plt.show()

subm["label"] = best_sub

subm.loc[subm['label'] <0,'label'] = 0

subm.loc[subm['label'] >1,'label'] = 1

subm['label']

subm.to_csv('submisie11.csv', index=False)