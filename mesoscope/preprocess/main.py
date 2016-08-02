import json
from numpy import array, concatenate, multiply, argsort
from thunder.images import fromtif
from os import mkdir, makedirs
from os.path import join, exists
from glob import glob
from . import metadata, images

def load(path, engine=None):
    metadata = metadata.load(join(path, '.json'))
    data = images.load(join(path, '.tif'), nplanes=meta['nplanes'], engine=engine)
    return data, metadata

def split(oim, nrois, nlines):
    ## Takes a single 2-dim plane and reshapes it according to nrois, nlines
    assert oim.ndim == 2
    
    if nrois > 1:
        ntotal = oim.shape[0]
        ngap = (ntotal - nlines*nrois)/(nrois-1)
        return array([oim[nlines*i + ngap*i: nlines*(i + 1) + ngap*i, :] for i in range(nrois)])
    else:
        return oim

########################################################################################################

def merge(oim, order):
    ## Takes a single 3-dim volume and merges along x dimension into a single plane
    if type(order) != bool:
        assert oim.ndim == 3
        assert len(order) == oim.shape[0]
        return oim[order].transpose((1, 0, 2)).reshape([oim.shape[1], -1])
    else:
        return oim

########################################################################################################

def reshape(oim, nrois, nlines, order):
    ## Takes a 2-dim plane / 3-dim volume and splits and merges
    if oim.ndim == 3:
        return array(map(lambda x : merge(split(x, nrois, nlines), order), oim))
    else:
        return merge(split(oim, nrois, nlines), order)