import click
from json import dumps
from os import mkdir
from os.path import join, isfile, isdir, dirname, splitext, basename
from skimage.io import imsave, imread
from showit import image
from extraction import load
from ..models import compare as compareModels
from ..models import overlay

@click.option('--overwrite', is_flag=True, help='Overwrite if directory already exists')
@click.option('--method', nargs=1, default='CC', help='Source extraction method')
@click.option('--diameter', nargs=1, default=10, type=float, help='Expected cell diameter')
@click.argument('output', nargs=1, metavar='<output directory>', required=False, default=None)
@click.argument('input', nargs=1, metavar='<input path>', required=True)
@click.command('extract', short_help='performe source extraction', options_metavar='<options>')
def extract_command(input, output, diameter, method, overwrite):
    status('reading data from %s' % input)


    success('extract complete')

def success(msg):
    click.echo('[' + click.style('success', fg='green') + '] ' + msg)

def status(msg):
    click.echo('[' + click.style('convert', fg='blue') + '] ' + msg)

def error(msg):
    click.echo('[' + click.style('error', fg='red') + '] ' + msg)

def warn(msg):
    click.echo('[' + click.style('warn', fg='yellow') + '] ' + msg)
