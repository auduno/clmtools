import numpy, pickle, random, os, config

from numpy import array, sqrt, square
from numpy.linalg import norm
from os import listdir
from os.path import isfile, join
from PIL import Image
from scipy.ndimage.filters import sobel
from sklearn.svm import SVR, SVC
from sklearn.linear_model import LogisticRegression

data_folder = config.data_folder
num_patches = config.num_patches
patch_size = config.patch_size

def build_patches(data, gradient=True, lbp=True, weights=None, optimize_params=False):
	filters = []
	grad_filters = []
	lbp_filters = []
	raw_bias = []
	grad_bias = []
	lbp_bias = []
	
	#if gradient or lbp:
	grad_patchcrop = [(patch_size+1)/2, (patch_size+3)/2]
	patchcrop = [(patch_size-1)/2, (patch_size+1)/2]
	
	for r in range(0, num_patches):
		print "training patch:"+str(r)
		
		positives = []
		negatives = []
		grad_positives = []
		grad_negatives = []
		lbp_positives = []
		lbp_negatives = []
		weighting = []
		
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
				m_crop = mask.crop((points[0]-grad_patchcrop[0], points[1]-grad_patchcrop[0], points[0]+grad_patchcrop[1], points[1]+grad_patchcrop[1]))
				m_crop = numpy.array(m_crop)
				if not numpy.all(m_crop == 255):
					print "cropping of patch "+str(r)+" in image '"+filename+"' was outside original image bounds. Dropping this patch from training."
				else:
					if weights:
						if r in weights and filename in weights[r]:
							weighting.append(True)
						else:
							weighting.append(False)
					if gradient:
						grad_crop = getGradientCrop(im, points)
						#Image.fromarray(grad_crop.astype('uint8')).save( join(data_folder, "pcropped/", "grad_"+filename) )
						grad_positives.append(grad_crop.flatten())
					if lbp:
						lbp_crop = getLBPCrop(im, points)
						#Image.fromarray(lbp_crop.astype('uint8')).save( join(data_folder, "pcropped/", "lbp_"+filename) )
						lbp_positives.append(lbp_crop.flatten())
					raw_crop = getRawCrop(im, points)
					positives.append(raw_crop.flatten())
				# get negative examples from randomization
				for nr in range(0,10):
					rpoints = random_coord(im.size, patch_size+2, points)
					# check whether cropping goes outside image
					m_crop = mask.crop((rpoints[0]-grad_patchcrop[0], rpoints[1]-grad_patchcrop[0], rpoints[0]+grad_patchcrop[1], rpoints[1]+grad_patchcrop[1]))
					m_crop = numpy.array(m_crop)
					if not numpy.all(m_crop == 255):
						pass
					else:
						if gradient:
							grad_crop = getGradientCrop(im, rpoints)
							#Image.fromarray(grad_crop.astype('uint8')).save( join(data_folder, "pcropped/", "grad_neg_"+filename) )	
							grad_negatives.append(grad_crop.flatten())
						if lbp:
							lbp_crop = getLBPCrop(im, rpoints)
							lbp_negatives.append(lbp_crop.flatten())
						raw_crop = getRawCrop(im, rpoints)
						negatives.append(raw_crop.flatten())
			
			if i % 1000 == 0:
				print i
			i += 1
		
		# get negative examples from landscape images
		negfiles = [f for f in listdir( join(data_folder, "negatives/")	 ) if isfile( join(data_folder, "negatives/",f) )]
		for filename in negfiles:
			im = Image.open( join(data_folder, "negatives/", filename) , "r")
			im = im.convert("L")
			diff = grad_patchcrop[0]
			for nr in range(0,100):
				x = random.randint(1+diff, im.size[0]-diff)
				y = random.randint(1+diff, im.size[1]-diff)
				rpoints = array([x,y])
				if gradient:
					grad_crop = getGradientCrop(im, rpoints)
					#Image.fromarray(grad_crop.astype('uint8')).save( join(data_folder, "pcropped/", "grad_neg_"+filename) )	
					grad_negatives.append(grad_crop.flatten())
				if lbp:
					lbp_crop = getLBPCrop(im, rpoints)
					lbp_negatives.append(lbp_crop.flatten())
				raw_crop = getRawCrop(im, rpoints)
				negatives.append(raw_crop.flatten())
		
		# maybe use some other nature photos for negative examples?
		
		# maybe use uniform images for negative examples?
		
		# normalize image data to 0,1 interval
		positives = [normalize(p) for p in positives]
		negatives = [normalize(n) for n in negatives]
		if gradient:
			grad_positives = [normalize(p) for p in grad_positives]
			grad_negatives = [normalize(n) for n in grad_negatives]
		if lbp:
			lbp_positives = [normalize(p) for p in lbp_positives]
			lbp_negatives = [normalize(n) for n in lbp_negatives]
		
		labels = [1.0 for p in positives]
		labels.extend([-1.0 for n in negatives])
		labels = numpy.array(labels)
		features = [p.flatten() for p in positives]
		features.extend([n.flatten() for n in negatives])
		features = numpy.vstack(features)
		if gradient:
			grad_features = [p.flatten() for p in grad_positives]
			grad_features.extend([n.flatten() for n in grad_negatives])
			grad_features = numpy.vstack(grad_features)
		if lbp:
			lbp_features = [p.flatten() for p in lbp_positives]
			lbp_features.extend([n.flatten() for n in lbp_negatives])
			lbp_features = numpy.vstack(lbp_features)
		
		if weights:
			# weighting
			num_positives = float(len(positives))
			num_weighted = float(sum(weighting))
			sample_weight = []
			if num_weighted > 0:
				for p in range(len(positives)):
					if weighting[p]:
						sample_weight.append(num_positives/(2*num_weighted))
					else:
						sample_weight.append(num_positives/(2*(num_positives-num_weighted)))
				for n in range(len(negatives)):
					sample_weight.append(1.)
			else:
				sample_weight = [1.0]*(len(positives)+len(negatives))
		else:
			sample_weight = [1.0]*(len(positives)+len(negatives))
		
		if optimize_params:
			# use grid search/cross-validation to set C, epsilon parameter on each patch?
			arr = numpy.arange(features.shape[0])
			numpy.random.shuffle(arr)
			from sklearn.grid_search import GridSearchCV
			from sklearn.metrics import mean_squared_error
			clfg = GridSearchCV(SVR(kernel="linear"), {'C':[0.1], 'epsilon' : [0.4, 0.3, 0.2, 0.1]}, loss_func=mean_squared_error, verbose=100)
			clfg.fit(features[arr,:], labels[arr])
			print clfg.best_params_
			clf = clfg.best_estimator_
		else:
			clf = SVR(C=0.1, epsilon=0.3, kernel="linear")
		#clf = LogisticRegression(penalty='L2', dual=False, C=0.00001)

		clf.fit(features, labels, sample_weight=sample_weight)
		
		# store filters as normalized images, for validation
		#saveAsImage(clf.coef_, join(data_folder, "svmImages/", "raw"+str(r)+".bmp"))
		
		filters.append(clf.coef_.flatten().tolist())
		raw_bias.append(clf.intercept_[0])

		if gradient:
			if optimize_params:
				clfg = GridSearchCV(SVR(kernel="linear"), {'C':[0.1], 'epsilon' : [0.4, 0.3, 0.2, 0.1]}, loss_func=mean_squared_error, verbose=100)
				clfg.fit(grad_features[arr,:], labels[arr])
				print "gradient best params"+str(clfg.best_params_)
				clf = clfg.best_estimator_
			else:
				clf = SVR(C=0.1, epsilon=0.3, kernel="linear")
			clf.fit(grad_features, labels, sample_weight=sample_weight)
			grad_filters.append(clf.coef_.flatten().tolist())
			grad_bias.append(clf.intercept_[0])
			
			#saveAsImage(clf.coef_, join(data_folder, "svmImages/", "grad"+str(r)+".bmp"))
		if lbp:
			if optimize_params:
				clfg = GridSearchCV(SVR(kernel="linear"), {'C':[0.1], 'epsilon' : [0.4, 0.3, 0.2, 0.1]}, loss_func=mean_squared_error, verbose=100)
				clfg.fit(lbp_features[arr,:], labels[arr])
				print "lbp best params"+str(clfg.best_params_)
				clf = clfg.best_estimator_
			else:
				clf = SVR(C=0.1, epsilon=0.3, kernel="linear")
			clf.fit(lbp_features, labels, sample_weight=sample_weight)
			lbp_filters.append(clf.coef_.flatten().tolist())
			lbp_bias.append(clf.intercept_[0])
			
			#saveAsImage(clf.coef_, join(data_folder, "svmImages/", "lbp"+str(r)+".bmp"))
	
	# output for standard model:
	filteroutput = {
		'raw' : [[-filters[f][r] for r in range(0, patch_size*patch_size)] for f in range(0, num_patches)],
	}
	biasoutput = {
		'raw' : raw_bias
	}
	if gradient:
		filteroutput['sobel'] = [[-grad_filters[f][r] for r in range(0, patch_size*patch_size)] for f in range(0, num_patches)]
		biasoutput['sobel'] = grad_bias
	if lbp:
		filteroutput['lbp'] = [[-lbp_filters[f][r] for r in range(0, patch_size*patch_size)] for f in range(0, num_patches)]
		biasoutput['lbp'] = lbp_bias
	
	# output result as dictionary with entries
	patchModel = {}
	patchModel['patchSize'] = [patch_size, patch_size]
	patchModel['weights'] = filteroutput
	patchModel['bias'] = biasoutput
	patchModel['numPatches'] = num_patches
	patchModel['patchType'] = 'SVM'
	
	return patchModel

