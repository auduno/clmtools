import config, random, numpy, pickle, math
from PIL import Image
from numpy import array, sqrt, square, fft, mean, zeros
from numpy.linalg import norm
from numpy.ma import conjugate
from os.path import isfile, join

data_folder = config.data_folder
num_patches = config.num_patches
patch_size = config.patch_size

def build_patches(data):
	filters = []
	for r in range(0, num_patches):
		print "training patch:"+str(r)
		images = []
		targetImages = []
		
		# load positive examples
		i = 0
		for filename, values in data.iteritems():
			im = Image.open( join(data_folder, "cropped/", filename), "r")
			
			# convert image to grayscale
			im = im.convert("L")
			
			#generate random offset to target to generate better filters
			xof = random.randint(-3,3)
			yof = random.randint(-3,3)
			
			if not numpy.isnan(values[r][0]):
				# TODO : check that there is not missing data:
		
				points = values[r]+(numpy.array(im.size)/2)
				points = numpy.around(points)
				points = points.astype(numpy.uint8)
				
				left = points[0]-(patch_size/2)-xof
				top = points[1]-(patch_size/2)-yof
				nux = points[0]-left
				nuy = points[1]-top
				
				p_crop = im.crop((left,top,left+patch_size,top+patch_size))
				Image.fromarray(numpy.asarray(p_crop).astype('int')).convert("L").save( join(data_folder, "pcropped/", "mosse"+filename+".bmp") )
				images.append(numpy.array(p_crop))
				
				# create target images
				targetImage = array([0.]*(patch_size*patch_size)).reshape((patch_size,patch_size))
				for xr in range(0,patch_size):
					for yr in range(0,patch_size):
						targetImage[yr,xr] = math.exp(-(((xr-nux)*(xr-nux))+((yr-nuy)*(yr-nuy)))/(0.5*0.5))
				#Image.fromarray((targetImage*255).astype('int')).convert("L").save("test_target.bmp")
				targetImages.append(targetImage)
							
			if i % 1000 == 0:
				print i
			i += 1
		
		# preprocess
		images = [im.astype(numpy.uint16) for im in images]
		images = [numpy.log(im+1) for im in images]
		# normalize
		images = [im-mean(im) for im in images]
		images = [im/norm(im) for im in images]
		# cosine windows
		images = [cosine_window(im) for im in images]
		
		# fft of images
		images = [fft.fft2(im) for im in images]
		targetImages = [fft.fft2(ti) for ti in targetImages]

		print "calculating filter"
		# calculate filter
		top = numpy.zeros((patch_size, patch_size))
		top = top.astype('complex')
		bottom = numpy.zeros((patch_size, patch_size))
		bottom = bottom.astype('complex')
		for ir in range(len(images)):
			if numpy.any(numpy.isnan(targetImages[ir])) or numpy.any(numpy.isnan(conjugate(images[ir]))) or numpy.any(numpy.isnan(images[ir])):
				import pdb;pdb.set_trace()
			top += targetImages[ir]*conjugate(images[ir])
			bottom += images[ir]*conjugate(images[ir])
				
		filter = top/bottom 
		
		# optionally store filters as normalized images, for validation
		filres = fft.ifft2(filter)
		fil = filres.real
		minf = numpy.min(fil)
		fil -= minf
		maxf = numpy.max(fil)
		fil *= (255/maxf)
		fil = numpy.floor(fil)
		Image.fromarray(fil.astype('int')).convert("L").save( join(data_folder, "svmImages/", "svm"+str(r)+".bmp") )
		#
		
		#fi = open("./svmFilters/filter"+str(r)+".pickle", "w")
		#pickle.dump(clf.coef_, fi)
		#fi.close()
		
		filter_real = map(lambda x: x.real, filter.flatten().tolist())
		filter_imag = map(lambda x: x.imag, filter.flatten().tolist())
		filter = [filter_real, filter_imag]
		
		filters.append(filter)
	
	# output for standard model:
	#filteroutput = [filters[f][r] for r in range(0, patch_size*patch_size) for f in range(0, num_patches)]
	filteroutput = filters
	# output result as dictionary with entries
	patchModel = {}
	patchModel['patchSize'] = [patch_size, patch_size]
	patchModel['weights'] = filteroutput
	patchModel['numPatches'] = num_patches
	patchModel['patchType'] = 'MOSSE'
	
	return patchModel

def cosine_window(ar):
	halfWidth = (patch_size)/2.
	halfHeight = (patch_size)/2.
	newArray = zeros(ar.shape)
	for i in range(0, patch_size):
		for j in range(0, patch_size):
			x = i-halfWidth
			y = j-halfHeight
			cww = math.sin((math.pi*i)/(patch_size-1))
			cwh = math.sin((math.pi*j)/(patch_size-1))
			min(cww,cwh)
			newArray[j,i] = min(cww,cwh)*ar[j,i]
	return newArray
