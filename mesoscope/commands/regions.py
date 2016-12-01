import os
import json
import click
from os import mkdir
from numpy import tile, maximum, full, nan, where, isnan, percentile
from glob import glob
from shutil import rmtree
from os.path import join, isfile, isdir, dirname, splitext, basename
from extraction import load
from extraction.model import ExtractionModel
from skimage.io import imsave, imread
from showit import image
from neurofinder import match, centers, shapes

@click.option('--overwrite', is_flag=True, help='Overwrite if directory already exists')
@click.option('--image', nargs=1, default=None, help='Path to base image')
@click.option('--compare', nargs=1, default=None, help='Path to regions for comparison')
@click.option('--threshold', nargs=1, default=5, type=float, help='Threshold for comparison')
@click.argument('output', nargs=1, metavar='<output directory>', required=False, default=None)
@click.argument('input', nargs=1, metavar='<input path>', required=True)
@click.command('regions', short_help='analyze regions', options_metavar='<options>')
def regions_command(input, output, image, compare, threshold, overwrite):
    status('reading data from %s' % input)
    model = load(input)

    output = dirname(input) if output is None else output
    if not isdir(output) and not output == '':
        mkdir(output)

    if image is not None:
        im = imread(image)
        clim = 3*percentile(im, 90)
        im = (im.astype(float)/clim).clip(0,1)
        size = im.shape
    else:
        size = (max([r.bbox[2] for r in model.regions])+1, max([r.bbox[3] for r in model.regions])+1)
        im = full(size, 0.0)


    if compare is not None:
        name = 'compare-%s-%s.json' % (basename(splitext(input)[0]), basename(splitext(compare)[0]))
        modelCompare = load(compare)
        matches = match(model.regions, modelCompare.regions, threshold)
        if not isfile(join(output, name)) or overwrite:
            status('comparing regions with data from %s' % compare)
            recall, precision = centers(model.regions, modelCompare.regions, threshold)
            inclusion, exclusion = shapes(model.regions, modelCompare.regions, threshold)
            results = {'recall':recall, 'precision':precision, 'inclusion':inclusion, 'exclusion':exclusion, 'threshold':threshold}
            with open(join(output, name), 'w') as f:
                f.write(json.dumps(results, indent=2))
        else:
            warn('%s already exists and overwrite is false' % name)
        matchesCompare = full(modelCompare.regions.count,nan)
        for ii in where(~isnan(matches))[0]:
            matchesCompare[matches[ii]] = ii

        if image is None:
            sizeCompare = (max([r.bbox[2] for r in modelCompare.regions])+1, max([r.bbox[3] for r in modelCompare.regions])+1)
            size = (maximum(size[0], sizeCompare[0]), maximum(size[1], sizeCompare[1]))
            im = full(size, 0.0)

        if any(~isnan(matches)):
            hits = ExtractionModel([model.regions[i] for i in where(~isnan(matches))[0]])
            h = hits.regions.mask(size, background='black', fill='green', stroke='white')
        else:
            h = full((size[0], size[1], 3), 0.0)
        if any(isnan(matches)):
            falseAlarms = ExtractionModel([model.regions[i] for i in where(isnan(matches))[0]])
            fA = falseAlarms.regions.mask(size, background='black', fill=[.7, 0, 0], stroke='white')
        else:
            fA = full((size[0], size[1], 3), 0.0)
        if any(~isnan(matchesCompare)):
            truePositives = ExtractionModel([modelCompare.regions[i] for i in where(~isnan(matchesCompare))[0]])
            tP = truePositives.regions.mask(size, background='black', fill='green', stroke='black')
        else:
            tP = full((size[0], size[1], 3), 0.0)
        if any(isnan(matchesCompare)):
            misses = ExtractionModel([modelCompare.regions[i] for i in where(isnan(matchesCompare))[0]])
            m = misses.regions.mask(size, background='black', fill='red', stroke='black')
        else:
            m = full((size[0], size[1], 3), 0.0)

        mask = maximum(maximum(maximum(h, fA), tP), m)
    else:
        mask = model.regions.mask(size, background='black', fill=[.7, 0, 0], stroke='white')

    if image is not None and compare is not None:
        name = '%s-%s-%s.tif' % (basename(splitext(image)[0]), basename(splitext(input)[0]), basename(splitext(compare)[0]))
    elif image is None and compare is not None:
        name = 'image-%s-%s.tif' % (basename(splitext(input)[0]), basename(splitext(compare)[0]))
    elif image is not None and compare is None:
        name = '%s-%s.tif' % (basename(splitext(image)[0]), basename(splitext(input)[0]))
    else:
        name = 'image-%s.tif' % basename(splitext(input)[0])

    if not isfile(join(output, name)) or overwrite:
        status('creating summary image')
        base = tile(im,(3,1,1)).transpose(1,2,0)
        blend = maximum(base, mask)
        imsave(join(output, name), (255*blend).astype('uint8'), plugin='tifffile', photometric='rgb')
    else:
        warn('%s already exists and overwrite is false' % name)

    success('regions complete')

def success(msg):
    click.echo('[' + click.style('success', fg='green') + '] ' + msg)

def status(msg):
    click.echo('[' + click.style('convert', fg='blue') + '] ' + msg)

def error(msg):
    click.echo('[' + click.style('error', fg='red') + '] ' + msg)

def warn(msg):
    click.echo('[' + click.style('warn', fg='yellow') + '] ' + msg)
