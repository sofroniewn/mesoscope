import os
import json
import click
from os import mkdir
from numpy import inf, percentile
from glob import glob
from shutil import rmtree
from os.path import join, isdir, isfile
from thunder.images import fromtif, frombinary
from skimage.io import imsave
from .common import success, status, error, warn

@click.option('--amount', nargs=1, default=None, type=int, help='Int bidirectional shift')
@click.argument('output', nargs=1, metavar='<output directory>', required=False, default=None)
@click.argument('input', nargs=1, metavar='<input directory>', required=True)
@click.command('bidi', short_help='bidirectionaly correct images', options_metavar='<options>')
def summarize_command(input, output, localcorr, mean, movie, ds, dt, size, overwrite):
    output = input + '_bidi' if output is None else output

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

    if not isdir(output):
        mkdir(output)

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

    success('bidi complete')
