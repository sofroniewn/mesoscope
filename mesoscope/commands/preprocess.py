import os
import json
import click
from os import mkdir
from numpy import inf, percentile
from glob import glob
from shutil import rmtree, copy
from os.path import join, isdir, isfile, abspath
from thunder.images import fromtif, frombinary
from skimage.io import imsave
from .common import success, status, error, warn, setup_spark
from ..bidis import correct
from ..utils import detrend as detrend_func

@click.option('--overwrite', is_flag=True, help='Overwrite if directory already exists')
@click.option('--url', is_flag=False, nargs=1, help='URL of the master node of a Spark cluster')
@click.option('--amount', nargs=1, default=None, type=int, help='Int bidirectional shift')
@click.option('--bidi', is_flag=True, help='Flag for bidi conversion')
@click.option('--order', nargs=1, default=5, type=int, help='Int order for detrending')
@click.option('--detrend', is_flag=True, help='Flag for detrending')
@click.argument('output', nargs=1, metavar='<output directory>', required=False, default=None)
@click.argument('input', nargs=1, metavar='<input directory>', required=True)
@click.command('preprocess', short_help='preprocess images', options_metavar='<options>')
def preprocess_command(input, output, bidi, amount, detrend, order, url, overwrite):
    input = abspath(input)
    output = input + '_preprocessed' if output is None else abspath(output)
    if isdir(output) and not overwrite:
        error('directory already exists and overwrite is false')
        return
    elif isdir(output) and overwrite:
        rmtree(output)
        mkdir(output)

    engine = setup_spark(url)
    status('reading data from %s' % input)
    if len(glob(join(input, '*.tif'))) > 0:
        data = fromtif(input, engine=engine)
        ext = 'tif'
    elif len(glob(join(input, '*.tiff'))) > 0:
        data = fromtif(input, ext='tiff', engine=engine)
        ext = 'tif'
    elif len(glob(join(input, '*.bin'))) > 0:
        data = frombinary(input, engine=engine)
        ext = 'bin'
    else:
        error('no tif or binary files found in %s' % input)
        return

    if bidi:
        status('start bidi correction')
        if len(data.shape) > 4:
            error('Data length %d currently not supported' % len(data.shape))
        else:
            newdata, amount = correct(data, amount=amount)
            status('shifted %s pixels' % amount)
    else:
        newdata = data

    if detrend:
        status('start detrending')
        newdata = newdata.map_as_series(lambda x: detrend_func(x, order))


    if ext == 'tif':
        newdata.totif(output, overwrite=overwrite)
    elif ext == 'bin':
        newdata.tobinary(output, overwrite=overwrite)
    else:
        error('extenstion %s not recognized' % ext)

    metafiles = glob(join(input, 'meta*.json'))
    if len(metafiles) > 0:
        status('copying metadata')
        for f in metafiles:
            copy(f, output)

    success('preprocessing complete')
