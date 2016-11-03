import os
import json
import click
from os import mkdir
from numpy import inf
from glob import glob
from shutil import rmtree
from os.path import join, isdir, isfile
from thunder.images import fromtif, frombinary
from skimage.io import imsave

@click.option('--overwrite', is_flag=True, help='Overwrite if directory already exists')
@click.option('--localcorr', is_flag=True, help='Compute local correlation')
@click.option('--size', nargs=1, default=2, help='Int or tuple neighborhood for local correlation')
@click.argument('output', nargs=1, metavar='<output directory>', required=False, default=None)
@click.argument('input', nargs=1, metavar='<input directory>', required=True)
@click.command('summarize', short_help='create summary images', options_metavar='<options>')
def summarize_command(input, output, localcorr, size, overwrite):
    output = input + '_converted' if output is None else output
    status('reading data from %s' % input)
    if len(glob(join(input, '*.tif'))) > 0:
        data = fromtif(input)
    elif len(glob(join(input, '*.bin'))) > 0:
        data = frombinary(input)
    else:
        error('no tif or binary files found in %s' % input)
        return

    if not isdir(output):
        mkdir(output)

    if not isfile(join(output, 'mean.tif')) or overwrite:
        status('summarizing-mean')
        mean = data.mean().toarray()
        imsave(join(output, 'mean.tif'), mean.clip(0, inf).astype('uint16'), plugin='tifffile', photometric='minisblack')
    else:
        warn('mean.tif already exists and overwrite is false')

    if localcorr:
        if type(size) == tuple:
            name = 'localcorr-%s.tif' % ''.join(map(str,size))
        else:
            name = 'localcorr-%s.tif' % size
        if not isfile(join(output, name)) or overwrite:
            status('summarizing-localcorr')
            lc = data.localcorr(size)
            mean = data.mean().toarray()
            imsave(join(output, name), lc.astype('float32'), plugin='tifffile', photometric='minisblack')
        else:
            warn('%s already exists and overwrite is false' % name)

    success('summary complete')

def success(msg):
    click.echo('[' + click.style('success', fg='green') + '] ' + msg)

def status(msg):
    click.echo('[' + click.style('convert', fg='blue') + '] ' + msg)

def error(msg):
    click.echo('[' + click.style('error', fg='red') + '] ' + msg)

def warn(msg):
    click.echo('[' + click.style('warn', fg='yellow') + '] ' + msg)
