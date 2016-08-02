import os
import json
import click
from .. import load, convert

@click.command('convert', short_help='convert raw data into images', options_metavar='<options>')
def convert(path):
    data, metadata = load(path)
    converted = convert(data, metadata)
    print converted.shape