import click
from json import dumps
from os import mkdir
from os.path import join, isfile, isdir, dirname, splitext, basename
from skimage.io import imsave, imread
from showit import image
from extraction import load
from .common import success, status, error, warn, setup_spark
from ..models import compare as compareModels
from ..models import overlay

@click.option('--overwrite', is_flag=True, help='Overwrite if directory already exists')
@click.option('--url', is_flag=False, nargs=1, help='URL of the master node of a Spark cluster')
@click.option('--method', nargs=1, default='CC', help='Source extraction method')
@click.option('--diameter', nargs=1, default=10, type=float, help='Expected cell diameter')
@click.argument('output', nargs=1, metavar='<output directory>', required=False, default=None)
@click.argument('input', nargs=1, metavar='<input directory>', required=True)
@click.command('extract', short_help='performe source extraction', options_metavar='<options>')
def extract_command(input, output, diameter, method, url, overwrite):

    output = input + '_extracted' if output is None else output

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

    status('extracting')
    # switch(method):
    #     case 'CC':
    #
    #     case 'NMF':
    #
    #     otherwise:
    #         error('extraction method %s not recognized' % method)


    success('extract complete')
