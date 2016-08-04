from numpy import array
from thunder.images import fromtif

def load(path, nplanes, engine=None):
    data = fromtif(path, nplanes=nplanes, engine=engine)
    return data

def split(oim, nrois, nlines):
    """
    Splits a single two dimensional plane.
    """
    if not oim.ndim == 2:
      raise Exception('original image must be two dimensional')
    
    if nrois > 1:
        ntotal = oim.shape[0]
        ngap = (ntotal - nlines*nrois)/(nrois-1)
        return array([oim[int(nlines*i + ngap*i): int(nlines*(i + 1) + ngap*i), :] for i in range(nrois)])
    else:
        return oim

def merge(oim, order):
    """
    Merges a three dimensional volume into a single plane.
    """
    if not type(order) == bool:
        if not oim.ndim == 3:
          raise Exception('original image must be three dimensional')
        if not len(order) == oim.shape[0]:
          raise Exception('length of order must match first image dimension')
        return oim[order].transpose((1, 0, 2)).reshape([oim.shape[1], -1])
    else:
        return oim

def reshape(oim, nrois, nlines, order):
    """
    Split and merge a two dimensional plane or three dimensional volume.
    """
    if oim.ndim == 3:
        return array(map(lambda x : merge(split(x, nrois, nlines), order), oim))
    else:
        return merge(split(oim, nrois, nlines), order)

def normalize(oim):
    """
    Normalize a three dimensional volume.
    """
    if not oim.ndim == 3:
        raise Exception('image must be three dimensional')
    means = oim.mean(axis=(1, 2), dtype='float32')
    maximum = means.max()
    return array([oim[i]*maximum/means[i] for i in range(oim.shape[0])])