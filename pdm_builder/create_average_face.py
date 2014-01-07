import numpy as np
from buildlib import preprocess
import pickle, skimage
from skimage.transform import PiecewiseAffineTransform, warp
from skimage.io import imread, Image, imsave
import config

data_pca, data_patches, meanshape, cropsize = preprocess.preprocess(config.annotations, mirror = True)

dp = {'data_pca' : data_pca, 'data_patches' : data_patches, 'meanshape' : meanshape, 'cropsize' : cropsize}
fi = open("out.data", "w")
pickle.dump(dp, fi)
fi.close()

#fi = open("out.data", "r")
#data = pickle.load(fi)
#fi.close()
#data_pca = data['data_pca']
#data_patches = data['data_patches']
#meanshape = data['meanshape']
#cropsize = data['cropsize']

# get meanshape
mean = [np.mean(column) for column in meanshape.T]
for k,v in data_pca.iteritems():
		data_pca[k] = (v+meanshape)-mean

meanshape = ((meanshape-mean)+[cropsize[0]/2,cropsize[1]/2])

imshape = (cropsize[0], cropsize[1], 3)
avim = np.zeros(imshape)
imlen = len(data_pca.keys())

# for each imaged
count = 0
for filename, values in data_pca.iteritems():
  # warp to meanshape
  im = imread("./cropped/"+filename)
  tform = PiecewiseAffineTransform()
  tform.estimate(meanshape, values+[cropsize[0]/2,cropsize[1]/2])
  # store in array
  outim = warp(im, tform, output_shape=cropsize)
  #imsave("./averageface/test.bmp", outim)
  avim += skimage.util.img_as_float(outim)
  count += 1
  print str(count)

avim /= imlen
avim *= 255  
avim = avim.astype(np.uint8)
imsave("./average.bmp", Image(avim))
# for all in array
  # average
  
# write out