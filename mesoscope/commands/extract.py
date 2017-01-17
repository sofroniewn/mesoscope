import click
from json import dumps
from os import mkdir
from os.path import join, isfile, isdir, dirname, splitext, basename, abspath
from glob import glob
from thunder.images import fromtif, frombinary
from extraction import load, NMF
from .common import success, status, error, warn, setup_spark
from ..models import overlay, filter_shape
from ..CC import CC

@click.option('--overwrite', is_flag=True, help='Overwrite if directory already exists')
@click.option('--url', is_flag=False, nargs=1, help='URL of the master node of a Spark cluster')
@click.option('--method', nargs=1, default='CC', help='Source extraction method')
@click.option('--diameter', nargs=1, default=10, type=float, help='Expected cell diameter')
@click.argument('output', nargs=1, metavar='<output directory>', required=False, default=None)
@click.argument('input', nargs=1, metavar='<input directory>', required=True)
@click.command('extract', short_help='performe source extraction', options_metavar='<options>')
def extract_command(input, output, diameter, method, url, overwrite):
    input = abspath(input)
    output = input + '_extracted' if output is None else abspath(output)

    if isfile(join(output, 'regions-' + method + '.json')) and not overwrite:
        error('file already exists and overwrite is false')
        return
    elif not isdir(output):
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
    if method == 'CC':
        algorithm = CC(diameter=diameter, clip_limit=0.04, theshold=0.2, sigma_blur=1, boundary=(1,1))
        unmerged = algorithm.fit(data)
        model = unmerged.merge(0.1)
        model = filter_shape(model, min_diameter = 0.7*diameter, max_diameter = 1.3*diameter, min_eccentricity = 0.2)
    elif method == 'NMF':
        algorithm = NMF(k=10, percentile=99, max_iter=50, overlap=0.1)
        unmerged = algorithm.fit(data, chunk_size=(50,50), padding=(25,25))
        model = unmerged.merge(overlap=0.20, max_iter=3, k_nearest=10)
    else:
        error('extraction method %s not recognized' % method)

    model.save(join(output, 'regions-' + method + '.json'))

    success('extraction complete')
