clmtools
======

This is a collection of python tools for building face-models for [clmtrackr](http://github.com/auduno/clmtrackr/). This includes:
* Annotater for images
* Annotations for some images in the [MUCT](www.milbo.org/muct/) dataset
* Model builder / trainer
* Model viewer
* Emotion classification builder

Note the annotations included here and the ones used in clmtrackr are slightly modified from the ones included in the MUCT dataset. The difference is mainly in the region around the eyes and nose. 

The intention is to add annotations for more images than the MUCT dataset over time.

### Downloading training data

Images from the MUCT database can be downloaded from https://code.google.com/p/muct/downloads/list by running the script "download_muct.py". It will place the images in the folder "/data/images".

### Training a model

Run pdm_builder.py to train a model. Model will be output as model.js.

Note that pdm_builder depends on *numpy*, *scipy*, *scikit-learn*, *scikit-image* and *PIL*.

### Annotating your own images

Open *main.html* from your browser. Load images to annotate by pushing "Choose Files" and select the image(s) you wish to annotate. The annotater will attempt to fit an annotation, but if it fails miserably, manually select the face by clicking "manually select face" and clickind and dragging a box around the face. From the rough annotated face, modify the annotation by clicking and dragging the points.

Landmarks that are obstructed should not be used for training the response filters. To avoid this, hold down shift while clicking the points, so that the point turns red. This means that point will be used only for creating the facial model, not the response filters.

To save the annotated data, click "save file". The browser will save a file called "annotations.csv" to the default download folder.