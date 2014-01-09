clmtools
======

This is a collection of python tools for building models for [clmtrackr](http://github.com/auduno/clmtrackr/). This includes:
* Model builder / trainer
* Annotations for some images in the [MUCT](www.milbo.org/muct/) dataset
* An annotater for images
* Model viewer
* Emotion classification builder

Note the annotations included here and the ones used in clmtrackr are slightly modified from the ones included in the MUCT dataset. The difference is mainly in the region around the eyes and nose. 

The intention is to add annotations for more images over time.

### Downloading training data

Images from the MUCT database can be downloaded from https://code.google.com/p/muct/downloads/list by running:
```
python download_muct.py
```
The images will be placed in the folder *./data/images*.

### Training a model

To train a model, make sure you have *numpy*, *scipy*, *scikit-learn*, *scikit-image* and *PIL* installed. If you have *pip* installed, install them by running:

```
pip install numpy scipy scikit-learn scikit-image PIL
```

To train a model, run pdm_builder.py:
```
python pdm_builder.py
```
Model will be output as model.js. Some configuration settings for the model training can be set in *./buildlib/config.py*.

### Annotating your own images

Open *./annotater/main.html* with a browser. Load images to annotate by pushing "Choose Files" and select the image(s) you wish to annotate. The annotater will attempt to fit an annotation, but if it fails miserably, manually select the face by clicking "manually select face" and click and drag a box around the face. From the rough annotated face, modify the annotation by clicking and dragging the points.

Landmarks that are obstructed (by hair, clothes, etc.) should not be used for training the classifiers. To avoid this, hold down shift while clicking the points, so that the point turns red. This means that the point will be used only for creating the facial model, not the classifiers.

Note that annotations will be saved in html5 local storage, so you don't need to save the data between sessions. To write out the annotated data, click "save file". The browser will save a file called *annotations.csv* to the default download folder. Note that this file will include all annotations currently in the local storage.

To train a model from these annotated images, modify the variables *images* and *annotations*  in *./buildlib/config.py* to point to the folder containing your images and the csv file with annotations respectively.