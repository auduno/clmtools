import numpy, pickle, random, os, config

from sklearn.svm import SVR, SVC
from sklearn.linear_model import LogisticRegression
from PIL import Image
from numpy import array, sqrt, square
from numpy.linalg import norm
from os import listdir
from os.path import isfile, join
from scipy.ndimage.filters import sobel

data_folder = config.data_folder
num_patches = config.num_patches
patch_size = config.patch_size

def build_patches(data, c_value=None, gradient=False):
	filters = []
	
	if gradient:
		patchcrop = [(patch_size+1)/2, (patch_size+3)/2]
		new_patch_size = patch_size+2
	else:
		patchcrop = [(patch_size-1)/2, (patch_size+1)/2]
		new_patch_size = patch_size
	
	for r in range(0, num_patches):
		print "training patch:"+str(r)
		positives = []
		negatives = []
		
		# load positive examples
		i = 0
		for filename, values in data.iteritems():
			im = Image.open( join(data_folder, "cropped/", filename) , "r")
			mask = Image.open( join(data_folder, "cropped/", filename[:-4]+"_mask.bmp") , "r")
			
			# convert image to grayscale
			im = im.convert("L")
			if not numpy.isnan(values[r][0]):
				# TODO : check that there is not missing data:
				points = numpy.around(values[r]+(numpy.array(im.size)/2))
				points = points.astype(numpy.uint8)
				# check whether cropping goes outside image
				m_crop = mask.crop((points[0]-patchcrop[0], points[1]-patchcrop[0], points[0]+patchcrop[1], points[1]+patchcrop[1]))
				m_crop = numpy.array(m_crop)
				if not numpy.all(m_crop == 255):
					print "cropping of patch "+str(r)+" in image '"+filename+"' was outside original image bounds. Dropping this patch from training."
				else:
					p_crop = im.crop((points[0]-patchcrop[0], points[1]-patchcrop[0], points[0]+patchcrop[1], points[1]+patchcrop[1] ))
					if gradient:
						p_crop = numpy.array(p_crop).astype('int32')
						dx = sobel(p_crop, axis=0, mode="constant")
						dy = sobel(p_crop, axis=1, mode="constant")
						p_crop = numpy.hypot(dx, dy)
						p_crop = p_crop[1:patch_size+1, 1:patch_size+1]
						if not numpy.max(p_crop) == 0.:
							p_crop *= 255.0 / numpy.max(p_crop)
						#Image.fromarray(p_crop.astype('uint8')).save("./pcropped/0svm2"+filename+".bmp")
					else:	
						#p_crop.save("./pcropped/svm"+filename)
						p_crop = numpy.array(p_crop)
					positives.append(p_crop.flatten())
				
				# get negative examples from randomization
				for nr in range(0,10):
					rpoints = random_coord(im.size, new_patch_size, points)
					# check whether cropping goes outside image
					m_crop = mask.crop((rpoints[0]-patchcrop[0],rpoints[1]-patchcrop[0],rpoints[0]+patchcrop[1],rpoints[1]+patchcrop[1]))
					m_crop = numpy.array(m_crop)
					if not numpy.all(m_crop == 255):
						pass
						#print "cropping of a negative for patch "+str(r)+" was outside original image bounds. Dropping this patch from training."
					else:
						p_crop = im.crop((rpoints[0]-patchcrop[0], rpoints[1]-patchcrop[0], rpoints[0]+patchcrop[1], rpoints[1]+patchcrop[1]))
						if gradient:
							#
							p_crop = numpy.array(p_crop).astype('int32')
							dx = sobel(p_crop, 0)
							dy = sobel(p_crop, 1)
							p_crop = numpy.hypot(dx, dy)
							p_crop = p_crop[1:patch_size+1, 1:patch_size+1]
							#p_crop = p_crop.crop((1, 1, patch_size+2, patch_size+1))
							if not numpy.max(p_crop) == 0.:
								p_crop *= 255.0 / numpy.max(p_crop)
						else:
							p_crop = numpy.array(p_crop)
						negatives.append(p_crop.flatten())
			
			if i % 1000 == 0:
				print i
			i += 1
		
		# get negative examples from landscape images
		negfiles = [f for f in listdir( join(data_folder, "negatives/")  ) if isfile( join(data_folder, "negatives/",f) )]
		for filename in negfiles:
			im = Image.open( join(data_folder, "negatives/", filename) , "r")
			im = im.convert("L")
			diff = patchcrop[0]
			for nr in range(0,100):
				
				x = random.randint(1+diff, im.size[0]-diff)
				y = random.randint(1+diff, im.size[1]-diff)
				rpoints = array([x,y])
				p_crop = im.crop((rpoints[0]-patchcrop[0], rpoints[1]-patchcrop[0],rpoints[0]+patchcrop[1],rpoints[1]+patchcrop[1]
				if gradient:
					p_crop = numpy.array(p_crop).astype('int32')
					dx = sobel(p_crop, 0)
					dy = sobel(p_crop, 1)
					p_crop = numpy.hypot(dx, dy)
					p_crop = p_crop[1:patch_size+1, 1:patch_size+1]
					#p_crop = p_crop.crop((1, 1, patch_size+1, patch_size+1))
					if not numpy.max(p_crop) == 0.:
						p_crop *= 255.0 / numpy.max(p_crop)
				else:
					p_crop = numpy.array(p_crop)
				negatives.append(p_crop.flatten())
		
		# maybe use some other nature photos for negative examples?
		
		# maybe use uniform images for negative examples?
		
		# normalize image data to 0,1 interval
		positives = [normalize(p) for p in positives]
		negatives = [normalize(n) for n in negatives]
		
		labels = [1.0 for p in positives]
		labels.extend([-1.0 for n in negatives])
		labels = numpy.array(labels)
		features = [p.flatten() for p in positives]
		features.extend([n.flatten() for n in negatives])
		features = numpy.vstack(features)

		# since we have more negative samples than positive samples, we need to balance the set
		#weights = []
		#negweight = float(len(positives))/float(len(negatives))
		#weights = {1. : 1., -1. : negweight}
		
		# train svm
		
		# use grid search/cross-validation to set C, epsilon parameter on each patch?
		#arr = numpy.arange(features.shape[0])
		#numpy.random.shuffle(arr)
		#from sklearn.grid_search import GridSearchCV
		#from sklearn.metrics import mean_squared_error
		##clfg = GridSearchCV(LogisticRegression(penalty='L2', dual=False), {'C':[0.00001, 0.0000001, 0.000000001]}, score_func=mean_squared_error, verbose=100)
		#clfg = GridSearchCV(SVR(kernel="linear"), {'C':[0.1, 0.0001, 0.00000001]}, score_func=mean_squared_error, verbose=100)
		#clfg.fit(features[arr,:], labels[arr])
		#import pdb;pdb.set_trace()
		# end grid search
		
		#clf = LogisticRegression(penalty='L2', dual=False, C=0.00001)
		clf = SVR(C=c_value, kernel="linear")
		#clf = SVR(C=c_value, epsilon=0.9, kernel="linear")
		
		#clf = clfg.best_estimator_
		clf.fit(features, labels)
		
		# optionally store filters as normalized images, for validation
		#coefficients = clf.coef_
		#coefficients = (normalize(coefficients)*255.).astype("uint8")
		#coefficients = coefficients.reshape((patch_size,patch_size))
		#coefImg = Image.fromarray(coefficients)
		#coefImg.save( join(data_folder, "svmImages/", "svm"+str(r)+".bmp") )
		
		print "bias : "+str(clf.intercept_[0])
		
		#errors = []
		#import math
		#for f in range(0,len(features)):
			#score = numpy.sum(features[f]*clf.coef_) + clf.intercept_
		#	score = clf.predict(features[f])
		#	errors.append(math.sqrt((labels[f]-score)**2))
		#print "mse:"+str(numpy.mean(errors))
		#import pdb;pdb.set_trace()
		
		#fi = open("./svmFilters/filter"+str(r)+".pickle", "w")
		#pickle.dump(clf.coef_, fi)
		#fi.close()
		
		#filters.append(clf.coef_.transpose().flatten().tolist())
		filters.append(clf.coef_.flatten().tolist())
	
	# output for standard model:
	filteroutput = [[-filters[f][r] for r in range(0, patch_size*patch_size)] for f in range(0, num_patches)]
	
	# output result as dictionary with entries
	patchModel = {}
	patchModel['patchSize'] = [patch_size, patch_size]
	patchModel['weights'] = filteroutput
	patchModel['numPatches'] = num_patches
	patchModel['patchType'] = 'SVM'
	
	return patchModel
	
def random_coord(size, patchsize, pos_coord):
	# get random value, multiply by size
	# ensure that it's not larger than patchsize and more than 5 pixels away from true point
	x_size = size[0]
	y_size = size[1]
	#diff = ((patchsize-1)/2)
	diff = 2
	over = True
	while over:
		x = random.randint(1+diff, x_size-diff)
		y = random.randint(1+diff, y_size-diff)
		rpos = array([x,y])

		distance = norm(rpos-pos_coord)
		if distance >= diff and distance < 15:
			over = False
	return rpos

def normalize(data):
	max_data = numpy.max(data)
	min_data = numpy.min(data)
	data = data.astype(numpy.float32)
	if max_data-min_data == 0:
		normalized_data = numpy.zeros(data.shape)
	else:
		normalized_data = (data-min_data)/(max_data-min_data)
	return normalized_data