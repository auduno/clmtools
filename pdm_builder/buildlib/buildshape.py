import numpy, math

from sklearn.decomposition import PCA
from sklearn.decomposition import SparsePCA
from sklearn.linear_model import ridge_regression
from numpy import row_stack, any, isnan, sum, diag, cov, mean, dot, trace
from numpy.linalg import qr

def pca(data, num_components=7):
		# creates a matrix with principal component analysis
		
		# build matrix with all data
		data = [d.flatten() for d in data if not any(isnan(d))]
		datamatrix = row_stack(data)
		
		# TODO: we should handle missing data better
		# how to handle occluded data?
		#		test out using https://github.com/sbailey/empca for handling missing data

		# do pca on matrix
		pca = PCA(n_components=num_components)
		pca.fit(datamatrix)
		
		#alternative way of calculating explained variance
		#		cdata = data - numpy.mean(data, axis=0)
		#		nuz = numpy.dot(pca.components_, cdata.T)
		#		cumulative_var = []
		#		for i in range(1,num_components+1):
		#			cumulative_var.append(numpy.trace(numpy.dot(nuz[0:i;].T, nuz[0:i,])))
		#		explained_var = [cumulative_var[0]]
		#		for i in range(1,num_components):
		#			explained_var.append(cumulative_var[i]-cumulative_var[i-1])
		
		# output decomposed matrix and variances
		eigenvalues = pca.explained_variance_
		
		return pca.components_, eigenvalues.tolist()

def spca(data, num_components=None, alpha=1):
		# creates a matrix with sparse principal component analysis
		# build matrix with all data
		data = [d.flatten() for d in data if not any(isnan(d))]
		datamatrix = row_stack(data)
		
		# center data
		cdata = datamatrix - mean(datamatrix, axis=0)
		
		if num_components is None:
			num_components = cdata.shape[0]
		
		# do spca on matrix
		spca = SparsePCA(n_components=num_components, alpha=alpha)
		spca.fit(cdata)
		
		# normalize components
		components = spca.components_.T
		for r in xrange(0,components.shape[1]):
			compnorm = numpy.apply_along_axis(numpy.linalg.norm, 0, components[:,r])
			if not compnorm == 0:
				components[:,r] /= compnorm
		components = components.T
		
		# calc adjusted explained variance from "Sparse Principal Component Analysis" by Zou, Hastie, Tibshirani
		spca.components_ = components
		#nuz = spca.transform(cdata).T
		nuz = ridge_regression(spca.components_.T, cdata.T, 0.01, solver='dense_cholesky').T
		
		#nuz = dot(components, cdata.T)
		q,r = qr(nuz.T)
		cumulative_var = []
		for i in range(1,num_components+1):
			cumulative_var.append(trace(r[0:i,]*r[0:i,]))
		explained_var = [math.sqrt(cumulative_var[0])]
		for i in range(1,num_components):
			explained_var.append(math.sqrt(cumulative_var[i])-math.sqrt(cumulative_var[i-1]))
		
		order = numpy.argsort(explained_var)[::-1]
		components = numpy.take(components,order,axis=0)
		evars = numpy.take(explained_var,order).tolist()
		#evars = numpy.take(explained_var,order)
		#order2 = [0,1,2,4,5,7,12,19]
		#components = numpy.take(components,order2,axis=0)
		#evars = numpy.take(evars,order2).tolist()
		
		return components, evars
