# mirror scheme
mirror_map = [14,13,12,11,10,9,8,7,6,5,4,3,2,1,0,19,20,21,22,15,16,17,18,\
    28,29,30,31,32,23,24,25,26,27,33,40,39,38,37,36,35,34,41,43,42,50,49,\
    48,47,46,45,44,55,54,53,52,51,58,57,56,61,60,59,62,67,68,69,70,63,64,\
    65,66]

# path for drawing face
path = {\
   'normal' : [\
      [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14],\
      [15,16,17,18],\
      [19,20,21,22],\
      [23,63,24,64,25,65,26,66,23],\
      [28,67,29,68,30,69,31,70,28],\
      [34,35,36,42,37,43,38,39,40],\
      [33, 41, 62],\
      [44,45,46,47,48,49,50,51,52,53,54,55,44,56,57,58,50,59,60,61,44],\
      27,32\
   ]   \
}

# list of new positions of array 1
num_patches = 71

# wanted width of pdm
# a width of 100 will give ocular distance of approximately ?
#modelwidth = 400
modelwidth = 65
#modelwidth = 40

# wanted patchsize, must be odd
patch_size = 11
#patch_size = 16

# raw image folder
data_folder = "./data/"
images = "./data/images/"
annotations = "./data/annotations.csv"

# folder image
cropped_image_folder = "./data/cropped/"

input_image_width = 480