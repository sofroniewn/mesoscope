import json
from numpy import ndarray, array, concatenate, multiply
from thunder.images import fromtif, fromarray
from os import mkdir, makedirs
from os.path import join, exists
from glob import glob
from .metadata import load as load_metadata
from .data import load as load_data
from .data import reshape, split, select
from .metadata import merge

def load(path, metapath=None, engine=None):
    """
    Load raw mesoscope data and metadata.

    Parameters
    ----------
    path : str
        Location with both metadata (.json) and image files (.tif).

    metapath : str
        Optional location with metadata (.json) if different from path.

    engine : multiple
        A computational backend for parallelization can be None (for local compute)
        or a SparkContext (for Spark).
    """
    if metapath == None:
        metapath = path
    metadata = load_metadata(metapath)

    if metadata['logFramesPerFile'] == 1:
        data = load_data(path, engine=engine)
    else:
        data = load_data(path, nplanes=metadata['nplanes'], engine=engine)
    metadata['shape'] = data.shape
    return data, metadata

def convert(data, metadata):
    """
    Convert raw mesoscope data by reshaping and merging rois.

    Parameters
    ----------
    data : numpy array or images
        Raw image data as a numpy array or thunder images object.

    metadata : dict
        Dictionary with metadata.
    """
    if isinstance(data, ndarray):
        data = fromarray(data)
    nchannels = metadata['nchannels']
    nrois = metadata['nrois']
    nlines = metadata['nlines']
    order = metadata['order']
    if metadata['merge']:
        newdata = data.map(lambda x : reshape(x, nrois, nlines, order))
    else:
        newdata = data.map(lambda x : split(x, nrois, nlines))
    newmetadata = merge(metadata)
    newmetadata['shape'] = newdata.shape
    return newdata, newmetadata

def reference(data, start=None, stop=None, algorithm='mean'):
    """
    Function for deteriminging reference image.

    Parameters
    ----------
    data : numpy array or images
        Raw image data as a numpy array or thunder images object.

    start, stop : nonnegative int, optional, default=None
        Indices of files to load, interpreted using Python slicing conventions.

    algorithm : algorithm used for calculating reference image
    """
    data = select(data,start,stop)
    if algorithm == 'mean':
        return data.mean().toarray()
    else:
        raise ValueError("Algorithm '%s' for generating reference not recognized" % algorithm)
