import click
from json import dumps
from os import mkdir
from os.path import join, isfile, isdir, dirname, splitext, basename
from skimage.io import imsave, imread
from showit import image
from extraction import load
from .common import success, status, error, warn
from ..models import compare as compareModels
from ..models import overlay

@click.argument('input', nargs=1, metavar='<input directory>', required=True)
@click.argument('output', nargs=1, metavar='<output directory>', required=False, default=None)
@click.option('--overwrite', is_flag=True, help='Overwrite if directory already exists')
@click.option('--image', nargs=1, default=None, help='Path to base image')
@click.option('--compare', nargs=1, default=None, help='Path to regions for comparison')
@click.option('--threshold', nargs=1, default=5, type=float, help='Threshold for comparison')
@click.command('regions', short_help='analyze regions', options_metavar='<options>')
def regions_command(input, output, image, compare, threshold, overwrite):
    status('reading data from %s' % input)
    model = load(input)

    output = dirname(input) if output is None else output
    if not isdir(output) and not output == '':
        mkdir(output)

    if compare is not None:
        name = 'compare-%s-%s.json' % (basename(splitext(input)[0]), basename(splitext(compare)[0]))
        modelCompare = load(compare)
        if not isfile(join(output, name)) or overwrite:
            status('comparing %s and %s' % (basename(splitext(input)[0]), basename(splitext(compare)[0])))
            results = compareModels(model, modelCompare, threshold)
            with open(join(output, name), 'w') as f:
                f.write(dumps(results, indent=2))
            status(dumps(results, indent=2))
        else:
            warn('%s already exists and overwrite is false' % name)
    else:
        modelCompare = None

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
        if image is not None:
            image = imread(image)
        blend = overlay(model, image=image, compare=modelCompare, threshold=threshold)
        imsave(join(output, name), (255*blend).astype('uint8'), plugin='tifffile', photometric='rgb')
    else:
        warn('%s already exists and overwrite is false' % name)

    success('regions complete')
