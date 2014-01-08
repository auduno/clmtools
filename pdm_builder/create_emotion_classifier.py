import pickle, json, os, numpy, math
from buildlib import preprocess, config
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn import cross_validation
from numpy import row_stack, any, isnan, sum, diag, cov, mean, dot, trace
from numpy.linalg import qr

data_folder = config.data_folder

emotions = {}

# load emotions
files = os.listdir( os.path.join(data_folder,"emotions/") )
for f in files:
  emotion = f.split(".")[0]
  emotions[emotion] = []
  fi = open( os.path.join(data_folder,"emotions/",f),"r")
  for lines in fi:
    emotions[emotion].append(lines.strip()[0:-4]+".bmp")
    emotions[emotion].append(lines.strip()[0:-4]+"_m.bmp")
  fi.close()

# preprocess data
data_pca, data_patches, meanshape, cropsize = preprocess.preprocess(config.annotations, mirror = True)

#dp = {'data_pca' : data_pca, 'data_patches' : data_patches, 'meanshape' : meanshape, 'cropsize' : cropsize}
#fi = open("out.data", "w")
#pickle.dump(dp, fi)
#fi.close()

#fi = open("out.data", "r")
#data = pickle.load(fi)
#fi.close()
#data_pca = data['data_pca']
#data_patches = data['data_patches']
#meanshape = data['meanshape']
#cropsize = data['cropsize']

# build pca model
data = [d.flatten() for d in data_pca.values() if not any(isnan(d))]
datamatrix = row_stack(data)
pca = PCA(n_components=20)
pca.fit(datamatrix)

labels = []
params = []

# get all points and transform
# insert into positive and negative labels
for k in data_pca.keys():
  labelvec = []
  for e in emotions.values():
    if k in e:
      labelvec.append(1.0)
    else:
      labelvec.append(0.0)
  labels.append(labelvec)
  #params = numpy.vstack((params, pca.transform(data_pca[k].flatten())))
  #import pdb;pdb.set_trace()
  params.append(pca.transform(data_pca[k].flatten())[0,2:])
  #params.append(pca.transform(data_pca[k].flatten()))

params = row_stack(params)
labels = row_stack(labels)

# do random forest classifier
#clf = RandomForestClassifier()
#scores = cross_validation.cross_val_score(clf, params, labels, cv=5)

# do logistic regression classifier?
clf = LogisticRegression(class_weight = 'auto', penalty = 'l2')
#scores = cross_validation.cross_val_score(clf, params, labels, cv=5)
#print scores

of = open("emotion_classifier.js","w")
of.write("var classifier = {")

for i,e in enumerate(emotions.keys()):
  clf.fit(params, labels[:,i])
  
  of.write('"'+e+'" : {')
  of.write('"bias" : '+str(clf.intercept_[0])+",")
  of.write('"coefficients" : '+str(clf.coef_.flatten().tolist())+",")
  of.write('},')

of.write("};")
of.close()