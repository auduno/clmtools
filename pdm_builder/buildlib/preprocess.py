import numpy, os
from numpy import vstack, mean
from PIL import Image
import ..config, procrustes

mirror_map = config.mirror_map
num_patches = config.num_patches
modelwidth = config.modelwidth
patch_size = config.patch_size
cropped_image_folder = config.cropped_image_folder
input_image_width = config.input_image_width

def preprocess(coordfiles, mirror=True, useNotVisiblePoints=True):
	# Preprocessing of images and coordinate input:
	#		-procrustes analysis
	#		-cropping and aligning of images
	#		-optional mirroring
	
	# read in coordinates
	coordinates = []
	filenames = []
	not_visible = []
	fi = open(coordfiles, "r")
	for lines in fi:
		#li = lines.split("\t")
		li = lines.strip().split(";")
		
		coor = []
		not_visible_coor = []
		filenames.append(li[0])
		#if li[0] == 'i033sb-fn.jpg':
		#	import pdb;pdb.set_trace()
		for r in xrange(0, num_patches):
			i = (r*3)+1
			#if li[i] == "0":
			#		visible_coor.append(True)
			#else:
			#		visible_coor.append(False)
			#coor.append(float(li[i+1]))
			#coor.append(float(li[i+2]))
			
			#if li[i+2] == "true":
			#		not_visible_coor.append(True)
			#else:
			#		not_visible_coor.append(False)
			
			if li[i+2] == "false":
				not_visible_coor.append(r)

			coor.append(float(li[i]))
			coor.append(float(li[i+1]))
		
		#coor = [float(x) for x in lines.strip().split(" ")]
		#coor = [numpy.nan if x == 0.0 else x for x in coor]
		single_coor = numpy.array(coor).reshape((num_patches,2))
		coordinates.append(single_coor)
		not_visible.append(not_visible_coor)
	fi.close()
	
	if mirror:
		# create mirror coordinates according to some map in config
		mirrors = []
		for c in range(0, len(coordinates)):
			# load image
			im = Image.open(config.data_folder+filenames[c], "r")
			# get imagesize
			imsize = im.size
			m = [coordinates[c][mirror_map[r]] for r in range(0, num_patches)]
			m = vstack(m)
			m[:,0] = (imsize[0]-1.0)-m[:,0]
			#m[:,0] = (imsize[0])-m[:,0]
			mirrors.append(m)
			not_visible_coor = [mirror_map[v] for v in not_visible[c]]
			not_visible.append(not_visible_coor)
		coordinates.extend(mirrors)
	
	# procrustes analysis of coordinates
	procrustes_distance = 1000.0
	# TODO: check that the first coordinate has all coordinates
	#meanshape = coordinates[0]
	meanshape = coordinates[5]
	while procrustes_distance > 20.0:
		aligned_coordinates = [[] for i in range(num_patches)]
		for c in coordinates:
			if useNotVisiblePoints:
				present_coord = [r for r in range(0, num_patches)]
			else:
				present_coord = [r for r in range(0, num_patches) if not numpy.isnan(coordinates[c][r,0]) and not numpy.isnan(coordinates[c][r,1])]
				# check that at least 50% of coordinates are present
				if len(present_coord) < num_patches/2:
					continue
			# only do procrustes analysis on present coordinates
			reduced_mean = meanshape[present_coord,:]
			reduced_coord = c[present_coord,:]
			# calculate aligned coordinates
			aligned = procrustes.procrustes(reduced_mean, reduced_coord)
			# add to aligned_coordinates
			for r in range(0,len(present_coord)):
				aligned_coordinates[present_coord[r]].append(aligned[r,:])
		# create new mean shape
		new_meanshape = numpy.zeros((num_patches,2))
		for r in range(0, num_patches):
			for ar in aligned_coordinates[r]:
				new_meanshape[r,:] += ar
			new_meanshape[r,:] /= len(aligned_coordinates[r])
		# calculate procrustes distance between old and new mean shape
		procrustes_distance = procrustes.procrustes_distance(meanshape, new_meanshape)
		# set old mean shape to new mean shape
		meanshape = new_meanshape
		print "procrustes distance in current iteration: "+str(procrustes_distance)
	
	# scale mean model to given modelwidth
	meanshape = procrustes.scale_width(meanshape, modelwidth)
	
	procrustes_transformations = []
	coordinates_final = []
	for c in range(0,len(coordinates)):
		if useNotVisiblePoints:
			present_coord = [r for r in range(0, num_patches)]
		else:
			present_coord = [r for r in range(0, num_patches) if not numpy.isnan(coordinates[c][r,0]) and not numpy.isnan(coordinates[c][r,1])]
			# check that at least 50% of coordinates are present
			if len(present_coord) < num_patches/2:
				continue
		# only do procrustes analysis on present coordinates
		reduced_mean = meanshape[present_coord,:]
		reduced_coord = coordinates[c][present_coord,:]
		# get procrustes transformation to mean
		c_transform = procrustes.procrustes(reduced_mean, reduced_coord)
		procrustes_transformations.append(c_transform)
		# transformed coordinates including nan
		c_final = numpy.array([numpy.nan for r in range(0,num_patches*2)]).reshape((num_patches,2))
		for r in range(0,len(present_coord)):
			c_final[present_coord[r],:] = c_transform[r,:]
		c_final = vstack(c_final)
		coordinates_final.append(c_final)
	
	# find how large to crop images
	mean_x = mean(meanshape[:,0])
	mean_y = mean(meanshape[:,1])
	min_x, max_x, min_y, max_y = float("inf"), -float("inf"), float("inf"), -float("inf")
	for c in procrustes_transformations:
		min_x = min(numpy.min(c[:,0]), min_x)
		max_x = max(numpy.max(c[:,0]), max_x)
		min_y = min(numpy.min(c[:,1]), min_y)
		max_y = max(numpy.max(c[:,1]), max_y)
	
	min_half_width = max(mean_x-min_x, max_x-mean_x) + ((patch_size-1)/2) + 2
	#min_half_width = max(mean_x-min_x, max_x-mean_x)
	min_half_height = max(mean_y-min_y, max_y-mean_y) + ((patch_size-1)/2) + 2
	#min_half_height = max(mean_y-min_y, max_y-mean_y)
	min_half_width = int(min_half_width)
	min_half_height = int(min_half_height)
	
	# get initial rectangle for cropping
	rect = numpy.array([mean_x-min_half_width, mean_y-min_half_height, \
		mean_x-min_half_width, mean_y+min_half_height,\
		mean_x+min_half_width, mean_y+min_half_height,\
		mean_x+min_half_width, mean_y-min_half_height]).reshape((4,2))
	
	# rotate and transform images same way as procrustes
	cropped_filenames = []
	fi = open(coordfiles, "r")
	i = 0
	for lines in fi:
		# load image
		filename = lines.split(";")[0]
		#filename = lines.split("\t")[0]
		im = Image.open(config.data_folder+filename, "r")
		if useNotVisiblePoints:
			present_coord = [r for r in range(0, num_patches)]
		else:
			# check which coordinates are present
			present_coord = [r for r in range(0, num_patches) if not numpy.isnan(coordinates[i][r,0]) and not numpy.isnan(coordinates[i][r,1])]
			# check that at least 50% of coordinates are present
			if len(present_coord) < num_patches/2:
				continue
		# only do procrustes analysis on present coordinates
		reduced_mean = meanshape[present_coord,:]
		reduced_coord = coordinates[i][present_coord,:]
		
		# get transformations
		crop_s, crop_r, crop_m1, crop_m2 = procrustes.get_reverse_transforms(reduced_mean, reduced_coord)
		# transform rect
		crop_rect = procrustes.transform(rect, crop_s, crop_r, crop_m1, crop_m2)

		# create a mask to detect when we crop outside the original image
		# create white image of same size as original
		mask = Image.new(mode='RGB', size=im.size, color=(255,255,255))
		# transform the same way as image
		mask = mask.transform((min_half_width*2, min_half_height*2), Image.QUAD, crop_rect.flatten(), Image.BILINEAR)
		# convert to boolean
		mask = mask.convert('L')
		mask.save(os.path.join(cropped_image_folder, os.path.splitext(filename)[0]+"_mask.bmp"))
		
		# use pil im.transform to crop and scale faces from images
		im = im.transform((min_half_width*2, min_half_height*2), Image.QUAD, crop_rect.flatten(), Image.BILINEAR)
		# save cropped images to output folder with text 
		im.save(os.path.join(cropped_image_folder, os.path.splitext(filename)[0]+".bmp"))
		cropped_filenames.append(os.path.splitext(filename)[0]+".bmp")
		i += 1
	fi.close()
	# if mirror is True: we need to mirror image
	if mirror:
		fi = open(coordfiles, "r")
		for lines in fi:
			#do the same stuff for mirrored images
			# load image
			#filename = lines.split("\t")[0]
			filename = lines.split(";")[0]
			im = Image.open(config.data_folder+filename, "r")
			
			if useNotVisiblePoints:
				present_coord = [r for r in range(0, num_patches)]
			else:
				# check which coordinates are present
				present_coord = [r for r in range(0, num_patches) if not numpy.isnan(coordinates[i][r,0]) and not numpy.isnan(coordinates[i][r,1])]
				# check that at least 50% of coordinates are present
				if len(present_coord) < num_patches/2:
					continue
			# only do procrustes analysis on present coordinates
			reduced_mean = meanshape[present_coord,:]
			reduced_coord = coordinates[i][present_coord,:]
			
			# get transformations
			crop_s, crop_r, crop_m1, crop_m2 = procrustes.get_reverse_transforms(reduced_mean, reduced_coord)
			# transform rect
			crop_rect = procrustes.transform(rect, crop_s, crop_r, crop_m1, crop_m2)

			# create a mask to detect when we crop outside the original image
			# create white image of same size as original
			mask = Image.new(mode='RGB', size=im.size, color=(255,255,255))
			# transform the same way as image
			mask = mask.transpose(Image.FLIP_LEFT_RIGHT)
			mask = mask.transform((min_half_width*2, min_half_height*2), Image.QUAD, crop_rect.flatten(), Image.BILINEAR)
			# convert to boolean
			mask = mask.convert('L')
			mask.save(os.path.join(cropped_image_folder, os.path.splitext(filename)[0]+"_m_mask.bmp"))

			# use pil im.transform to crop and scale faces from images
			im = im.transpose(Image.FLIP_LEFT_RIGHT)
			im = im.transform((min_half_width*2, min_half_height*2), Image.QUAD, crop_rect.flatten(), Image.BILINEAR)
			# save cropped images to output folder with text 
			im.save(os.path.join(cropped_image_folder, os.path.splitext(filename)[0]+"_m.bmp"))
			cropped_filenames.append(os.path.splitext(filename)[0]+"_m.bmp")
			i += 1
		fi.close()
	
	# output new coordinates
	new_coordinates = []
	#mean_meanshape = [mean(column) for column in meanshape.T]
	for c in coordinates_final:
		# mark coordinate files where the mark is occluded in some way
		new_coordinates.append(c - meanshape)
	
	#returns a dictionary where key is filename and value is coordinate matrix
	data_pca = {}
	for r in range(0, len(new_coordinates)):
		data_pca[cropped_filenames[r]] = new_coordinates[r]
			
	# TODO : create duplicate matrix
	data_patches = {}
	for r in range(0, len(new_coordinates)):
		#if cropped_filenames[r] == 'i033sb-fn.bmp':
		#	import pdb;pdb.set_trace()
		coord = numpy.copy(new_coordinates[r])
		if useNotVisiblePoints:
			# set not visible points to nan
			for vn in not_visible[r]:
				coord[vn,:] = numpy.nan
		data_patches[cropped_filenames[r]] = coord
	
	return data_pca, data_patches, meanshape, (min_half_width*2, min_half_height*2)
