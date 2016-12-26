import click
from json import dumps
from os import mkdir
from shutil import copy
from os.path import join, isfile, isdir, dirname, splitext, basename
from glob import glob
from thunder.images import fromtif, frombinary
from extraction import load
from ..traces import dff
from .common import success, status, error, warn, setup_spark

@click.option('--overwrite', is_flag=True, help='Overwrite if directory already exists')
@click.option('--url', is_flag=False, nargs=1, help='URL of the master node of a Spark cluster')
@click.option('--regions', nargs=1, default=None, help='Regions for traces')
@click.argument('output', nargs=1, metavar='<output directory>', required=False, default=None)
@click.argument('input', nargs=1, metavar='<input directory>', required=True)
@click.command('trace', short_help='extract traces from sources', options_metavar='<options>')
def trace_command(input, output, regions, url, overwrite):

    output = input + '_traces' if output is None else output

    if isdir(output) and not overwrite:
        error('directory already exists and overwrite is false')
        return
    elif isdir(output) and overwrite:
        rmtree(output)
        mkdir(output)

    model = load(regions)

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

    status('calculating traces')
    traces = dff(data, model)
    traces.tobinary(output, overwrite=overwrite)

    metafiles = glob(join(input, '*.json'))
    if len(metafiles) > 0:
        status('copying metadata')
        for f in metafiles:
            copy(f, output)

    success('traces complete')
