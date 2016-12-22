import os
import json
import click
from os import mkdir
from numpy import inf, percentile
from glob import glob
from shutil import rmtree
from os.path import join, isdir, isfile
from pandas import DataFrame
from thunder.images import fromtif, frombinary
from ..registrations import register
from .common import success, status, error, warn, setup_spark

@click.option('--overwrite', is_flag=True, help='Overwrite if directory already exists')
@click.option('--url', is_flag=False, nargs=1, help='URL of the master node of a Spark cluster')
@click.argument('output', nargs=1, metavar='<output directory>', required=False, default=None)
@click.argument('input', nargs=1, metavar='<input directory>', required=True)
@click.command('register', short_help='register input directory', options_metavar='<options>')
def register_command(input, output, overwrite, url):

    output = input + '_registered' if output is None else output

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

    status('registering')
    newdata, shifts = register(data)

    if ext == 'tif':
        newdata.totif(output, overwrite=overwrite)
    elif ext == 'bin':
        newdata.tobinary(output, overwrite=overwrite)
    else:
        error('extenstion %s not recognized' % ext)

    #shifts = DataFrame(shifts)
    #shifts.to_csv(join(output, 'shifts.csv'))


    success('registration complete')
