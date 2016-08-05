import json
from numpy import ndarray, array, concatenate, multiply
from thunder.images import fromtif, fromarray
from os import mkdir, makedirs
from os.path import join, exists
from glob import glob
from .metadata import load as load_metadata
from .data import load as load_data
from .data import reshape
from .metadata import merge

def load(path, engine=None):
    """
    Load raw mesoscope data and metadata.

    Parameters
    ----------
    path : str 
        Location with both metadata (.json) and image files (.tif).

    engine : multiple
        A computational backend for parallelization can be None (for local compute) 
        or a SparkContext (for Spark).
    """
    metadata = load_metadata(path)
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
    newdata = data.map(lambda x : reshape(x, nrois, nlines, order))
    newmetadata = merge(metadata)
    newmetadata['shape'] = newdata.shape
    return newdata, newmetadata