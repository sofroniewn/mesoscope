import os
import json
import click
from os import mkdir
from numpy import inf, percentile
from glob import glob
from shutil import rmtree, copy
from os.path import join, isdir, isfile
from thunder.images import fromtif, frombinary
from skimage.io import imsave
from .common import success, status, error, warn, setup_spark
from ..bidiCorrection import correct

@click.option('--overwrite', is_flag=True, help='Overwrite if directory already exists')
@click.option('--url', is_flag=False, nargs=1, help='URL of the master node of a Spark cluster')
@click.option('--amount', nargs=1, default=None, type=int, help='Int bidirectional shift')
@click.argument('output', nargs=1, metavar='<output directory>', required=False, default=None)
@click.argument('input', nargs=1, metavar='<input directory>', required=True)
@click.command('bidi', short_help='bidirectionaly correct images', options_metavar='<options>')
def bidi_command(input, output, amount, url, overwrite):
    output = input + '_bidi' if output is None else output
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

    status('starting bidi correction')
    if len(data.shape) > 4:
        error('Data length %d currently not supported' % len(data.shape))
    else:
        newdata, amount = correct(data, amount=amount)
        status('shifted %s pixels' % amount)

    if ext == 'tif':
        newdata.totif(output, overwrite=overwrite)
    elif ext == 'bin':
        newdata.tobinary(output, overwrite=overwrite)
    else:
        error('extenstion %s not recognized' % ext)

    metafiles = glob(join(input, '*.json'))
    if len(metafiles) > 0:
        status('copying metadata')
        for f in metafiles:
            copy(f, output)

    success('bidi complete')
