import tarfile, shutil, os, requests

#MUCT database
files = {
	"muct-a-jpg-v1.tar.gz" : "http://muct.googlecode.com/files/muct-a-jpg-v1.tar.gz",
	"muct-b-jpg-v1.tar.gz" : "http://muct.googlecode.com/files/muct-b-jpg-v1.tar.gz",
	"muct-c-jpg-v1.tar.gz" : "http://muct.googlecode.com/files/muct-c-jpg-v1.tar.gz",
	"muct-e-jpg-v1.tar.gz" : "http://muct.googlecode.com/files/muct-e-jpg-v1.tar.gz",
	}

for fi, url in files.iteritems():
	# download	
	r = requests.get(url, stream=True)
	size = int(r.headers['Content-Length'].strip())
	bytes = 0
	f = open(fi, 'wb')
	print "Downloading: %s Bytes: %s" % (fi, size)
	for buf in r.iter_content(1024):
		if buf:
			f.write(buf)
			bytes += len(buf)
			status = r"%10d	 [%3.2f%%]" % (bytes, bytes * 100. / size)
			status = status + chr(8)*(len(status)+1)
			print status,
	f.close()
	
	# untar files
	print "Extracting files from tar archive"
	tar = tarfile.open(fi)
	tar.extractall()
	tar.close()

	# move to correct directory
	print "Moving files"
	for f in os.listdir("./jpg"):
		shutil.move(os.path.join("./jpg",f), "./images")

	# delete remaining files and folders
	os.remove(fi)
	shutil.rmtree("./jpg")
	
print "Done!"