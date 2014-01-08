clmtools
======

This is a collection of tools for building face-models for [clmtrackr](http://github.com/auduno/clmtrackr/). This includes:
* Annotater for images
* Annotations for some images in the [MUCT](www.milbo.org/muct/) dataset
* Model builder / trainer
* Model viewer
* Emotion classification builder

Note the annotations included here and the ones used in clmtrackr are slightly modified from the ones included int the MUCT dataset. The intention is to add annotations for more images than the MUCT dataset over time.

Python dependencies for pdm_builder is:
* numpy
* scipy
* scikit-learn
* scikit-image
* PIL