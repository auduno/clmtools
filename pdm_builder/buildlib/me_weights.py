import os, config, string
# these weights will weigh up some images where the eyes and mouth are in particular poses
# so that the SVM patches will be more generically discriminate

eyeweights = []
fi = open(os.path.join(config.data_folder, "training_hints/", "eyes_wide_open.csv"),"r")
for lines in fi:
	ewf = lines.strip().split(".")[:-1]
	eyeweights.append(string.join(ewf,".")+".bmp")
	eyeweights.append(string.join(ewf,".")+"_m.bmp")
fi.close()
fi = open(os.path.join(config.data_folder, "training_hints/", "eyes_closed.csv"),"r")
for lines in fi:
	ewf = lines.strip().split(".")[:-1]
	eyeweights.append(string.join(ewf,".")+".bmp")
	eyeweights.append(string.join(ewf,".")+"_m.bmp")
fi.close()
weights = dict.fromkeys([23,24,25,26,27,28,29,30,31,32,63,64,65,66,67,68,69,70], eyeweights)

mouthweights = []
fi = open(os.path.join(config.data_folder, "training_hints/", "mouth.csv"),"r")
for lines in fi:
	ewf = lines.strip().split(".")[:-1]
	mouthweights.append(string.join(ewf,".")+".bmp")
	mouthweights.append(string.join(ewf,".")+"_m.bmp")
fi.close()
weights.update(dict.fromkeys([44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61], mouthweights))
