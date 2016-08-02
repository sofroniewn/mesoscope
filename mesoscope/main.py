import json
from numpy import array, concatenate, multiply
from thunder.images import fromtif
from os import mkdir, makedirs
from os.path import join, exists
from glob import glob
from .metadata import load as load_metadata
from .data import load as load_data
from .data import reshape

def load(path, engine=None):
    """
    Load mesoscope data.
    """
    metadata = load_metadata(path)
    data = load_data(path, nplanes=metadata['nplanes'], engine=engine)
    metadata['shape'] = data.shape
    return data, metadata

def convert(data, metadata):
    """
    Convert mesoscope data.
    """
    nchannels = metadata['nchannels']
    nrois = metadata['nrois']
    nlines = metadata['nlines']
    order = metadata['order']
    return data.map(lambda x : reshape(x, nrois, nlines, order))