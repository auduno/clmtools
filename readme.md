clmtools
======

This is a collection of python tools for building models for [clmtrackr](http://github.com/auduno/clmtrackr/). This includes:
* Model builder / trainer
* Annotations for some images in the [MUCT](www.milbo.org/muct/) dataset
* Annotations for various images found online
* An annotater for new images
* Model viewer

Note the annotations included here and the ones used in clmtrackr are slightly different from the ones included in the MUCT dataset. The difference is mainly in the region around the eyes and nose.

### Downloading training data

Images from the MUCT database can be downloaded from https://code.google.com/p/muct/downloads/list by running:
```
python download_muct.py
```
The images will be placed in the folder *./data/images*.

A set of facial images found online can be downloaded by running:
```
python download_more.py
```
Please note that these images are not public domain, and this set of images should therefore not be shared or reproduced anywhere without prior consent from the copyright owners.

### Training a model

To train a model, make sure you have *numpy*, *scipy*, *scikit-learn*, *scikit-image* and *PIL* installed. If you have *pip* installed, install them by running:

```
pip install numpy scipy scikit-learn scikit-image PIL
```

To train a model, run pdm_builder.py:
```
python pdm_builder.py
```
Model will be output as *model.js*. Some configuration settings for the model training can be set in *./buildlib/config.py*.

### Annotating your own images

Open *./annotater/main.html* with a browser. Load images to annotate by pushing "Choose Files" and select the image(s) you wish to annotate. The annotater will attempt to fit an annotation, but if it fails miserably, manually select the face by clicking "manually select face" and click and drag a box around the face. From the rough annotated face, modify the annotation by clicking and dragging the points.

Points that are obstructed (by hair, clothes, etc.) should not be used for training the classifiers. To avoid this, hold down shift while clicking the points, so that the point turns red. This means that the point will be used only for creating the facial model, not the classifiers.

Note that annotations will automatically be saved in html5 local storage, so you don't need to save the data between sessions or images. To write out the annotated data, click "save file". The browser will save a file called *annotations.csv* to the default download folder. Note that this file will include all annotations currently in the local storage. 

*annotations.csv* is a semicolon-separated value file of the following format :
```
i000qa-fn.jpg;186;346;false;187;382;false;190;410;false;203;440;....
i000qb-fn.jpg;145;357;false;144;389;false;148;422;false;161;451;....
```
The first column is the name of the image file, followed by three fields for each point, where the first field is x-coordinate of the point, second field is the y-coordinate, and the third field is whether or whether not the point can be used in training classifiers.

To train a model from these annotated images, modify the variables *images* and *annotations*  in *./buildlib/config.py* to point to the folder containing your images and the csv file with annotations respectively.

The placement of the points used in the annotations for the models in clmtrackr look roughly like this:

![annotations](https://dl.dropboxusercontent.com/u/10557805/clmtools/annotations2b.jpg)