def getGradientCrop(image, point):
	grad_crop = image.crop((point[0]-(patch_size+1)/2, point[1]-(patch_size+1)/2, point[0]+(patch_size+3)/2, point[1]+(patch_size+3)/2))
	grad_crop = numpy.array(grad_crop).astype('float32')
	dx = sobel(grad_crop, 0)/4.0
	dy = sobel(grad_crop, 1)/4.0
	grad_crop = numpy.hypot(dx, dy)
	grad_crop = grad_crop[1:patch_size+1, 1:patch_size+1]
	return grad_crop

def getLBPCrop(image, point):
	lbp_crop = image.crop((point[0]-(patch_size+1)/2, point[1]-(patch_size+1)/2, point[0]+(patch_size+3)/2, point[1]+(patch_size+3)/2))
	lbp_crop = local_binary_pattern(lbp_crop)
	return lbp_crop

def getRawCrop(image, point):
	raw_crop = image.crop((point[0]-(patch_size-1)/2, point[1]-(patch_size-1)/2, point[0]+(patch_size+1)/2, point[1]+(patch_size+1)/2))
	raw_crop = numpy.array(raw_crop)
	return raw_crop

def saveAsImage(coef, filename):
	coefficients = (normalize(coef)*255.).astype("uint8")
	coefficients = coefficients.reshape((patch_size,patch_size))
	coefImg = Image.fromarray(coefficients)
	coefImg.save( filename )

