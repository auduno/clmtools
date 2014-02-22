import pickle, json, os, numpy, math
from buildlib import preprocess, config
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn import cross_validation
from numpy import row_stack, any, isnan, sum, diag, cov, mean, dot, trace

data_folder = config.data_folder

# create some needed folders
for folder in ["cropped", "pcropped", "svmImages"]:
	if not os.path.exists(os.path.join(config.data_folder, folder)):
		os.makedirs(os.path.join(config.data_folder, folder))

files = {
	"angry" : "angry.csv",
	"disgusted" : "disgusted.csv",
	"fear" : "fear.csv",
	"happy" : "happy.csv",
	"sad" : "sad.csv",
	"surprised" : "surprised.csv",
}

classes = {}

# load classes
for c, f in files.iteritems():
	classes[c] = []
	fi = open( os.path.join(data_folder,"classes/",f),"r")
	for lines in fi:
		filename = os.path.splitext(lines.strip())[0]
		classes[c].append(filename)
		classes[c].append(filename+"_m")
	fi.close()

# preprocess data
data_pca, data_patches, meanshape, cropsize = preprocess.preprocess(config.annotations, mirror = True, crop=True)
#dp = {'data_pca' : data_pca, 'meanshape' : meanshape}
#fi = open("out2.data", "w")
#pickle.dump(dp, fi)
#fi.close()

#fi = open("out2.data", "r")
#data = pickle.load(fi)
#fi.close()
#data_pca = data['data_pca']
#meanshape = data['meanshape']

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
	filename = os.path.splitext(k)[0]
	labelvec = []
	for c in classes.values():
		if filename in c:
			labelvec.append(1.0)
		else:
			labelvec.append(0.0)
	labels.append(labelvec)
	#params = numpy.vstack((params, pca.transform(data_pca[k].flatten())))
	params.append(pca.transform(data_pca[k].flatten())[0,2:])
	#params.append(pca.transform(data_pca[k].flatten()))

params = row_stack(params)
labels = row_stack(labels)

# do random forest classifier
#clf = RandomForestClassifier()
#scores = cross_validation.cross_val_score(clf, params, labels, cv=5)

# do logistic regression classifier
clf = LogisticRegression(class_weight = 'auto', penalty = 'l2')
#scores = cross_validation.cross_val_score(clf, params, labels, cv=5)
#print scores

of = open("classifier.js","w")
of.write("var classifier = {\n")

for i,c in enumerate(classes.keys()):
	if sum(labels[:,i]) < 10.0:
		print "Class '%s' had %d positive training samples. More positive samples needed for training. Ignoring this class." % (c, sum(labels[:,i]))
		continue
	print "Training classifier for '%s' with %d positive training." % (c, sum(labels[:,i]))
	clf.fit(params, labels[:,i])
	
	of.write('\t"'+c+'" : {')
	of.write('"bias" : '+str(clf.intercept_[0])+",")
	of.write('"coefficients" : '+str(clf.coef_.flatten().tolist())+",")
	of.write('},\n')

of.write("};")
of.close()

import shutil
for folder in ["cropped", "pcropped", "svmImages"]:
  if os.path.exists(os.path.join(config.data_folder, folder)):
    shutil.rmtree(os.path.join(config.data_folder, folder))