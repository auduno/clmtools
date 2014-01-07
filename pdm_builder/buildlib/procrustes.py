from numpy import sqrt, sum, dot, square, shape, mean, array
from numpy.linalg.linalg import svd
from numpy.linalg import inv
 
def procrustes(m1, m2):

    # centralize matrices
    mean_m1 = [mean(column) for column in m1.T]
    m1 = m1-mean_m1
    mean_m2 = [mean(column) for column in m2.T]
    m2 = m2-mean_m2
 
    # scaling
    scale_m1 = sqrt(sum(square(m1))/(m1.shape[1]))
    scale_m2 = sqrt(sum(square(m2))/(m2.shape[1]))
    m2 = (m2/scale_m2)*scale_m1
        
    # rotation
    u, s, v = svd(dot(m1.T, m2))
    r = dot(v.T, u.T)
    m2 = dot(m2, r)
    
    # set m2 center to m1 center
    m2 = m2+mean_m1
    
    return m2
 
def procrustes_distance(m1, m2):
    distance = sum(square(m1 - m2))
    
    return distance

def scale_width(m, width):
    # scale width model m to width
    
    # get width of model
    min_x_mean = min(m[:,0])
    max_x_mean = max(m[:,0])
    meanwidth = max_x_mean-min_x_mean
    
    # center model
    mean_m = [mean(column) for column in m.T]
    m -= mean_m
    
    # scale model
    m = (m/meanwidth)*width
    
    # uncenter model
    m += mean_m
    
    return m

def get_reverse_transforms(mat1, mat2):
    # get the reverse procrustes transformation to align m2 with m1
    
    m1 = array(mat1)
    m2 = array(mat2)
    
    # centralize matrices
    mean_m1 = [mean(column) for column in m1.T]
    m1 = m1-mean_m1
    mean_m2 = [mean(column) for column in m2.T]
    m2 = m2-mean_m2
    
    t = array(mean_m2)-array(mean_m1)
    
    # scaling
    scale_m1 = sqrt(sum(square(m1))/(m1.shape[1]))
    scale_m2 = sqrt(sum(square(m2))/(m2.shape[1]))
    m2 = (m2/scale_m2)*scale_m1
    
    sc = scale_m2/scale_m1
    
    # rotation
    u, s, v = svd(dot(m1.T, m2))
    r = inv(dot(v.T, u.T))
    
    return sc, r, mean_m1, mean_m2

def transform(mat, s, r, mean1, mean2):
    # transform matrix via transform t, scale s, rotation r
    
    m = array(mat)
    
    mean_m = [mean(column) for column in m.T]
    m -= mean_m
    # TODO : which mean should I subtract here?
    #m -= mean1
    m = dot(m, r)
    m *= s
    #m += t
    #m += mean_m
    m += mean2
    return m
