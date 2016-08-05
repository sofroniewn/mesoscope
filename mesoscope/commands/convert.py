import os
import json
import click
from os import mkdir
from numpy import inf
from glob import glob
from shutil import rmtree
from os.path import join, isdir
import skimage.external.tifffile as tifffile
from .. import load, convert

@click.option('--overwrite', is_flag=True, help='Overwrite if directory already exists')
@click.argument('output', nargs=1, metavar='<output directory>', required=False, default=None)
@click.argument('input', nargs=1, metavar='<input directory>', required=True)
@click.command('convert', short_help='process raw data by converting into images', options_metavar='<options>')
def convert_command(input, output, overwrite):
    output = input + '_converted' if output is None else output
    status('reading data from %s' % input)
    status('writing data to %s' % output)
    if isdir(output) and not overwrite:
        error('directory already exists and overwrite is false')
        return
    elif isdir(output) and overwrite:
        rmtree(output)
        mkdir(output)
    if len(glob(join(input, '*.json'))) == 0:
        error('no json metadata found in %s' % input)
        return
    if len(glob(join(input, '*.tif'))) == 0:
        error('no tif or tiff files found in %s' % input)
        return
    data, meta = load(input)
    newdata, newmeta = convert(data, meta)
    def write(kv):
        tifffile.imsave(join(output, 'image-%05g.tif' % kv[0]), kv[1])
    newdata.clip(0, inf).astype('uint16').foreach(write)
    with open(join(output, 'metadata.json'), 'w') as f:
      f.write(json.dumps(newmeta))
    success('data written')

def success(msg):
    click.echo('[' + click.style('success', fg='green') + '] ' + msg)

def status(msg):
    click.echo('[' + click.style('convert', fg='blue') + '] ' + msg)

def error(msg):
    click.echo('[' + click.style('error', fg='red') + '] ' + msg)
