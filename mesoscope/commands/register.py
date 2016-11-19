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
from .. import register, reference

@click.option('--overwrite', is_flag=True, help='Overwrite if directory already exists')
@click.argument('output', nargs=1, metavar='<output directory>', required=False, default=None)
@click.argument('input', nargs=1, metavar='<input directory>', required=True)
@click.command('register', short_help='register input directory', options_metavar='<options>')
def register_command(input, output, overwrite):
    output = input + '_registered' if output is None else output
    if isdir(output) and not overwrite:
        error('directory already exists and overwrite is false')
        return
    elif isdir(output) and overwrite:
        rmtree(output)
        mkdir(output)

    status('reading data from %s' % input)
    if len(glob(join(input, '*.tif'))) > 0:
        data = fromtif(input)
        ext = 'tif'
    elif len(glob(join(input, '*.bin'))) > 0:
        data = frombinary(input)
        ext = 'bin'
    else:
        error('no tif or binary files found in %s' % input)
        return

    ref = reference(data, algorithm='mean')
    newdata, shifts = register(data, ref)

    if ext == 'tif':
        newdata.totif(output, overwrite=overwrite)
    elif ext == 'bin':
        newdata.tobinary(output, overwrite=overwrite)
    else:
        error('extenstion %s not recognized' % ext)

    shifts = DataFrame(shifts)
    shifts.to_csv(join(output, 'shifts.csv'))


    success('registration complete')

def success(msg):
    click.echo('[' + click.style('success', fg='green') + '] ' + msg)

def status(msg):
    click.echo('[' + click.style('convert', fg='blue') + '] ' + msg)

def error(msg):
    click.echo('[' + click.style('error', fg='red') + '] ' + msg)

def warn(msg):
    click.echo('[' + click.style('warn', fg='yellow') + '] ' + msg)