def local_binary_pattern(img):
	np_crop = numpy.array(img).astype('int32')
	npi_crop = numpy.zeros(np_crop.shape)
	for i in range(1,np_crop.shape[0]-1):
		for j in range(1,np_crop.shape[1]-1):
			# get all edges
			topLeft = np_crop[i-1,j-1]
			topMid = np_crop[i-1,j]
			topRight = np_crop[i-1,j+1]
			midLeft = np_crop[i,j-1]
			midMid = np_crop[i,j]
			midRight = np_crop[i,j+1]
			bottomLeft = np_crop[i+1,j-1]
			bottomMid = np_crop[i+1,j]
			bottomRight = np_crop[i+1,j+1]
			entry = max(numpy.sign(midRight-midMid),0)*1 + max(numpy.sign(topRight-midMid),0)*2 + \
				max(numpy.sign(topMid-midMid),0)*4 + max(numpy.sign(topLeft-midMid),0)*8 + max(numpy.sign(midLeft-midMid),0)*16 + \
				max(numpy.sign(bottomLeft-midMid),0)*32 + max(numpy.sign(bottomMid-midMid),0)*64 + max(numpy.sign(bottomRight-midMid),0)*128
			npi_crop[i,j] = entry
	npi_crop = npi_crop[1:patch_size+1, 1:patch_size+1]
	
	return npi_crop

def random_coord(size, patchsize, pos_coord):
	# get random value, multiply by size
	# ensure that it's not larger than patchsize and more than 5 pixels away from true point
	x_size = size[0]
	y_size = size[1]
	diff = ((patchsize-1)/2)
	#diff = 2
	over = True
	while over:
		x = random.randint(1+diff, x_size-diff)
		y = random.randint(1+diff, y_size-diff)
		rpos = array([x,y])
		#distance = norm(rpos-pos_coord)
		#if distance >= diff and distance < 15:
		if norm(rpos-pos_coord) >= diff:
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