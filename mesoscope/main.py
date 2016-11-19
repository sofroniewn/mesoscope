import json
from numpy import ndarray, array, concatenate, multiply
from thunder.images import fromtif, fromarray
from os import mkdir, makedirs
from os.path import join, exists
from glob import glob
from .metadata import load as load_metadata
from .data import load as load_data
from .data import reshape, split, smooth
from .metadata import merge
from registration import CrossCorr

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

def reference(data, algorithm='mean'):
    """
    Function for deterimining reference image.

    Parameters
    ----------
    data : numpy array or images
        Raw image data as a numpy array or thunder images object.

    algorithm : algorithm used for calculating reference image
    """

    if algorithm == 'mean':
        return data.mean().toarray()
    else:
        raise ValueError("Algorithm '%s' for generating reference not recognized" % algorithm)

def downsample(data, ds=None, dt=None):
    """
    Function for downsampling images in space and time.

    Parameters
    ----------
    data : numpy array or images
        Raw image data as a numpy array or thunder images object.

    ds : int or tuple that specifies downsampling in space

    dt : int that specifies downsampling in time
    """

    if not ds == None:
        data = data.median_filter(ds).subsample(ds)

    if not dt == None:
        data = data.map_as_series(lambda x: smooth(x, dt))

    return data

def register(data, ref):
    """
    Function for registering data using a referece image.

    Parameters
    ----------
    data : numpy array or images
        Raw image data as a numpy array or thunder images object.

    ref : numpy array or images
        Reference image as a numpy array or thunder images object.
    """

    if len(data.shape) == 4:
        algorithm = CrossCorr(axis=0)
    else:
        algorithm = CrossCorr()

    model = algorithm.fit(data, ref)
    registered = model.transform(data)
    shifts = model.toarray()

    return registered, shifts
