import os
import json
import click
from os import mkdir
from numpy import inf
from glob import glob
from shutil import rmtree
from os.path import join, isdir, abspath
from .common import success, status, error, warn, setup_spark
from .. import load, convert

@click.argument('output', nargs=1, metavar='<output directory>', required=False, default=None)
@click.argument('input', nargs=1, metavar='<input directory>', required=True)
@click.option('--overwrite', is_flag=True, help='Overwrite if directory already exists')
@click.option('--url', is_flag=False, nargs=1, help='URL of the master node of a Spark cluster')
@click.option('--ext', nargs=1, default='tif')
@click.command('convert', short_help='process raw data by converting into images', options_metavar='<options>')
def convert_command(input, output, ext, url, overwrite):
    input = abspath(input)
    output = input + '_converted' if output is None else abspath(output)
    if isdir(output) and not overwrite:
        error('directory already exists and overwrite is false')
        return
    elif isdir(output) and overwrite:
        rmtree(output)
        mkdir(output)

    engine = setup_spark(url)
    status('reading data from %s' % input)
    if len(glob(join(input, '*.json'))) == 0:
        error('no json metadata found in %s' % input)
        return
    if len(glob(join(input, '*.tif'))) == 0 and len(glob(join(input, '*.tiff'))) == 0:
        error('no tif or tiff files found in %s' % input)
        return
    data, meta = load(input, input, engine=engine)
    status('converting')
    newdata, newmeta = convert(data, meta)

    status('writing data to %s' % output)
    if ext == 'tif':
        newdata.clip(0, inf).astype('uint16').totif(output, overwrite=overwrite)
    elif ext == 'bin':
        newdata.clip(0, inf).astype('uint16').tobinary(output, overwrite=overwrite)
    else:
        error('extenstion %s not recognized' % ext)

    with open(join(output, 'metadata.json'), 'w') as f:
      f.write(json.dumps(newmeta, indent=2))
    success('data written')
