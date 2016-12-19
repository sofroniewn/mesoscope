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
    elif metadata['volume'] and metadata['logFramesPerFile'] == metadata['framesPerSlice']:
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
