import os
import json
import click
from os import mkdir
from numpy import inf, percentile
from glob import glob
from shutil import rmtree, copy
from os.path import join, isdir, isfile
from pandas import DataFrame
from thunder.images import fromtif, frombinary
from ..registrations import register, register_blocks, register_blocks_piecewise
from .common import success, status, error, warn, setup_spark

@click.option('--overwrite', is_flag=True, help='Overwrite if directory already exists')
@click.option('--url', is_flag=False, nargs=1, help='URL of the master node of a Spark cluster')
@click.option('--method', nargs=1, default='normal', help='Registaion method')
@click.option('--size', nargs=1, default=32, type=int, help='Size of blocks')
@click.argument('output', nargs=1, metavar='<output directory>', required=False, default=None)
@click.argument('input', nargs=1, metavar='<input directory>', required=True)
@click.command('register', short_help='register input directory', options_metavar='<options>')
def register_command(input, output, overwrite, url, method, size):

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
    if method == 'normal':
        newdata, shifts = register(data)
    elif method == 'blocks':
        newdata = register_blocks(data, size=(size, size))
    elif method == 'piecewise':
        newdata = register_blocks_piecewise(data, size=(size, size))
    else:
        error('registration method %s not recognized' % method)


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

    #shifts = DataFrame(shifts)
    #shifts.to_csv(join(output, 'shifts.csv'))


    success('registration complete')
